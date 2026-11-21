"""
Modelo ORM de la tabla MASCOTAS (adaptador secundario).

managed = False: la tabla la crea sql/01_crear_tablas.sql, nunca migrate.
"""
from django.db import models

from veterinaria.domain.entities.mascota import ESPECIES, SEXOS
from veterinaria.infrastructure.models.dueno import DuenoModel


class MascotaModel(models.Model):
    id = models.AutoField(primary_key=True)  # NUMBER IDENTITY (NOCACHE)
    # FK a DUENOS (fk_mascotas_dueno). Con db_column el atributo dueno_id sigue
    # existiendo, y el repositorio lo usa igual que antes de ser ForeignKey.
    # DO_NOTHING: el borrado protegido (R3) lo decide el caso de uso, y la
    # restricción final la mantiene Oracle.
    dueno = models.ForeignKey(
        DuenoModel,
        on_delete=models.DO_NOTHING,
        db_column="dueno_id",
        related_name="mascotas",
    )
    nombre = models.CharField(max_length=60)
    especie = models.CharField(
        max_length=20, choices=[(e, e.capitalize()) for e in ESPECIES]
    )  # ck_mascotas_especie
    raza = models.CharField(max_length=60, null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=[(s, s) for s in SEXOS])  # ck_mascotas_sexo
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "mascotas"
        app_label = "veterinaria"
        ordering = ["nombre"]
        verbose_name = "mascota"
        verbose_name_plural = "mascotas"

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
