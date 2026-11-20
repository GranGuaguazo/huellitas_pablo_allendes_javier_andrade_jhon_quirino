"""
Contenedor de dependencias.

Es el ÚNICO lugar donde se eligen los repositorios concretos (Oracle).
Las vistas piden aquí sus casos de uso ya armados. Para cambiar de base de
datos bastaría con cambiar las clases que se instancian en este archivo.
"""
from veterinaria.application.use_cases.atenciones import ListarAtenciones, ObtenerAtencion
from veterinaria.infrastructure.repositories.atencion_repository import OracleAtencionRepository
from veterinaria.infrastructure.repositories.detalle_atencion_repository import (
    OracleDetalleAtencionRepository,
)

# --- Repositorios ---------------------------------------------------------

atencion_repository = OracleAtencionRepository()
detalle_atencion_repository = OracleDetalleAtencionRepository()

# --- Casos de uso: atenciones (Javier) ------------------------------------

listar_atenciones = ListarAtenciones(atencion_repository)
obtener_atencion = ObtenerAtencion(atencion_repository)

# --- Casos de uso: dueños y mascotas (Pablo) ------------------------------

# --- Casos de uso: servicios (Jhon) ---------------------------------------
