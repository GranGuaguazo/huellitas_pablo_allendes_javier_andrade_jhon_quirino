"""
Router de bases de datos.

- Las tablas del NEGOCIO (app "veterinaria") viven en Oracle (alias "negocio").
- Todo lo interno de Django (usuarios, grupos, permisos, tokens, admin,
  sesiones) vive en SQLite (alias "default").
"""

APP_NEGOCIO = "veterinaria"
ALIAS_NEGOCIO = "negocio"


class NegocioRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP_NEGOCIO:
            return ALIAS_NEGOCIO
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == APP_NEGOCIO:
            return ALIAS_NEGOCIO
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        # Solo se relacionan modelos que están en la misma base
        if obj1._meta.app_label == APP_NEGOCIO and obj2._meta.app_label == APP_NEGOCIO:
            return True
        if obj1._meta.app_label != APP_NEGOCIO and obj2._meta.app_label != APP_NEGOCIO:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Las tablas de Oracle se crean con los scripts de sql/, nunca con migrate
        if app_label == APP_NEGOCIO:
            return False
        # Las apps de Django solo migran en SQLite
        return db == "default"
