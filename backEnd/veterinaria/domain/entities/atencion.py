"""
Entidad de dominio: Atención (entidad principal, tabla ATENCIONES).

Clase pura de Python: no importa nada de Django. Aquí viven los estados
permitidos y las transiciones, porque son conocimiento del negocio.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from veterinaria.domain.entities.detalle_atencion import DetalleAtencion

AGENDADA = "agendada"
REALIZADA = "realizada"
PAGADA = "pagada"
CANCELADA = "cancelada"

ESTADOS = (AGENDADA, REALIZADA, PAGADA, CANCELADA)
ESTADO_INICIAL = AGENDADA

# agendada → realizada → pagada · agendada → cancelada
TRANSICIONES = {
    AGENDADA: (REALIZADA, CANCELADA),
    REALIZADA: (PAGADA,),
    PAGADA: (),
    CANCELADA: (),
}


@dataclass
class Atencion:
    mascota_id: int
    fecha: datetime
    motivo: str
    estado: str = ESTADO_INICIAL
    total: Decimal = Decimal("0")
    id: int | None = None
    fecha_creacion: datetime | None = None
    detalles: list[DetalleAtencion] = field(default_factory=list)
    mascota_nombre: str | None = None  # solo lectura: nombre para mostrar

    def transiciones_permitidas(self) -> tuple[str, ...]:
        return TRANSICIONES.get(self.estado, ())

    def puede_cambiar_a(self, nuevo_estado: str) -> bool:
        return nuevo_estado in self.transiciones_permitidas()

    def es_eliminable(self) -> bool:
        # Solo se elimina en el estado inicial
        return self.estado == ESTADO_INICIAL

    def calcular_total(self) -> Decimal:
        # El total siempre sale del detalle (base de la regla R2)
        return sum((d.subtotal for d in self.detalles), Decimal("0"))
