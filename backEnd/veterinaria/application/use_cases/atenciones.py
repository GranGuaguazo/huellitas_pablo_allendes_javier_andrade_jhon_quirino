"""
Casos de uso de atenciones (un caso de uso por operación).

La atención es la entidad principal: no es un CRUD más.
  - Crear = la atención con TODAS sus líneas de detalle en una sola operación.
  - Actualizar = cambiar de estado, solo por las transiciones permitidas.
  - Eliminar = solo en el estado inicial ('agendada').

Reglas del problema que viven aquí:
  R1  Una mascota no puede tener dos atenciones 'agendada' el mismo día.
  R2  Solo se agregan servicios activos y el total se recalcula siempre
      desde el detalle (el precio unitario lo pone el catálogo, no el cliente).
  (R3, borrado protegido de dueños y mascotas, está en duenos.py y mascotas.py.)

Solo dependen de los puertos (domain/ports), nunca del ORM ni de Oracle.
"""
from datetime import date, datetime

from veterinaria.application.exceptions import (
    AtencionAgendadaMismoDia,
    AtencionNoEliminable,
    AtencionNoEncontrada,
    AtencionSinDetalle,
    DatoAtencionInvalido,
    EstadoAtencionDesconocido,
    MascotaNoEncontrada,
    ServicioInactivo,
    ServicioNoEncontrado,
    ServicioRepetidoEnAtencion,
    TransicionAtencionInvalida,
)
from veterinaria.domain.entities.atencion import AGENDADA, ESTADOS, Atencion
from veterinaria.domain.entities.detalle_atencion import DetalleAtencion
from veterinaria.domain.ports.atencion_repository import AtencionRepository
from veterinaria.domain.ports.mascota_repository import MascotaRepository
from veterinaria.domain.ports.servicio_repository import ServicioRepository

MOTIVO_MAX = 200  # VARCHAR2(200)
CANTIDAD_MAX = 99999  # NUMBER(5); ck_detatencion_cantidad exige > 0


class ListarAtenciones:
    def __init__(self, repo: AtencionRepository):
        self.repo = repo

    def ejecutar(
        self,
        estado: str | None = None,
        mascota_id: int | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        texto: str | None = None,
    ) -> list[Atencion]:
        return self.repo.listar(
            estado=estado, mascota_id=mascota_id, desde=desde, hasta=hasta, texto=texto
        )


class ObtenerAtencion:
    def __init__(self, repo: AtencionRepository):
        self.repo = repo

    def ejecutar(self, atencion_id: int) -> Atencion:
        atencion = self.repo.obtener(atencion_id)
        if atencion is None:
            raise AtencionNoEncontrada(atencion_id)
        return atencion


class CrearAtencion:
    """Crea la atención 'agendada' con sus líneas de detalle (R1 y R2)."""

    def __init__(
        self,
        repo: AtencionRepository,
        mascota_repo: MascotaRepository,
        servicio_repo: ServicioRepository,
    ):
        self.repo = repo
        self.mascota_repo = mascota_repo
        self.servicio_repo = servicio_repo

    def ejecutar(
        self,
        mascota_id: int,
        fecha: datetime,
        motivo: str,
        detalles: list[dict],
    ) -> Atencion:
        """`detalles` es una lista de {"servicio_id": int, "cantidad": int}.

        Si llega un "precio_unitario" se ignora: el precio sale del catálogo.
        """
        if self.mascota_repo.obtener(mascota_id) is None:
            raise MascotaNoEncontrada(mascota_id)

        if not isinstance(fecha, datetime):
            raise DatoAtencionInvalido("La fecha de la atención debe incluir día y hora.", campo="fecha")

        motivo = (motivo or "").strip()
        if not motivo:
            raise DatoAtencionInvalido("El motivo de la atención es obligatorio.", campo="motivo")
        if len(motivo) > MOTIVO_MAX:
            raise DatoAtencionInvalido(
                f"El motivo no puede superar {MOTIVO_MAX} caracteres.", campo="motivo"
            )

        lineas = self._armar_detalle(detalles)

        # R1: una sola atención agendada por mascota y día
        if self.repo.existe_agendada_mismo_dia(mascota_id, fecha):
            raise AtencionAgendadaMismoDia(mascota_id, fecha)

        atencion = Atencion(
            mascota_id=mascota_id,
            fecha=fecha,
            motivo=motivo,
            estado=AGENDADA,
            detalles=lineas,
        )
        # R2: el total nunca viene del cliente, se calcula desde el detalle
        atencion.total = atencion.calcular_total()
        return self.repo.crear(atencion)

    def _armar_detalle(self, detalles: list[dict]) -> list[DetalleAtencion]:
        if not detalles:
            raise AtencionSinDetalle()

        lineas: list[DetalleAtencion] = []
        vistos: set[int] = set()
        for linea in detalles:
            servicio_id = linea.get("servicio_id")
            cantidad = linea.get("cantidad", 1)

            if servicio_id in vistos:
                # Clave compuesta (atencion_id, servicio_id): se suma la cantidad
                raise ServicioRepetidoEnAtencion(servicio_id)
            vistos.add(servicio_id)

            if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not (
                1 <= cantidad <= CANTIDAD_MAX
            ):
                raise DatoAtencionInvalido(
                    f"La cantidad del servicio {servicio_id} debe ser un entero entre 1 y {CANTIDAD_MAX}.",
                    campo="detalles",
                )

            servicio = self.servicio_repo.obtener(servicio_id)
            if servicio is None:
                raise ServicioNoEncontrado(servicio_id)
            # R2: solo servicios activos
            if not servicio.activo:
                raise ServicioInactivo(servicio_id)

            lineas.append(
                DetalleAtencion(
                    servicio_id=servicio_id,
                    cantidad=cantidad,
                    precio_unitario=servicio.precio,  # precio vigente del catálogo
                    servicio_nombre=servicio.nombre,
                )
            )
        return lineas


class CambiarEstadoAtencion:
    """«Actualizar» la entidad principal = avanzar su estado.

    agendada → realizada → pagada · agendada → cancelada
    """

    def __init__(self, repo: AtencionRepository):
        self.repo = repo

    def ejecutar(self, atencion_id: int, nuevo_estado: str) -> Atencion:
        nuevo_estado = (nuevo_estado or "").strip().lower()
        if nuevo_estado not in ESTADOS:
            raise EstadoAtencionDesconocido(nuevo_estado, ESTADOS)

        atencion = self.repo.obtener(atencion_id)
        if atencion is None:
            raise AtencionNoEncontrada(atencion_id)

        if not atencion.puede_cambiar_a(nuevo_estado):
            raise TransicionAtencionInvalida(atencion.estado, nuevo_estado)

        # R2: el total se recalcula siempre desde el detalle al cambiar de estado
        actualizada = self.repo.actualizar_estado(
            atencion_id, nuevo_estado, total=atencion.calcular_total()
        )
        if actualizada is None:  # se eliminó entre la lectura y la escritura
            raise AtencionNoEncontrada(atencion_id)
        return actualizada


class EliminarAtencion:
    """Solo se elimina una atención en el estado inicial ('agendada')."""

    def __init__(self, repo: AtencionRepository):
        self.repo = repo

    def ejecutar(self, atencion_id: int) -> None:
        atencion = self.repo.obtener(atencion_id)
        if atencion is None:
            raise AtencionNoEncontrada(atencion_id)
        if not atencion.es_eliminable():
            raise AtencionNoEliminable(atencion.estado)
        self.repo.eliminar(atencion_id)
