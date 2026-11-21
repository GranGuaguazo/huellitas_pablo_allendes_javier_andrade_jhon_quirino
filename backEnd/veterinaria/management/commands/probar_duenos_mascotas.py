"""
Prueba el CRUD de dueños y mascotas contra Oracle (evidencia de la semana 2).

Usa los casos de uso y los repositorios reales, dentro de UNA transacción que
se revierte al final: no deja datos de prueba en el esquema.

    python manage.py probar_duenos_mascotas
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from veterinaria.application.exceptions import ErrorNegocio
from veterinaria.application.use_cases.duenos import (
    ActualizarDueno,
    CrearDueno,
    EliminarDueno,
    ListarDuenos,
    ObtenerDueno,
)
from veterinaria.application.use_cases.mascotas import (
    ActualizarMascota,
    CrearMascota,
    EliminarMascota,
    ListarMascotas,
    ObtenerMascota,
)
from veterinaria.infrastructure.repositories.atencion_repository import (
    OracleAtencionRepository,
)
from veterinaria.infrastructure.repositories.dueno_repository import (
    OracleDuenoRepository,
)
from veterinaria.infrastructure.repositories.mascota_repository import (
    OracleMascotaRepository,
)

ALIAS = "negocio"


class _Revertir(Exception):
    """Sirve solo para forzar el ROLLBACK al terminar las pruebas."""


class Command(BaseCommand):
    help = "Prueba el CRUD de dueños y mascotas contra Oracle (todo se revierte al final)."

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
        dueno_repo = OracleDuenoRepository()
        mascota_repo = OracleMascotaRepository()
        atencion_repo = OracleAtencionRepository()

        crear_d = CrearDueno(dueno_repo)
        listar_d = ListarDuenos(dueno_repo)
        obtener_d = ObtenerDueno(dueno_repo)
        actualizar_d = ActualizarDueno(dueno_repo)
        eliminar_d = EliminarDueno(dueno_repo, mascota_repo)

        crear_m = CrearMascota(mascota_repo, dueno_repo)
        listar_m = ListarMascotas(mascota_repo)
        obtener_m = ObtenerMascota(mascota_repo)
        actualizar_m = ActualizarMascota(mascota_repo, dueno_repo)
        eliminar_m = EliminarMascota(mascota_repo, atencion_repo)

        self.stdout.write(
            "Probando dueños y mascotas contra Oracle (todo se revierte al final)"
        )
        try:
            with transaction.atomic(using=ALIAS):
                # ---------------- Dueños ----------------
                self.stdout.write("Dueños")
                self._ok(f"Listar: {len(listar_d.ejecutar())} dueños en la tabla")

                # RUT sin puntos y email en mayúsculas: se normalizan al guardar
                nuevo = crear_d.ejecutar(
                    "111111111", " Dueño de Prueba ", "+56 9 1111 1111",
                    " PRUEBA@Correo.cl ", "Renca",
                )
                self._ok(f"Crear: id={nuevo.id} rut={nuevo.rut} email={nuevo.email}")

                leido = obtener_d.ejecutar(nuevo.id)
                self._ok(f"Obtener: {leido.nombre!r}, comuna={leido.comuna}")

                self._ok(
                    "Listar con texto 'prueba': "
                    f"{[d.nombre for d in listar_d.ejecutar(texto='prueba')]}"
                )
                self._ok(
                    "Listar comuna 'Renca': "
                    f"{[d.nombre for d in listar_d.ejecutar(comuna='Renca')]}"
                )

                actualizado = actualizar_d.ejecutar(
                    nuevo.id, "11.111.111-1", "Dueño de Prueba",
                    "+56 9 2222 2222", "prueba@correo.cl", "Independencia",
                )
                self._ok(
                    f"Actualizar: comuna={actualizado.comuna} telefono={actualizado.telefono}"
                )

                self._esperar_error(
                    "RUT duplicado",
                    lambda: crear_d.ejecutar(
                        "11.111.111-1", "Otro", "+56 9 1", "otro@correo.cl", "Renca"
                    ),
                )
                self._esperar_error(
                    "Email duplicado",
                    lambda: crear_d.ejecutar(
                        "22.222.222-2", "Otro", "+56 9 1", "prueba@correo.cl", "Renca"
                    ),
                )
                self._esperar_error(
                    "RUT inválido",
                    lambda: crear_d.ejecutar(
                        "12.345.678-9", "Otro", "+56 9 1", "x@correo.cl", "Renca"
                    ),
                )
                self._esperar_error(
                    "Email inválido",
                    lambda: crear_d.ejecutar(
                        "22.222.222-2", "Otro", "+56 9 1", "sin-arroba", "Renca"
                    ),
                )
                self._esperar_error("Dueño no encontrado", lambda: obtener_d.ejecutar(999999))

                # ---------------- Mascotas ----------------
                self.stdout.write("Mascotas")
                self._ok(f"Listar: {len(listar_m.ejecutar())} mascotas en la tabla")

                firulais = crear_m.ejecutar(
                    nuevo.id, " Firulais ", "PERRO", "m", "Quiltro", date(2020, 5, 17)
                )
                self._ok(
                    f"Crear: id={firulais.id} dueno_id={firulais.dueno_id} "
                    f"{firulais.especie} sexo={firulais.sexo}"
                )

                leida = obtener_m.ejecutar(firulais.id)
                self._ok(f"Obtener: {leida.nombre!r}, nacimiento={leida.fecha_nacimiento}")

                self._ok(
                    "Listar mascotas del dueño: "
                    f"{[m.nombre for m in listar_m.ejecutar(dueno_id=nuevo.id)]}"
                )
                self._ok(
                    "Listar especie 'perro': "
                    f"{[m.nombre for m in listar_m.ejecutar(especie='perro')]}"
                )

                cambiada = actualizar_m.ejecutar(
                    firulais.id, nuevo.id, "Firulais", "perro", "M", "Mestizo", None
                )
                self._ok(
                    f"Actualizar: raza={cambiada.raza} nacimiento={cambiada.fecha_nacimiento}"
                )

                self._esperar_error(
                    "Nombre repetido para el mismo dueño",
                    lambda: crear_m.ejecutar(nuevo.id, "firulais", "gato", "H"),
                )
                self._esperar_error(
                    "Dueño inexistente",
                    lambda: crear_m.ejecutar(999999, "Fantasma", "perro", "M"),
                )
                self._esperar_error(
                    "Especie inválida",
                    lambda: crear_m.ejecutar(nuevo.id, "Nemo", "pez", "M"),
                )
                self._esperar_error(
                    "Sexo inválido",
                    lambda: crear_m.ejecutar(nuevo.id, "Nemo", "perro", "X"),
                )
                self._esperar_error(
                    "Fecha de nacimiento futura",
                    lambda: crear_m.ejecutar(
                        nuevo.id, "Futuro", "perro", "M", None,
                        date.today() + timedelta(days=1),
                    ),
                )
                self._esperar_error("Mascota no encontrada", lambda: obtener_m.ejecutar(999999))

                # ---------------- Regla R3 (borrado protegido) ----------------
                self.stdout.write("Regla R3 (borrado protegido)")
                self._esperar_error(
                    "Dueño con mascotas no se elimina",
                    lambda: eliminar_d.ejecutar(nuevo.id),
                )

                rocky = mascota_repo.obtener_por_dueno_y_nombre(
                    dueno_repo.obtener_por_rut("12.345.678-5").id, "Rocky"
                ) if dueno_repo.obtener_por_rut("12.345.678-5") else None
                if rocky is not None:  # de 02_datos_ejemplo.sql, tiene atenciones
                    self._esperar_error(
                        "Mascota con atenciones no se elimina (Rocky)",
                        lambda: eliminar_m.ejecutar(rocky.id),
                    )
                else:
                    self.stdout.write("  --  Rocky no existe: se omite este caso de R3")

                eliminar_m.ejecutar(firulais.id)
                self._ok("Eliminar mascota sin atenciones: sin errores")
                eliminar_d.ejecutar(nuevo.id)
                self._ok("Eliminar dueño sin mascotas: sin errores")

                raise _Revertir()
        except _Revertir:
            self.stdout.write("Listo: todo se revirtió, no quedaron datos de prueba.")
