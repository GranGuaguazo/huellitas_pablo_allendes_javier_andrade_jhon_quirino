# Un modelo por tabla. Se reexportan aquí para que veterinaria/models.py
# los registre en Django.
from veterinaria.infrastructure.models.atencion import AtencionModel
from veterinaria.infrastructure.models.detalle_atencion import DetalleAtencionModel
from veterinaria.infrastructure.models.servicio import ServicioModel

__all__ = ["AtencionModel", "DetalleAtencionModel", "ServicioModel"]