"""
Entidad de dominio: Dueño (tabla DUENOS).

Clase pura de Python: no importa nada de Django. Representa a la persona
responsable de una o más mascotas de la clínica.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Dueno:
    rut: str  # con puntos y guion: 12.345.678-5
    nombre: str
    telefono: str
    email: str
    comuna: str  # se usa como filtro en el listado
    id: int | None = None  # None hasta que el dueño se guarda
    fecha_registro: datetime | None = None  # la asigna Oracle (UTC)
