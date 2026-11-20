"""
Repositorio de atenciones sobre Oracle (implementa AtencionRepository).

Convierte modelos de Django en entidades de dominio: los casos de uso nunca
ven un modelo del ORM.
"""
from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from veterinaria.domain.entities.atencion import AGENDADA, Atencion
from veterinaria.domain.entities.detalle_atencion import DetalleAtencion
from veterinaria.domain.ports.atencion_repository import AtencionRepository
from veterinaria.infrastructure.models import AtencionModel, DetalleAtencionModel

DB = "negocio"  # alias de Oracle en settings.py


def _inicio_del_dia(dia: date) -> datetime:
    """00:00 de ese día en hora de Chile (Django lo pasa a UTC al consultar)."""
    return timezone.make_aware(datetime.combine(dia, time.min))


def detalle_a_entidad(m: DetalleAtencionModel) -> DetalleAtencion:
    return DetalleAtencion(
        atencion_id=m.atencion_id,
        servicio_id=m.servicio_id,
        cantidad=m.cantidad,
        precio_unitario=m.precio_unitario,
    )


def a_entidad(m: AtencionModel) -> Atencion:
    return Atencion(
        id=m.id,
        mascota_id=m.mascota_id,
        fecha=m.fecha,
        motivo=m.motivo,
        estado=m.estado,
        total=m.total,
        fecha_creacion=m.fecha_creacion,
        detalles=[detalle_a_entidad(d) for d in m.detalles.all()],
    )


class OracleAtencionRepository(AtencionRepository):

    def _base(self):
        return AtencionModel.objects.prefetch_related("detalles")

    def listar(self, estado=None, mascota_id=None, desde=None, hasta=None, texto=None):
        qs = self._base()
        if estado:
            qs = qs.filter(estado=estado)
        if mascota_id:
            qs = qs.filter(mascota_id=mascota_id)
        if desde:
            qs = qs.filter(fecha__gte=_inicio_del_dia(desde))
        if hasta:
            qs = qs.filter(fecha__lt=_inicio_del_dia(hasta + timedelta(days=1)))
        if texto:
            qs = qs.filter(Q(motivo__icontains=texto))
        return [a_entidad(m) for m in qs]

    def obtener(self, atencion_id):
        m = self._base().filter(id=atencion_id).first()
        return a_entidad(m) if m else None

    def crear(self, atencion):
        # Cabecera y líneas en UNA transacción: si falla una línea, no queda nada.
        with transaction.atomic(using=DB):
            m = AtencionModel.objects.create(
                mascota_id=atencion.mascota_id,
                fecha=atencion.fecha,
                motivo=atencion.motivo,
                estado=atencion.estado,
                total=atencion.total,
            )
            for d in atencion.detalles:
                DetalleAtencionModel.objects.create(
                    atencion=m,
                    servicio_id=d.servicio_id,
                    cantidad=d.cantidad,
                    precio_unitario=d.precio_unitario,
                )
        return self.obtener(m.id)

    def actualizar_estado(self, atencion_id, nuevo_estado):
        filas = AtencionModel.objects.filter(id=atencion_id).update(estado=nuevo_estado)
        return self.obtener(atencion_id) if filas else None

    def eliminar(self, atencion_id):
        with transaction.atomic(using=DB):
            DetalleAtencionModel.objects.filter(atencion_id=atencion_id).delete()
            filas = AtencionModel.objects.filter(id=atencion_id).delete()[0]
        return filas > 0

    def existe_agendada_mismo_dia(self, mascota_id, dia, excluir_id=None):
        qs = AtencionModel.objects.filter(
            mascota_id=mascota_id,
            estado=AGENDADA,
            fecha__gte=_inicio_del_dia(dia),
            fecha__lt=_inicio_del_dia(dia + timedelta(days=1)),
        )
        if excluir_id is not None:
            qs = qs.exclude(id=excluir_id)
        return qs.exists()

    def existe_con_mascota(self, mascota_id):
        return AtencionModel.objects.filter(mascota_id=mascota_id).exists()
