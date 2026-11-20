"""
Repositorio de servicios sobre Oracle (implementa ServicioRepository).

Convierte modelos de Django en entidades de dominio: los casos de uso nunca
ven un modelo del ORM.
"""
from django.db.models import Q

from veterinaria.domain.entities.servicio import Servicio
from veterinaria.domain.ports.servicio_repository import ServicioRepository
from veterinaria.infrastructure.models import ServicioModel


def a_entidad(m: ServicioModel) -> Servicio:
    return Servicio(
        id=m.id,
        codigo=m.codigo,
        nombre=m.nombre,
        descripcion=m.descripcion,
        precio=m.precio,
        activo=m.activo,
    )


class OracleServicioRepository(ServicioRepository):

    def listar(self, texto=None, activo=None):
        qs = ServicioModel.objects.all()  # ordenado por nombre (Meta.ordering)
        if activo is not None:
            qs = qs.filter(activo=activo)
        if texto:
            qs = qs.filter(Q(codigo__icontains=texto) | Q(nombre__icontains=texto))
        return [a_entidad(m) for m in qs]

    def obtener(self, servicio_id):
        m = ServicioModel.objects.filter(id=servicio_id).first()
        return a_entidad(m) if m else None

    def obtener_por_codigo(self, codigo):
        m = ServicioModel.objects.filter(codigo=codigo).first()
        return a_entidad(m) if m else None

    def obtener_por_nombre(self, nombre):
        m = ServicioModel.objects.filter(nombre=nombre).first()
        return a_entidad(m) if m else None

    def crear(self, servicio):
        m = ServicioModel.objects.create(
            codigo=servicio.codigo,
            nombre=servicio.nombre,
            descripcion=servicio.descripcion,
            precio=servicio.precio,
            activo=servicio.activo,
        )
        return a_entidad(m)

    def actualizar(self, servicio):
        filas = ServicioModel.objects.filter(id=servicio.id).update(
            codigo=servicio.codigo,
            nombre=servicio.nombre,
            descripcion=servicio.descripcion,
            precio=servicio.precio,
            activo=servicio.activo,
        )
        return self.obtener(servicio.id) if filas else None

    def eliminar(self, servicio_id):
        filas = ServicioModel.objects.filter(id=servicio_id).delete()[0]
        return filas > 0