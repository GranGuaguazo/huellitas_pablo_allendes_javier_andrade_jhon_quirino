"""
Puerto (contrato) del repositorio de mascotas.

El dominio y los casos de uso dependen de esta interfaz, nunca de Oracle ni
del ORM de Django. La implementación concreta está en infrastructure/.
"""
from abc import ABC, abstractmethod

from veterinaria.domain.entities.mascota import Mascota


class MascotaRepository(ABC):

    @abstractmethod
    def listar(
        self,
        dueno_id: int | None = None,
        especie: str | None = None,
        texto: str | None = None,
    ) -> list[Mascota]:
        """Mascotas ordenadas por nombre. Filtra por dueño, especie y texto (nombre o raza)."""

    @abstractmethod
    def obtener(self, mascota_id: int) -> Mascota | None:
        """La mascota, o None si no existe."""

    @abstractmethod
    def obtener_por_dueno_y_nombre(self, dueno_id: int, nombre: str) -> Mascota | None:
        """La mascota de ese dueño con ese nombre, o None (control de duplicados)."""

    @abstractmethod
    def crear(self, mascota: Mascota) -> Mascota:
        """Guarda la mascota y la devuelve con su id."""

    @abstractmethod
    def actualizar(self, mascota: Mascota) -> Mascota | None:
        """Actualiza la mascota. Devuelve None si no existe."""

    @abstractmethod
    def eliminar(self, mascota_id: int) -> bool:
        """Elimina la mascota. False si no existía."""

    # --- Consulta propia del problema ---

    @abstractmethod
    def existe_con_dueno(self, dueno_id: int) -> bool:
        """R3: ¿el dueño tiene mascotas? (borrado protegido de dueños)."""
