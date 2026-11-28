"""
Panel de administración de Django para las 5 entidades de la clínica.

Los modelos viven en Oracle (managed = False): el panel solo lee y escribe
filas, nunca crea tablas. Los permisos de cada rol (veterinario, recepcion)
los asigna el comando `crear_roles`.

Detalle de atención NO se registra con su propio ModelAdmin: su clave
primaria es compuesta (atencion_id, servicio_id) y el admin de Django no
soporta claves compuestas (ImproperlyConfigured). Se muestra como un inline
de solo lectura dentro de la atención.
"""
from django.contrib import admin

from veterinaria.domain.entities.atencion import AGENDADA
from veterinaria.infrastructure.models import (
    AtencionModel,
    DetalleAtencionModel,
    DuenoModel,
    MascotaModel,
    ServicioModel,
)


@admin.register(DuenoModel)
class DuenoAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre", "telefono", "email", "comuna", "fecha_registro")
    search_fields = ("rut", "nombre", "email")
    list_filter = ("comuna",)
    readonly_fields = ("fecha_registro",)
    ordering = ("nombre",)

    def has_delete_permission(self, request, obj=None):
        # R3: un dueño con mascotas no se elimina (si no, Oracle respondería
        # con ORA-02292 y el panel mostraría un error 500).
        if obj is not None and obj.mascotas.exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(MascotaModel)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especie", "raza", "sexo", "dueno", "fecha_nacimiento")
    list_select_related = ("dueno",)
    search_fields = ("nombre", "raza", "dueno__nombre", "dueno__rut")
    list_filter = ("especie", "sexo")
    autocomplete_fields = ("dueno",)  # buscador en vez de una lista gigante
    ordering = ("nombre",)

    def has_delete_permission(self, request, obj=None):
        # R3: una mascota con atenciones no se elimina.
        if obj is not None and obj.atenciones.exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(ServicioModel)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "precio", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("activo",)
    ordering = ("nombre",)

    def has_delete_permission(self, request, obj=None):
        # Un servicio usado en una atención no se elimina: se desactiva.
        if obj is not None and obj.detalles_atencion.exists():
            return False
        return super().has_delete_permission(request, obj)


class DetalleAtencionInline(admin.TabularInline):
    """Líneas de la atención, solo lectura (clave primaria compuesta)."""

    model = DetalleAtencionModel
    extra = 0
    can_delete = False
    fields = ("servicio", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("servicio", "cantidad", "precio_unitario", "subtotal")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AtencionModel)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "mascota", "motivo", "total", "estado")
    list_select_related = ("mascota",)
    search_fields = ("mascota__nombre", "mascota__dueno__nombre", "motivo")
    list_filter = ("estado",)
    autocomplete_fields = ("mascota",)
    # El total se calcula desde el detalle (R2): no se edita a mano.
    readonly_fields = ("total", "fecha_creacion")
    inlines = [DetalleAtencionInline]
    ordering = ("-fecha", "-id")

    def has_delete_permission(self, request, obj=None):
        # Igual que EliminarAtencion: solo se elimina una atención agendada.
        if obj is not None and obj.estado != AGENDADA:
            return False
        return super().has_delete_permission(request, obj)
