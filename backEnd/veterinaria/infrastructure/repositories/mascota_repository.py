"""
Repositorio de mascotas sobre Oracle (implementa MascotaRepository).

Convierte modelos de Django en entidades de dominio: los casos de uso nunca
ven un modelo del ORM.
"""
from django.db.models import Q

from veterinaria.domain.entities.mascota import Mascota
from veterinaria.domain.ports.mascota_repository import MascotaRepository
from veterinaria.infrastructure.models import MascotaModel


def a_entidad(m: MascotaModel) -> Mascota:
    return Mascota(
        id=m.id,
        dueno_id=m.dueno_id,
        nombre=m.nombre,
        especie=m.especie,
        sexo=m.sexo,
        raza=m.raza,
        fecha_nacimiento=m.fecha_nacimiento,
    )


class OracleMascotaRepository(MascotaRepository):

    def listar(self, dueno_id=None, especie=None, texto=None):
        qs = MascotaModel.objects.all()  # ordenado por nombre (Meta.ordering)
        if dueno_id:
            qs = qs.filter(dueno_id=dueno_id)
        if especie:
            qs = qs.filter(especie=especie)
        if texto:
            qs = qs.filter(Q(nombre__icontains=texto) | Q(raza__icontains=texto))
        return [a_entidad(m) for m in qs]

    def obtener(self, mascota_id):
        m = MascotaModel.objects.filter(id=mascota_id).first()
        return a_entidad(m) if m else None

    def obtener_por_dueno_y_nombre(self, dueno_id, nombre):
        m = MascotaModel.objects.filter(dueno_id=dueno_id, nombre__iexact=nombre).first()
        return a_entidad(m) if m else None

    def crear(self, mascota):
        m = MascotaModel.objects.create(
            dueno_id=mascota.dueno_id,
            nombre=mascota.nombre,
            especie=mascota.especie,
            sexo=mascota.sexo,
            raza=mascota.raza,
            fecha_nacimiento=mascota.fecha_nacimiento,
        )
        return a_entidad(m)

    def actualizar(self, mascota):
        filas = MascotaModel.objects.filter(id=mascota.id).update(
            dueno_id=mascota.dueno_id,
            nombre=mascota.nombre,
            especie=mascota.especie,
            sexo=mascota.sexo,
            raza=mascota.raza,
            fecha_nacimiento=mascota.fecha_nacimiento,
        )
        return self.obtener(mascota.id) if filas else None

    def eliminar(self, mascota_id):
        filas = MascotaModel.objects.filter(id=mascota_id).delete()[0]
        return filas > 0

    def existe_con_dueno(self, dueno_id):
        return MascotaModel.objects.filter(dueno_id=dueno_id).exists()
