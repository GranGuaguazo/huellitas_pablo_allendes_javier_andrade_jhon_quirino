from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Clínica veterinaria Huellitas"
admin.site.site_title = "Huellitas"
admin.site.index_title = "Administración"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("veterinaria.api.urls")),
]