from django.contrib import admin
from django.urls import path

admin.site.site_header = "Clínica veterinaria Huellitas"
admin.site.site_title = "Huellitas"
admin.site.index_title = "Administración"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Las rutas de la API (/api/) se agregan en la semana 3
]
