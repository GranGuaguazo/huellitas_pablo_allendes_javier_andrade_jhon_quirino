"""
Puerto (contrato) del repositorio de atenciones.

El dominio y los casos de uso dependen de esta interfaz, nunca de Oracle ni
del ORM de Django. La implementación concreta está en infrastructure/.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal

from veterinaria.domain.entities.atencion import Atencion


class AtencionRepository(ABC):

    @abstractmethod
    def listar(
        self,
        estado: str | None = None,
        mascota_id: int | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        texto: str | None = None,
    ) -> list[Atencion]:
        """Atenciones con su detalle, más recientes primero."""

    @abstractmethod
    def obtener(self, atencion_id: int) -> Atencion | None:
        """La atención con sus líneas de detalle, o None si no existe."""

    @abstractmethod
    def crear(self, atencion: Atencion) -> Atencion:
        """Guarda la atención y TODAS sus líneas en una sola transacción."""

    @abstractmethod
    def actualizar_estado(
        self, atencion_id: int, nuevo_estado: str, total: Decimal | None = None
    ) -> Atencion | None:
        """Cambia el estado (y el total, si se entrega). None si la atención no existe."""

    @abstractmethod
    def eliminar(self, atencion_id: int) -> bool:
        """Elimina la atención y su detalle. False si no existía."""

    # --- Consultas propias del problema ---

    @abstractmethod
    def existe_agendada_mismo_dia(
        self, mascota_id: int, fecha: datetime, excluir_id: int | None = None
    ) -> bool:
        """R1: ¿la mascota ya tiene una atención 'agendada' el mismo día que `fecha`?

        El «día» se cuenta en hora de Chile; esa conversión es de la
        infraestructura, por eso el caso de uso entrega la fecha completa.
        """

    @abstractmethod
    def existe_con_mascota(self, mascota_id: int) -> bool:
        """R3: ¿la mascota tiene atenciones? (borrado protegido de mascotas)."""
