"""
Modelo ORM de la tabla ATENCIONES (adaptador secundario).

managed = False: la tabla la crea sql/01_crear_tablas.sql, nunca migrate.
"""
from django.db import models
from django.utils import timezone

from veterinaria.domain.entities.atencion import ESTADO_INICIAL, ESTADOS


class AtencionModel(models.Model):
    id = models.AutoField(primary_key=True)  # NUMBER IDENTITY (NOCACHE)
    # FK a MASCOTAS (fk_atenciones_mascota). Se declara como entero mientras
    # no exista MascotaModel; al cambiarla a ForeignKey(db_column="mascota_id")
    # el atributo mascota_id sigue existiendo y el repositorio no cambia.
    mascota_id = models.IntegerField()
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=200)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=12,
        choices=[(e, e.capitalize()) for e in ESTADOS],
        default=ESTADO_INICIAL,
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "atenciones"
        app_label = "veterinaria"
        ordering = ["-fecha", "-id"]
        verbose_name = "atención"
        verbose_name_plural = "atenciones"

    def __str__(self):
        return f"Atención {self.id} · {self.fecha:%d-%m-%Y} · {self.estado}"
