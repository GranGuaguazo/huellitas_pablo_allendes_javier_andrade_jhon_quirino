"""
Modelo ORM de la tabla SERVICIOS (adaptador secundario).

managed = False: la tabla la crea sql/01_crear_tablas.sql, nunca migrate.
"""
from django.db import models


class ServicioModel(models.Model):
    id = models.AutoField(primary_key=True)  # NUMBER IDENTITY (NOCACHE)
    codigo = models.CharField(max_length=10)  # uq_servicios_codigo, formato AAA-00
    nombre = models.CharField(max_length=100)  # uq_servicios_nombre
    descripcion = models.TextField(null=True, blank=True)  # CLOB
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # ck_servicios_precio >= 0
    activo = models.BooleanField(default=True)  # NUMBER(1), ck_servicios_activo IN (0,1)

    class Meta:
        managed = False
        db_table = "servicios"
        app_label = "veterinaria"
        ordering = ["nombre"]
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"