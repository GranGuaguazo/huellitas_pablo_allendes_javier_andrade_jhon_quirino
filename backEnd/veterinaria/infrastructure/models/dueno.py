"""
Modelo ORM de la tabla DUENOS (adaptador secundario).

managed = False: la tabla la crea sql/01_crear_tablas.sql, nunca migrate.
"""
from django.db import models
from django.utils import timezone


class DuenoModel(models.Model):
    id = models.AutoField(primary_key=True)  # NUMBER IDENTITY (NOCACHE)
    rut = models.CharField(max_length=12)  # uq_duenos_rut, formato 12.345.678-5
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.CharField(max_length=120)  # uq_duenos_email, ck_duenos_email
    comuna = models.CharField(max_length=60)
    fecha_registro = models.DateTimeField(default=timezone.now)  # UTC; Oracle pone el DEFAULT

    class Meta:
        managed = False
        db_table = "duenos"
        app_label = "veterinaria"
        ordering = ["nombre"]
        verbose_name = "dueño"
        verbose_name_plural = "dueños"

    def __str__(self):
        return f"{self.nombre} ({self.rut})"
