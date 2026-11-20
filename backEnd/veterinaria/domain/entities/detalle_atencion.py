"""
Entidad de dominio: línea de detalle de una atención (tabla DETALLE_ATENCION).

La clave es compuesta (atencion_id, servicio_id): un servicio aparece una
sola vez por atención; si se aplica dos veces se aumenta la cantidad.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DetalleAtencion:
    servicio_id: int
    cantidad: int
    precio_unitario: Decimal
    atencion_id: int | None = None  # None hasta que la atención se guarda

    @property
    def subtotal(self) -> Decimal:
        # Mismo cálculo que la columna virtual de Oracle
        return Decimal(self.cantidad) * Decimal(self.precio_unitario)
