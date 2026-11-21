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


class DuenoNoEncontrado(NoEncontrado):
    def __init__(self, dueno_id: int):
        super().__init__(f"No existe el dueño {dueno_id}.")


class RutDuplicado(Duplicado):
    """Ya existe otro dueño con ese RUT (uq_duenos_rut)."""

    def __init__(self, rut: str):
        super().__init__(f"Ya existe un dueño con el RUT '{rut}'.", campo="rut")


class EmailDuplicado(Duplicado):
    """Ya existe otro dueño con ese email (uq_duenos_email)."""

    def __init__(self, email: str):
        super().__init__(f"Ya existe un dueño con el email '{email}'.", campo="email")


class RutInvalido(ReglaIncumplida):
    """El RUT no tiene formato válido o su dígito verificador no cuadra."""

    def __init__(self, rut: str):
        super().__init__(
            f"El RUT '{rut}' no es válido; use el formato 12.345.678-5.", campo="rut"
        )


class EmailInvalido(ReglaIncumplida):
    """El email no tiene formato válido (ck_duenos_email exige una @)."""

    def __init__(self, email: str):
        super().__init__(f"El email '{email}' no es válido.", campo="email")


class DuenoEnUso(EnUso):
    """R3: borrado protegido. El dueño tiene mascotas registradas."""

    def __init__(self, dueno_id: int):
        super().__init__(
            f"No se puede eliminar el dueño {dueno_id}: tiene mascotas registradas. "
            "Elimine o traspase sus mascotas primero."
        )


class MascotaNoEncontrada(NoEncontrado):
    def __init__(self, mascota_id: int):
        super().__init__(f"No existe la mascota {mascota_id}.")


class MascotaNombreDuplicado(Duplicado):
    """El dueño ya tiene una mascota con ese nombre (regla del caso de uso)."""

    def __init__(self, nombre: str):
        super().__init__(
            f"Este dueño ya tiene una mascota llamada '{nombre}'.", campo="nombre"
        )


class MascotaEnUso(EnUso):
    """R3: borrado protegido. La mascota tiene atenciones registradas."""

    def __init__(self, mascota_id: int):
        super().__init__(
            f"No se puede eliminar la mascota {mascota_id}: tiene atenciones registradas."
        )


class EspecieInvalida(ReglaIncumplida):
    """La especie no está en la lista (ck_mascotas_especie)."""

    def __init__(self, especie: str, permitidas: tuple[str, ...]):
        super().__init__(
            f"La especie '{especie}' no es válida; use una de: {', '.join(permitidas)}.",
            campo="especie",
        )


class SexoInvalido(ReglaIncumplida):
    """El sexo debe ser M o H (ck_mascotas_sexo)."""

    def __init__(self, sexo: str):
        super().__init__(f"El sexo '{sexo}' no es válido; use M o H.", campo="sexo")


class FechaNacimientoFutura(ReglaIncumplida):
    """La fecha de nacimiento no puede ser posterior a hoy."""

    def __init__(self, fecha):
        super().__init__(
            f"La fecha de nacimiento {fecha:%d-%m-%Y} no puede ser futura.",
            campo="fecha_nacimiento",
        )



# ---------------------------------------------------------------------
# Servicios (Jhon)
# ---------------------------------------------------------------------

class ServicioNoEncontrado(NoEncontrado):
    def __init__(self, servicio_id: int):
        super().__init__(f"No existe el servicio {servicio_id}.")


class CodigoServicioDuplicado(Duplicado):
    """Ya existe otro servicio con ese código (uq_servicios_codigo)."""

    def __init__(self, codigo: str):
        super().__init__(
            f"Ya existe un servicio con el código '{codigo}'.", campo="codigo"
        )


class NombreServicioDuplicado(Duplicado):
    """Ya existe otro servicio con ese nombre (uq_servicios_nombre)."""

    def __init__(self, nombre: str):
        super().__init__(
            f"Ya existe un servicio con el nombre '{nombre}'.", campo="nombre"
        )


class ServicioEnUso(EnUso):
    """Borrado protegido: el servicio aparece en el detalle de alguna atención."""

    def __init__(self, servicio_id: int):
        super().__init__(
            f"No se puede eliminar el servicio {servicio_id}: se usa en atenciones. "
            "Desactívelo en su lugar."
        )


class CodigoServicioInvalido(ReglaIncumplida):
    """El código no cumple el formato AAA-00."""

    def __init__(self, codigo: str):
        super().__init__(
            f"El código '{codigo}' no es válido; use el formato AAA-00 (por ejemplo VAC-01).",
            campo="codigo",
        )


class PrecioServicioInvalido(ReglaIncumplida):
    """El precio es negativo (ck_servicios_precio)."""

    def __init__(self, precio):
        super().__init__(f"El precio no puede ser negativo ({precio}).", campo="precio")