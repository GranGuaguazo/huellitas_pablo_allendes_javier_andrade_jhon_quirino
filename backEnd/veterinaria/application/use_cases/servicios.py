"""
Casos de uso de servicios (un caso de uso por operación).

Aquí viven las reglas del catálogo: formato del código (AAA-00), precio
mayor o igual a 0, código y nombre únicos, y borrado protegido (no se elimina
un servicio que ya se usó en una atención).

Solo dependen de los puertos (domain/ports), nunca del ORM ni de Oracle.
"""
import re
from decimal import Decimal, InvalidOperation

from veterinaria.application.exceptions import (
    CodigoServicioDuplicado,
    CodigoServicioInvalido,
    NombreServicioDuplicado,
    PrecioServicioInvalido,
    ReglaIncumplida,
    ServicioEnUso,
    ServicioNoEncontrado,
)
from veterinaria.domain.entities.servicio import Servicio
from veterinaria.domain.ports.detalle_atencion_repository import DetalleAtencionRepository
from veterinaria.domain.ports.servicio_repository import ServicioRepository

FORMATO_CODIGO = re.compile(r"^[A-Z]{3}-\d{2}$")


def _validar(codigo, nombre, precio):
    """Valida y normaliza los datos de un servicio. Devuelve (codigo, nombre, precio)."""
    codigo = (codigo or "").strip().upper()
    if not FORMATO_CODIGO.match(codigo):
        raise CodigoServicioInvalido(codigo)

    nombre = (nombre or "").strip()
    if not nombre:
        raise ReglaIncumplida("El nombre del servicio es obligatorio.", campo="nombre")

    try:
        precio = Decimal(str(precio))
    except InvalidOperation:
        raise PrecioServicioInvalido(precio)
    if not precio.is_finite() or precio < 0:
        raise PrecioServicioInvalido(precio)

    return codigo, nombre, precio


class ListarServicios:
    def __init__(self, repo: ServicioRepository):
        self.repo = repo

    def ejecutar(self, texto: str | None = None, activo: bool | None = None) -> list[Servicio]:
        return self.repo.listar(texto=texto, activo=activo)


class ObtenerServicio:
    def __init__(self, repo: ServicioRepository):
        self.repo = repo

    def ejecutar(self, servicio_id: int) -> Servicio:
        servicio = self.repo.obtener(servicio_id)
        if servicio is None:
            raise ServicioNoEncontrado(servicio_id)
        return servicio


class CrearServicio:
    def __init__(self, repo: ServicioRepository):
        self.repo = repo

    def ejecutar(self, codigo, nombre, precio, descripcion=None, activo=True) -> Servicio:
        codigo, nombre, precio = _validar(codigo, nombre, precio)
        if self.repo.obtener_por_codigo(codigo) is not None:
            raise CodigoServicioDuplicado(codigo)
        if self.repo.obtener_por_nombre(nombre) is not None:
            raise NombreServicioDuplicado(nombre)
        return self.repo.crear(
            Servicio(
                codigo=codigo,
                nombre=nombre,
                precio=precio,
                descripcion=descripcion,
                activo=activo,
            )
        )


class ActualizarServicio:
    def __init__(self, repo: ServicioRepository):
        self.repo = repo

    def ejecutar(
        self, servicio_id, codigo, nombre, precio, descripcion=None, activo=True
    ) -> Servicio:
        if self.repo.obtener(servicio_id) is None:
            raise ServicioNoEncontrado(servicio_id)
        codigo, nombre, precio = _validar(codigo, nombre, precio)

        # Duplicado solo si el código o el nombre pertenecen a OTRO servicio
        otro = self.repo.obtener_por_codigo(codigo)
        if otro is not None and otro.id != servicio_id:
            raise CodigoServicioDuplicado(codigo)
        otro = self.repo.obtener_por_nombre(nombre)
        if otro is not None and otro.id != servicio_id:
            raise NombreServicioDuplicado(nombre)

        actualizado = self.repo.actualizar(
            Servicio(
                id=servicio_id,
                codigo=codigo,
                nombre=nombre,
                precio=precio,
                descripcion=descripcion,
                activo=activo,
            )
        )
        if actualizado is None:
            raise ServicioNoEncontrado(servicio_id)
        return actualizado


class EliminarServicio:
    def __init__(
        self, repo: ServicioRepository, detalle_repo: DetalleAtencionRepository
    ):
        self.repo = repo
        self.detalle_repo = detalle_repo

    def ejecutar(self, servicio_id: int) -> None:
        if self.repo.obtener(servicio_id) is None:
            raise ServicioNoEncontrado(servicio_id)
        # Borrado protegido: si alguna atención lo usó, no se elimina
        if self.detalle_repo.existe_con_servicio(servicio_id):
            raise ServicioEnUso(servicio_id)
        self.repo.eliminar(servicio_id)