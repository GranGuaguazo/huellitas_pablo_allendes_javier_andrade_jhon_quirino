"""
Repositorio de dueños sobre Oracle (implementa DuenoRepository).

Convierte modelos de Django en entidades de dominio: los casos de uso nunca
ven un modelo del ORM.
"""
from django.db.models import Q

from veterinaria.domain.entities.dueno import Dueno
from veterinaria.domain.ports.dueno_repository import DuenoRepository
from veterinaria.infrastructure.models import DuenoModel


def a_entidad(m: DuenoModel) -> Dueno:
    return Dueno(
        id=m.id,
        rut=m.rut,
        nombre=m.nombre,
        telefono=m.telefono,
        email=m.email,
        comuna=m.comuna,
        fecha_registro=m.fecha_registro,
    )


class OracleDuenoRepository(DuenoRepository):

    def listar(self, texto=None, comuna=None):
        qs = DuenoModel.objects.all()  # ordenado por nombre (Meta.ordering)
        if comuna:
            qs = qs.filter(comuna__iexact=comuna)
        if texto:
            qs = qs.filter(
                Q(rut__icontains=texto)
                | Q(nombre__icontains=texto)
                | Q(email__icontains=texto)
            )
        return [a_entidad(m) for m in qs]

    def obtener(self, dueno_id):
        m = DuenoModel.objects.filter(id=dueno_id).first()
        return a_entidad(m) if m else None

    def obtener_por_rut(self, rut):
        m = DuenoModel.objects.filter(rut=rut).first()
        return a_entidad(m) if m else None

    def obtener_por_email(self, email):
        m = DuenoModel.objects.filter(email__iexact=email).first()
        return a_entidad(m) if m else None

    def crear(self, dueno):
        m = DuenoModel.objects.create(
            rut=dueno.rut,
            nombre=dueno.nombre,
            telefono=dueno.telefono,
            email=dueno.email,
            comuna=dueno.comuna,
        )
        return a_entidad(m)

    def actualizar(self, dueno):
        filas = DuenoModel.objects.filter(id=dueno.id).update(
            rut=dueno.rut,
            nombre=dueno.nombre,
            telefono=dueno.telefono,
            email=dueno.email,
            comuna=dueno.comuna,
        )
        return self.obtener(dueno.id) if filas else None

    def eliminar(self, dueno_id):
        filas = DuenoModel.objects.filter(id=dueno_id).delete()[0]
        return filas > 0
