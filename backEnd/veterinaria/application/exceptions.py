"""
Excepciones de negocio de la clínica «Huellitas».

Los casos de uso lanzan estas excepciones; NO saben nada de HTTP. Solo los
adaptadores (api/) las traducen a códigos de estado:

    NoEncontrado        -> 404
    Duplicado           -> 409
    EnUso               -> 409
    ReglaIncumplida     -> 409
    TransicionInvalida  -> 409

Cada integrante agrega en su sección las excepciones de su entidad,
heredando de una de las cinco excepciones base.
"""


class ErrorNegocio(Exception):
    """Base de todos los errores de negocio."""

    def __init__(self, mensaje: str, campo: str | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo  # campo con error, cuando corresponde


class NoEncontrado(ErrorNegocio):
    """El registro pedido no existe."""


class Duplicado(ErrorNegocio):
    """Se repite un valor que debe ser único (RUT, código, nombre...)."""


class EnUso(ErrorNegocio):
    """No se puede borrar: otro registro lo usa (borrado protegido)."""


class ReglaIncumplida(ErrorNegocio):
    """Se incumple una regla de negocio (R1, R2, R3...)."""


class TransicionInvalida(ErrorNegocio):
    """El cambio de estado no está permitido."""


# ---------------------------------------------------------------------
# Atenciones y detalle_atencion (Javier)
# ---------------------------------------------------------------------

class AtencionNoEncontrada(NoEncontrado):
    def __init__(self, atencion_id: int):
        super().__init__(f"No existe la atención {atencion_id}.")


class AtencionAgendadaMismoDia(ReglaIncumplida):
    """R1: una mascota no puede tener dos atenciones agendadas el mismo día."""

    def __init__(self, mascota_id: int, dia):
        super().__init__(
            f"La mascota {mascota_id} ya tiene una atención agendada el {dia:%d-%m-%Y}.",
            campo="fecha",
        )


class ServicioInactivo(ReglaIncumplida):
    """R2: solo se agregan servicios activos al detalle."""

    def __init__(self, servicio_id: int):
        super().__init__(
            f"El servicio {servicio_id} está inactivo y no se puede agregar.",
            campo="detalles",
        )


class AtencionSinDetalle(ReglaIncumplida):
    def __init__(self):
        super().__init__("La atención debe tener al menos un servicio.", campo="detalles")


class ServicioRepetidoEnAtencion(Duplicado):
    """La clave compuesta impide repetir un servicio: se suma la cantidad."""

    def __init__(self, servicio_id: int):
        super().__init__(
            f"El servicio {servicio_id} está repetido en el detalle; aumente la cantidad.",
            campo="detalles",
        )


class TransicionAtencionInvalida(TransicionInvalida):
    def __init__(self, actual: str, nuevo: str):
        super().__init__(
            f"Una atención '{actual}' no puede pasar a '{nuevo}'.", campo="estado"
        )


class AtencionNoEliminable(ReglaIncumplida):
    def __init__(self, estado: str):
        super().__init__(
            f"Solo se elimina una atención 'agendada'; esta está '{estado}'.",
            campo="estado",
        )


# ---------------------------------------------------------------------
# Dueños y mascotas (Pablo)
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# Servicios (Jhon)
# ---------------------------------------------------------------------
