"""
Modelo ORM de la tabla DETALLE_ATENCION.

- Clave primaria compuesta (atencion_id, servicio_id): CompositePrimaryKey
  de Django 5.2.
- subtotal es una columna VIRTUAL de Oracle: GeneratedField con
  db_persist=False, así Django nunca intenta escribirla (ORA-54013).
"""
from django.db import models

from veterinaria.infrastructure.models.atencion import AtencionModel
from veterinaria.infrastructure.models.servicio import ServicioModel


class DetalleAtencionModel(models.Model):
    pk = models.CompositePrimaryKey("atencion_id", "servicio_id")
    atencion = models.ForeignKey(
        AtencionModel,
        on_delete=models.CASCADE,  # en Oracle: fk_detalle_atencion ON DELETE CASCADE
        db_column="atencion_id",
        related_name="detalles",
    )
    # FK a SERVICIOS (fk_detalle_servicio). DO_NOTHING: un servicio usado no
    # se borra (borrado protegido en el caso de uso de servicios).
    servicio = models.ForeignKey(
        ServicioModel,
        on_delete=models.DO_NOTHING,
        db_column="servicio_id",
        related_name="detalles_atencion",
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.GeneratedField(
        expression=models.F("cantidad") * models.F("precio_unitario"),
        output_field=models.DecimalField(max_digits=12, decimal_places=2),
        db_persist=False,
    )

    class Meta:
        managed = False
        db_table = "detalle_atencion"
        app_label = "veterinaria"
        verbose_name = "detalle de atención"
        verbose_name_plural = "detalles de atención"

    def __str__(self):
        return f"Atención {self.atencion_id} · servicio {self.servicio_id} × {self.cantidad}"
