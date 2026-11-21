"""
Puerto (contrato) del repositorio de dueños.

El dominio y los casos de uso dependen de esta interfaz, nunca de Oracle ni
del ORM de Django. La implementación concreta está en infrastructure/.
"""
from abc import ABC, abstractmethod

from veterinaria.domain.entities.dueno import Dueno


class DuenoRepository(ABC):

    @abstractmethod
    def listar(
        self, texto: str | None = None, comuna: str | None = None
    ) -> list[Dueno]:
        """Dueños ordenados por nombre. Filtra por texto (RUT, nombre o email) y por comuna."""

    @abstractmethod
    def obtener(self, dueno_id: int) -> Dueno | None:
        """El dueño, o None si no existe."""

    @abstractmethod
    def obtener_por_rut(self, rut: str) -> Dueno | None:
        """El dueño con ese RUT, o None (control de duplicados)."""

    @abstractmethod
    def obtener_por_email(self, email: str) -> Dueno | None:
        """El dueño con ese email, o None (control de duplicados)."""

    @abstractmethod
    def crear(self, dueno: Dueno) -> Dueno:
        """Guarda el dueño y lo devuelve con su id."""

    @abstractmethod
    def actualizar(self, dueno: Dueno) -> Dueno | None:
        """Actualiza el dueño. Devuelve None si no existe."""

    @abstractmethod
    def eliminar(self, dueno_id: int) -> bool:
        """Elimina el dueño. False si no existía."""
