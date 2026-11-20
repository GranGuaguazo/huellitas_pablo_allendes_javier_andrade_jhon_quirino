"""
Prueba el CRUD de servicios contra Oracle (evidencia de la semana 2).

Usa los casos de uso y el repositorio reales, dentro de UNA transacción que se
revierte al final: no deja datos de prueba en el esquema.

    python manage.py probar_servicios
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from veterinaria.application.exceptions import ErrorNegocio
from veterinaria.application.use_cases.servicios import (
    ActualizarServicio,
    CrearServicio,
    EliminarServicio,
    ListarServicios,
    ObtenerServicio,
)
from veterinaria.infrastructure.repositories.detalle_atencion_repository import (
    OracleDetalleAtencionRepository,
)
from veterinaria.infrastructure.repositories.servicio_repository import (
    OracleServicioRepository,
)

ALIAS = "negocio"


class _Revertir(Exception):
    """Sirve solo para forzar el ROLLBACK al terminar las pruebas."""


class Command(BaseCommand):
    help = "Prueba el CRUD de servicios contra Oracle (todo se revierte al final)."

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
        repo = OracleServicioRepository()
        detalle_repo = OracleDetalleAtencionRepository()
        crear = CrearServicio(repo)
        listar = ListarServicios(repo)
        obtener = ObtenerServicio(repo)
        actualizar = ActualizarServicio(repo)
        eliminar = EliminarServicio(repo, detalle_repo)

        self.stdout.write("Probando servicios contra Oracle (todo se revierte al final)")
        try:
            with transaction.atomic(using=ALIAS):
                self._ok(f"Listar: {len(listar.ejecutar())} servicios en la tabla")

                nuevo = crear.ejecutar(
                    "tst-99", " Servicio de prueba ", "9990.50", "Descripción larga", True
                )
                self._ok(f"Crear: id={nuevo.id} código={nuevo.codigo} precio={nuevo.precio}")

                leido = obtener.ejecutar(nuevo.id)
                self._ok(f"Obtener: {leido.nombre!r}, activo={leido.activo}")

                encontrados = listar.ejecutar(texto="tst")
                self._ok(f"Listar con texto 'tst': {[s.codigo for s in encontrados]}")

                actualizado = actualizar.ejecutar(
                    nuevo.id, "TST-99", "Servicio de prueba", 12000, "Cambiada", False
                )
                self._ok(
                    f"Actualizar: precio={actualizado.precio} activo={actualizado.activo}"
                )
                inactivos = listar.ejecutar(activo=False)
                self._ok(f"Listar inactivos: {[s.codigo for s in inactivos]}")

                self._esperar_error(
                    "Código duplicado", lambda: crear.ejecutar("TST-99", "Otro nombre", 1)
                )
                self._esperar_error(
                    "Nombre duplicado",
                    lambda: crear.ejecutar("TST-98", "Servicio de prueba", 1),
                )
                self._esperar_error(
                    "Código inválido", lambda: crear.ejecutar("abc", "Otro", 1)
                )
                self._esperar_error(
                    "Precio negativo", lambda: crear.ejecutar("TST-97", "Otro", -5)
                )
                self._esperar_error("No encontrado", lambda: obtener.ejecutar(999999))

                usado = repo.obtener_por_codigo("CON-01")  # de 02_datos_ejemplo.sql
                if usado is not None:
                    self._esperar_error(
                        "Borrado protegido (CON-01 está en atenciones)",
                        lambda: eliminar.ejecutar(usado.id),
                    )
                else:
                    self.stdout.write("  --  CON-01 no existe: se omite el borrado protegido")

                eliminar.ejecutar(nuevo.id)
                self._ok("Eliminar servicio libre: sin errores")

                raise _Revertir()
        except _Revertir:
            self.stdout.write("Listo: todo se revirtió, no quedaron datos de prueba.")