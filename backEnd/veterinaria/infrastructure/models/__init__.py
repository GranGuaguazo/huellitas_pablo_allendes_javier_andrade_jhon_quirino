# Un modelo por tabla. Se reexportan aquí para que veterinaria/models.py
# los registre en Django.
from veterinaria.infrastructure.models.atencion import AtencionModel
from veterinaria.infrastructure.models.detalle_atencion import DetalleAtencionModel

__all__ = ["AtencionModel", "DetalleAtencionModel"]
