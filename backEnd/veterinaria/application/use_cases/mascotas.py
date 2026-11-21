"""
Casos de uso de mascotas (un caso de uso por operación).

Reglas: el dueño debe existir, nombre obligatorio y no repetido para el mismo
dueño, especie y sexo dentro de los valores permitidos, fecha de nacimiento
no futura, y R3 (borrado protegido: no se elimina una mascota que tiene
atenciones).

Solo dependen de los puertos (domain/ports), nunca del ORM ni de Oracle.
"""
from datetime import date

from veterinaria.application.exceptions import (
    DuenoNoEncontrado,
    EspecieInvalida,
    FechaNacimientoFutura,
    MascotaEnUso,
    MascotaNoEncontrada,
    MascotaNombreDuplicado,
    ReglaIncumplida,
    SexoInvalido,
)
from veterinaria.domain.entities.mascota import ESPECIES, SEXOS, Mascota
from veterinaria.domain.ports.atencion_repository import AtencionRepository
from veterinaria.domain.ports.dueno_repository import DuenoRepository
from veterinaria.domain.ports.mascota_repository import MascotaRepository


def _validar(nombre, especie, sexo, raza, fecha_nacimiento):
    """Valida y normaliza los datos de una mascota."""
    nombre = (nombre or "").strip()
    if not nombre:
        raise ReglaIncumplida("El nombre de la mascota es obligatorio.", campo="nombre")
    if len(nombre) > 60:
        raise ReglaIncumplida(
            "El nombre no puede superar 60 caracteres.", campo="nombre"
        )

    especie = (especie or "").strip().lower()
    if especie not in ESPECIES:
        raise EspecieInvalida(especie, ESPECIES)

    sexo = (sexo or "").strip().upper()
    if sexo not in SEXOS:
        raise SexoInvalido(sexo)

    raza = (raza or "").strip() or None
    if raza is not None and len(raza) > 60:
        raise ReglaIncumplida("La raza no puede superar 60 caracteres.", campo="raza")

    if fecha_nacimiento is not None and fecha_nacimiento > date.today():
        raise FechaNacimientoFutura(fecha_nacimiento)

    return nombre, especie, sexo, raza, fecha_nacimiento


class ListarMascotas:
    def __init__(self, repo: MascotaRepository):
        self.repo = repo

    def ejecutar(
        self,
        dueno_id: int | None = None,
        especie: str | None = None,
        texto: str | None = None,
    ) -> list[Mascota]:
        return self.repo.listar(dueno_id=dueno_id, especie=especie, texto=texto)


class ObtenerMascota:
    def __init__(self, repo: MascotaRepository):
        self.repo = repo

    def ejecutar(self, mascota_id: int) -> Mascota:
        mascota = self.repo.obtener(mascota_id)
        if mascota is None:
            raise MascotaNoEncontrada(mascota_id)
        return mascota


class CrearMascota:
    def __init__(self, repo: MascotaRepository, dueno_repo: DuenoRepository):
        self.repo = repo
        self.dueno_repo = dueno_repo

    def ejecutar(
        self, dueno_id, nombre, especie, sexo, raza=None, fecha_nacimiento=None
    ) -> Mascota:
        if self.dueno_repo.obtener(dueno_id) is None:
            raise DuenoNoEncontrado(dueno_id)
        nombre, especie, sexo, raza, fecha_nacimiento = _validar(
            nombre, especie, sexo, raza, fecha_nacimiento
        )
        if self.repo.obtener_por_dueno_y_nombre(dueno_id, nombre) is not None:
            raise MascotaNombreDuplicado(nombre)
        return self.repo.crear(
            Mascota(
                dueno_id=dueno_id,
                nombre=nombre,
                especie=especie,
                sexo=sexo,
                raza=raza,
                fecha_nacimiento=fecha_nacimiento,
            )
        )


class ActualizarMascota:
    def __init__(self, repo: MascotaRepository, dueno_repo: DuenoRepository):
        self.repo = repo
        self.dueno_repo = dueno_repo

    def ejecutar(
        self, mascota_id, dueno_id, nombre, especie, sexo, raza=None, fecha_nacimiento=None
    ) -> Mascota:
        if self.repo.obtener(mascota_id) is None:
            raise MascotaNoEncontrada(mascota_id)
        if self.dueno_repo.obtener(dueno_id) is None:
            raise DuenoNoEncontrado(dueno_id)
        nombre, especie, sexo, raza, fecha_nacimiento = _validar(
            nombre, especie, sexo, raza, fecha_nacimiento
        )

        # Duplicado solo si el nombre pertenece a OTRA mascota del mismo dueño
        otra = self.repo.obtener_por_dueno_y_nombre(dueno_id, nombre)
        if otra is not None and otra.id != mascota_id:
            raise MascotaNombreDuplicado(nombre)

        actualizada = self.repo.actualizar(
            Mascota(
                id=mascota_id,
                dueno_id=dueno_id,
                nombre=nombre,
                especie=especie,
                sexo=sexo,
                raza=raza,
                fecha_nacimiento=fecha_nacimiento,
            )
        )
        if actualizada is None:
            raise MascotaNoEncontrada(mascota_id)
        return actualizada


class EliminarMascota:
    def __init__(self, repo: MascotaRepository, atencion_repo: AtencionRepository):
        self.repo = repo
        self.atencion_repo = atencion_repo

    def ejecutar(self, mascota_id: int) -> None:
        if self.repo.obtener(mascota_id) is None:
            raise MascotaNoEncontrada(mascota_id)
        # R3, borrado protegido: usa existe_con_mascota() de Javier
        if self.atencion_repo.existe_con_mascota(mascota_id):
            raise MascotaEnUso(mascota_id)
        self.repo.eliminar(mascota_id)
