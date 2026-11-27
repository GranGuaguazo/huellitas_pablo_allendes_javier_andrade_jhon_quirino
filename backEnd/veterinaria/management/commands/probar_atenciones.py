"""
Prueba la entidad principal (atenciones + detalle) contra Oracle (semana 3).

Usa los casos de uso y los repositorios reales, dentro de UNA transacción que
se revierte al final: no deja datos de prueba en el esquema. Demuestra cada
regla funcionando y fallando:

    R1  dos atenciones 'agendada' de la misma mascota el mismo día
    R2  servicio inactivo (ECO-01) y total recalculado desde el detalle
    Transiciones permitidas / no permitidas y borrado solo en 'agendada'

    python manage.py probar_atenciones
"""
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from veterinaria.application.exceptions import ErrorNegocio
from veterinaria.application.use_cases.atenciones import (
    CambiarEstadoAtencion,
    CrearAtencion,
    EliminarAtencion,
    ListarAtenciones,
    ObtenerAtencion,
)
from veterinaria.infrastructure.models import (
    AtencionModel,
    MascotaModel,
    ServicioModel,
)
from veterinaria.infrastructure.repositories.atencion_repository import (
    OracleAtencionRepository,
)
from veterinaria.infrastructure.repositories.mascota_repository import (
    OracleMascotaRepository,
)
from veterinaria.infrastructure.repositories.servicio_repository import (
    OracleServicioRepository,
)

ALIAS = "negocio"


class _Revertir(Exception):
    """Sirve solo para forzar el ROLLBACK al terminar las pruebas."""


