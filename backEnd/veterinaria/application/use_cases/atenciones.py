"""
Casos de uso de atenciones (un caso de uso por operación).

Semana 2: consultas (listar y obtener).
Semana 3: crear con detalle, cambiar estado y eliminar, con las reglas R1 y R2.

Solo dependen del puerto (domain/ports), nunca del ORM ni de Oracle.
"""
from datetime import date

from veterinaria.application.exceptions import AtencionNoEncontrada
from veterinaria.domain.entities.atencion import Atencion
from veterinaria.domain.ports.atencion_repository import AtencionRepository


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
