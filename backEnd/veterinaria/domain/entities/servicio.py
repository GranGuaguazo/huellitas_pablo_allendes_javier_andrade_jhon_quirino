"""
Entidad de dominio: Servicio (tabla SERVICIOS).

Clase pura de Python: no importa nada de Django. Representa un servicio del
catálogo de la clínica (consulta, vacuna, desparasitación...).
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Servicio:
    codigo: str  # formato AAA-00, por ejemplo VAC-01
    nombre: str
    precio: Decimal  # precio vigente en pesos, nunca negativo
    descripcion: str | None = None
    activo: bool = True  # False = suspendido; no se agrega a atenciones nuevas (R2)
    id: int | None = None  # None hasta que el servicio se guarda