"""
Puerto (contrato) del repositorio de detalle_atencion.

Las líneas se crean y eliminan junto con su atención (AtencionRepository),
por eso este puerto solo tiene consultas.
"""
from abc import ABC, abstractmethod

from veterinaria.domain.entities.detalle_atencion import DetalleAtencion


class DetalleAtencionRepository(ABC):

    @abstractmethod
    def listar_por_atencion(self, atencion_id: int) -> list[DetalleAtencion]:
        """Líneas de detalle de una atención."""

    @abstractmethod
    def existe_con_servicio(self, servicio_id: int) -> bool:
        """¿El servicio se usa en alguna atención? (borrado protegido de servicios)."""
