"""
Entidad de dominio: Mascota (tabla MASCOTAS).

Clase pura de Python: no importa nada de Django. Aquí viven los valores
permitidos de especie y sexo, porque son conocimiento del negocio.
"""
from dataclasses import dataclass
from datetime import date

ESPECIES = ("perro", "gato", "ave", "conejo", "reptil", "otro")

MACHO = "M"
HEMBRA = "H"
SEXOS = (MACHO, HEMBRA)


@dataclass
class Mascota:
    dueno_id: int  # FK a DUENOS
    nombre: str  # no se repite para un mismo dueño
    especie: str  # una de ESPECIES
    sexo: str  # "M" o "H"
    raza: str | None = None  # opcional
    fecha_nacimiento: date | None = None  # opcional, no puede ser futura
    id: int | None = None  # None hasta que la mascota se guarda
