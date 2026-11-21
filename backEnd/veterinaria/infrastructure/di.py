"""""
Contenedor de dependencias.

Es el ÚNICO lugar donde se eligen los repositorios concretos (Oracle).
Las vistas piden aquí sus casos de uso ya armados. Para cambiar de base de
datos bastaría con cambiar las clases que se instancian en este archivo.
"""
from veterinaria.application.use_cases.atenciones import ListarAtenciones, ObtenerAtencion
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
from veterinaria.application.use_cases.servicios import (
    ActualizarServicio,
    CrearServicio,
    EliminarServicio,
    ListarServicios,
    ObtenerServicio,
)
from veterinaria.infrastructure.repositories.atencion_repository import OracleAtencionRepository
from veterinaria.infrastructure.repositories.detalle_atencion_repository import (
    OracleDetalleAtencionRepository,
)
from veterinaria.infrastructure.repositories.dueno_repository import OracleDuenoRepository
from veterinaria.infrastructure.repositories.mascota_repository import OracleMascotaRepository
from veterinaria.infrastructure.repositories.servicio_repository import OracleServicioRepository

# --- Repositorios ---------------------------------------------------------

atencion_repository = OracleAtencionRepository()
detalle_atencion_repository = OracleDetalleAtencionRepository()
servicio_repository = OracleServicioRepository()
dueno_repository = OracleDuenoRepository()
mascota_repository = OracleMascotaRepository()

# --- Casos de uso: atenciones (Javier) ------------------------------------

listar_atenciones = ListarAtenciones(atencion_repository)
obtener_atencion = ObtenerAtencion(atencion_repository)

# --- Casos de uso: dueños y mascotas (Pablo) ------------------------------

listar_duenos = ListarDuenos(dueno_repository)
obtener_dueno = ObtenerDueno(dueno_repository)
crear_dueno = CrearDueno(dueno_repository)
actualizar_dueno = ActualizarDueno(dueno_repository)
# R3: un dueño con mascotas no se elimina
eliminar_dueno = EliminarDueno(dueno_repository, mascota_repository)

listar_mascotas = ListarMascotas(mascota_repository)
obtener_mascota = ObtenerMascota(mascota_repository)
crear_mascota = CrearMascota(mascota_repository, dueno_repository)
actualizar_mascota = ActualizarMascota(mascota_repository, dueno_repository)
# R3: una mascota con atenciones no se elimina (existe_con_mascota() de Javier)
eliminar_mascota = EliminarMascota(mascota_repository, atencion_repository)

# --- Casos de uso: servicios (Jhon) ---------------------------------------

listar_servicios = ListarServicios(servicio_repository)
obtener_servicio = ObtenerServicio(servicio_repository)
crear_servicio = CrearServicio(servicio_repository)
actualizar_servicio = ActualizarServicio(servicio_repository)
# Borrado protegido: consulta si el servicio se usa en el detalle de atenciones
eliminar_servicio = EliminarServicio(servicio_repository, detalle_atencion_repository)