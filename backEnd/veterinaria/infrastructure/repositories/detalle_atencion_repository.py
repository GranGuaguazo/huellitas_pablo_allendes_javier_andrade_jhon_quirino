"""Repositorio de detalle_atencion sobre Oracle (implementa DetalleAtencionRepository)."""
from veterinaria.domain.ports.detalle_atencion_repository import DetalleAtencionRepository
from veterinaria.infrastructure.models import DetalleAtencionModel
from veterinaria.infrastructure.repositories.atencion_repository import detalle_a_entidad


class OracleDetalleAtencionRepository(DetalleAtencionRepository):

    def listar_por_atencion(self, atencion_id):
        qs = (
            DetalleAtencionModel.objects.filter(atencion_id=atencion_id)
            .select_related("servicio")
            .order_by("servicio_id")
        )
        return [detalle_a_entidad(m) for m in qs]

    def existe_con_servicio(self, servicio_id):
        return DetalleAtencionModel.objects.filter(servicio_id=servicio_id).exists()
