"""
Puerto (contrato) del repositorio de servicios.

El dominio y los casos de uso dependen de esta interfaz, nunca de Oracle ni
del ORM de Django. La implementación concreta está en infrastructure/.
"""
from abc import ABC, abstractmethod

from veterinaria.domain.entities.servicio import Servicio


class ServicioRepository(ABC):

    @abstractmethod
    def listar(
        self, texto: str | None = None, activo: bool | None = None
    ) -> list[Servicio]:
        """Servicios ordenados por nombre. Filtra por texto (código o nombre) y por activo."""

    @abstractmethod
    def obtener(self, servicio_id: int) -> Servicio | None:
        """El servicio, o None si no existe."""

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Servicio | None:
        """El servicio con ese código, o None (control de duplicados)."""

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Servicio | None:
        """El servicio con ese nombre, o None (control de duplicados)."""

    @abstractmethod
    def crear(self, servicio: Servicio) -> Servicio:
        """Guarda el servicio y lo devuelve con su id."""

    @abstractmethod
    def actualizar(self, servicio: Servicio) -> Servicio | None:
        """Actualiza el servicio. Devuelve None si no existe."""

    @abstractmethod
    def eliminar(self, servicio_id: int) -> bool:
        """Elimina el servicio. False si no existía."""