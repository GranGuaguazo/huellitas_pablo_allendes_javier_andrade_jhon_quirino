"""
Casos de uso de dueños (un caso de uso por operación).

Aquí viven las reglas: RUT válido (módulo 11) y único, email válido y único,
campos obligatorios, y R3 (borrado protegido: no se elimina un dueño que
tiene mascotas).

Solo dependen de los puertos (domain/ports), nunca del ORM ni de Oracle.
"""
import re

from veterinaria.application.exceptions import (
    DuenoEnUso,
    DuenoNoEncontrado,
    EmailDuplicado,
    EmailInvalido,
    ReglaIncumplida,
    RutDuplicado,
    RutInvalido,
)
from veterinaria.domain.entities.dueno import Dueno
from veterinaria.domain.ports.dueno_repository import DuenoRepository
from veterinaria.domain.ports.mascota_repository import MascotaRepository

FORMATO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalizar_rut(rut) -> str:
    """Valida el RUT con el módulo 11 y lo devuelve como 12.345.678-5."""
    limpio = re.sub(r"[.\-\s]", "", str(rut or "")).upper()
    if not re.fullmatch(r"\d{7,8}[\dK]", limpio):
        raise RutInvalido(str(rut or ""))

    cuerpo, dv = limpio[:-1], limpio[-1]
    suma, multiplicador = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - suma % 11
    esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)
    if dv != esperado:
        raise RutInvalido(str(rut))

    return f"{int(cuerpo):,}".replace(",", ".") + "-" + dv


def _texto_obligatorio(valor, campo: str, etiqueta: str, maximo: int) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ReglaIncumplida(f"{etiqueta} es obligatorio.", campo=campo)
    if len(valor) > maximo:
        raise ReglaIncumplida(
            f"{etiqueta} no puede superar {maximo} caracteres.", campo=campo
        )
    return valor


def _validar(rut, nombre, telefono, email, comuna):
    """Valida y normaliza los datos de un dueño. Devuelve la tupla normalizada."""
    rut = normalizar_rut(rut)
    nombre = _texto_obligatorio(nombre, "nombre", "El nombre", 100)
    telefono = _texto_obligatorio(telefono, "telefono", "El teléfono", 20)
    comuna = _texto_obligatorio(comuna, "comuna", "La comuna", 60)

    email = (email or "").strip().lower()
    if not FORMATO_EMAIL.match(email) or len(email) > 120:
        raise EmailInvalido(email)

    return rut, nombre, telefono, email, comuna


class ListarDuenos:
    def __init__(self, repo: DuenoRepository):
        self.repo = repo

    def ejecutar(self, texto: str | None = None, comuna: str | None = None) -> list[Dueno]:
        return self.repo.listar(texto=texto, comuna=comuna)


class ObtenerDueno:
    def __init__(self, repo: DuenoRepository):
        self.repo = repo

    def ejecutar(self, dueno_id: int) -> Dueno:
        dueno = self.repo.obtener(dueno_id)
        if dueno is None:
            raise DuenoNoEncontrado(dueno_id)
        return dueno


class CrearDueno:
    def __init__(self, repo: DuenoRepository):
        self.repo = repo

    def ejecutar(self, rut, nombre, telefono, email, comuna) -> Dueno:
        rut, nombre, telefono, email, comuna = _validar(
            rut, nombre, telefono, email, comuna
        )
        if self.repo.obtener_por_rut(rut) is not None:
            raise RutDuplicado(rut)
        if self.repo.obtener_por_email(email) is not None:
            raise EmailDuplicado(email)
        return self.repo.crear(
            Dueno(rut=rut, nombre=nombre, telefono=telefono, email=email, comuna=comuna)
        )


class ActualizarDueno:
    def __init__(self, repo: DuenoRepository):
        self.repo = repo

    def ejecutar(self, dueno_id, rut, nombre, telefono, email, comuna) -> Dueno:
        if self.repo.obtener(dueno_id) is None:
            raise DuenoNoEncontrado(dueno_id)
        rut, nombre, telefono, email, comuna = _validar(
            rut, nombre, telefono, email, comuna
        )

        # Duplicado solo si el RUT o el email pertenecen a OTRO dueño
        otro = self.repo.obtener_por_rut(rut)
        if otro is not None and otro.id != dueno_id:
            raise RutDuplicado(rut)
        otro = self.repo.obtener_por_email(email)
        if otro is not None and otro.id != dueno_id:
            raise EmailDuplicado(email)

        actualizado = self.repo.actualizar(
            Dueno(
                id=dueno_id,
                rut=rut,
                nombre=nombre,
                telefono=telefono,
                email=email,
                comuna=comuna,
            )
        )
        if actualizado is None:
            raise DuenoNoEncontrado(dueno_id)
        return actualizado


class EliminarDueno:
    def __init__(self, repo: DuenoRepository, mascota_repo: MascotaRepository):
        self.repo = repo
        self.mascota_repo = mascota_repo

    def ejecutar(self, dueno_id: int) -> None:
        if self.repo.obtener(dueno_id) is None:
            raise DuenoNoEncontrado(dueno_id)
        # R3, borrado protegido: un dueño con mascotas no se elimina
        if self.mascota_repo.existe_con_dueno(dueno_id):
            raise DuenoEnUso(dueno_id)
        self.repo.eliminar(dueno_id)