class Command(BaseCommand):
    help = "Prueba atenciones (R1, R2, estados) contra Oracle (todo se revierte al final)."

    def _ok(self, texto):
        self.stdout.write(f"  OK  {texto}")

    def _esperar_error(self, texto, accion):
        """La acción DEBE lanzar un error de negocio; se muestra su mensaje."""
        try:
            accion()
        except ErrorNegocio as e:
            self._ok(f"{texto}: {type(e).__name__} -> {e}")
        else:
            raise AssertionError(f"{texto}: debía fallar y no falló")

    def handle(self, *args, **opciones):
        repo = OracleAtencionRepository()
        crear = CrearAtencion(repo, OracleMascotaRepository(), OracleServicioRepository())
        listar = ListarAtenciones(repo)
        obtener = ObtenerAtencion(repo)
        cambiar = CambiarEstadoAtencion(repo)
        eliminar = EliminarAtencion(repo)

        # Datos de 02_datos_ejemplo.sql
        rocky = MascotaModel.objects.get(nombre="Rocky").id
        mishi = MascotaModel.objects.get(nombre="Mishi").id
        consulta = ServicioModel.objects.get(codigo="CON-01")
        vacuna = ServicioModel.objects.get(codigo="VAC-01")
        eco = ServicioModel.objects.get(codigo="ECO-01")  # inactivo
        # 22:30 de Chile: en UTC ya es el día siguiente (prueba el «mismo día» de R1)
        manana = timezone.localdate() + timedelta(days=1)
        noche = timezone.make_aware(datetime.combine(manana, time(22, 30)))
        manana_9 = timezone.make_aware(datetime.combine(manana, time(9, 0)))

        self.stdout.write("Probando atenciones contra Oracle (todo se revierte al final)")
        try:
            with transaction.atomic(using=ALIAS):
                self._ok(f"Listar: {len(listar.ejecutar())} atenciones en la tabla")

                a = crear.ejecutar(
                    rocky,
                    noche,
                    "Control post vacuna",
                    [
                        {"servicio_id": consulta.id, "cantidad": 1},
                        # precio enviado por el cliente: se ignora (R2)
                        {"servicio_id": vacuna.id, "cantidad": 2, "precio_unitario": 1},
                    ],
                )
                esperado = consulta.precio + 2 * vacuna.precio
                self._ok(
                    f"Crear con 2 líneas: id={a.id} mascota={a.mascota_nombre} "
                    f"estado={a.estado} total={a.total} (esperado {esperado})"
                )
                assert a.total == esperado, "el total no coincide con el detalle"
                for d in a.detalles:
                    self._ok(
                        f"    línea {d.servicio_nombre}: {d.cantidad} × {d.precio_unitario}"
                        f" = {d.subtotal}"
                    )
                guardada = AtencionModel.objects.get(id=a.id)
                self._ok(
                    f"Oracle guardó fecha UTC {guardada.fecha:%Y-%m-%d %H:%M} "
                    f"(Chile: {timezone.localtime(guardada.fecha):%Y-%m-%d %H:%M})"
                )

                self._ok(f"Obtener: {obtener.ejecutar(a.id).motivo!r}")
                self._ok(
                    "Listar con texto 'rocky' y estado agendada: "
                    f"{[x.id for x in listar.ejecutar(estado='agendada', texto='rocky')]}"
                )

                # R1
                self._esperar_error(
                    "R1 misma mascota, mismo día (09:00 vs 22:30)",
                    lambda: crear.ejecutar(
                        rocky, manana_9, "Otra", [{"servicio_id": consulta.id, "cantidad": 1}]
                    ),
                )
                otra = crear.ejecutar(
                    mishi, manana_9, "Vacuna anual", [{"servicio_id": vacuna.id, "cantidad": 1}]
                )
                self._ok(f"R1 otra mascota el mismo día sí se permite: id={otra.id}")

                # R2
                self._esperar_error(
                    "R2 servicio inactivo (ECO-01)",
                    lambda: crear.ejecutar(
                        mishi,
                        manana_9 + timedelta(days=3),
                        "Ecografía",
                        [{"servicio_id": eco.id, "cantidad": 1}],
                    ),
                )
                self._esperar_error(
                    "Sin detalle",
                    lambda: crear.ejecutar(mishi, manana_9 + timedelta(days=3), "Nada", []),
                )
                self._esperar_error(
                    "Servicio repetido",
                    lambda: crear.ejecutar(
                        mishi,
                        manana_9 + timedelta(days=3),
                        "Doble",
                        [
                            {"servicio_id": consulta.id, "cantidad": 1},
                            {"servicio_id": consulta.id, "cantidad": 1},
                        ],
                    ),
                )
                self._esperar_error(
                    "Mascota inexistente",
                    lambda: crear.ejecutar(
                        999999, manana_9, "X", [{"servicio_id": consulta.id, "cantidad": 1}]
                    ),
                )

                # Transiciones
                self._esperar_error(
                    "Transición agendada → pagada", lambda: cambiar.ejecutar(a.id, "pagada")
                )
                self._ok(f"agendada → realizada: {cambiar.ejecutar(a.id, 'realizada').estado}")
                self._esperar_error(
                    "Eliminar una atención realizada", lambda: eliminar.ejecutar(a.id)
                )
                self._esperar_error(
                    "Transición realizada → cancelada",
                    lambda: cambiar.ejecutar(a.id, "cancelada"),
                )
                pagada = cambiar.ejecutar(a.id, "pagada")
                self._ok(f"realizada → pagada: {pagada.estado}, total={pagada.total}")

                self._ok(f"agendada → cancelada: {cambiar.ejecutar(otra.id, 'cancelada').estado}")
                nueva = crear.ejecutar(
                    mishi, manana_9, "Reagendada", [{"servicio_id": vacuna.id, "cantidad": 1}]
                )
                self._ok(f"R1 una cancelada no bloquea el día: id={nueva.id}")

                eliminar.ejecutar(nueva.id)
                self._esperar_error("Obtener eliminada", lambda: obtener.ejecutar(nueva.id))
                self._ok("Eliminar agendada (y su detalle por ON DELETE CASCADE)")
                self._esperar_error("Atención inexistente", lambda: obtener.ejecutar(999999))

                raise _Revertir
        except _Revertir:
            pass

        self.stdout.write(self.style.SUCCESS("Todas las pruebas OK. Cambios revertidos."))
