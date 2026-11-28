"""
Crea los roles de la clínica (grupos de Django) y un usuario de prueba por rol.

    python manage.py crear_roles
    python manage.py crear_roles --password 'MiClaveSegura1'

- veterinario: todos los permisos de la app (ver, agregar, cambiar y borrar).
- recepcion: agenda y cobra (agregar, cambiar y ver atenciones, dueños y
  mascotas), pero en servicios solo puede VER (no cambia precios). No borra
  nada. También ve el detalle de la atención (solo lectura).

El endpoint /api/auth/me/ entrega el rol según el nombre del grupo, por eso
los nombres son exactos. Se puede ejecutar varias veces: no duplica nada.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string

APP = "veterinaria"

# Modelo -> acciones permitidas a recepción. Los códigos de permiso llevan el
# sufijo del modelo: view_serviciomodel, change_atencionmodel, etc.
PERMISOS_RECEPCION = {
    "atencionmodel": ("add", "change", "view"),
    "duenomodel": ("add", "change", "view"),
    "mascotamodel": ("add", "change", "view"),
    "serviciomodel": ("view",),          # no cambia precios
    "detalleatencionmodel": ("view",),   # lo ve dentro de la atención
}

USUARIOS = {
    "veterinario": "veterinario1",
    "recepcion": "recepcion1",
}


class Command(BaseCommand):
    help = "Crea los grupos veterinario y recepcion con sus permisos y un usuario de prueba por rol."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            help="Contraseña de los usuarios de prueba nuevos (si se omite, se genera una al azar).",
        )

    def handle(self, *args, **opciones):
        todos = Permission.objects.filter(content_type__app_label=APP)
        if not todos.exists():
            raise CommandError(
                "No hay permisos de la app 'veterinaria'. Ejecuta primero: python manage.py migrate"
            )

        # --- veterinario: todos los permisos de la app ---
        veterinario, _ = Group.objects.get_or_create(name="veterinario")
        veterinario.permissions.set(todos)

        # --- recepcion: solo lo que agenda y cobra ---
        codigos = [
            f"{accion}_{modelo}"
            for modelo, acciones in PERMISOS_RECEPCION.items()
            for accion in acciones
        ]
        permisos_recepcion = todos.filter(codename__in=codigos)
        if permisos_recepcion.count() != len(codigos):
            raise CommandError("Faltan permisos de recepción: ¿se ejecutó migrate?")
        recepcion, _ = Group.objects.get_or_create(name="recepcion")
        recepcion.permissions.set(permisos_recepcion)

        self.stdout.write(
            f"Grupos listos: veterinario ({veterinario.permissions.count()} permisos), "
            f"recepcion ({recepcion.permissions.count()} permisos)"
        )

        # --- un usuario de prueba por rol ---
        User = get_user_model()
        clave = opciones["password"]
        for nombre_grupo, username in USUARIOS.items():
            usuario = User.objects.filter(username=username).first()
            if usuario is None:
                clave_usuario = clave or get_random_string(12)
                usuario = User.objects.create_user(
                    username=username,
                    email=f"{username}@huellitas.cl",
                    password=clave_usuario,
                )
                self.stdout.write(
                    f"Usuario creado: {username} · contraseña: {clave_usuario}  (anótala)"
                )
            else:
                self.stdout.write(f"Usuario existente: {username} (no se cambia su contraseña)")

            usuario.is_staff = True  # para que entre al panel /admin/
            usuario.save(update_fields=["is_staff"])
            usuario.groups.set([Group.objects.get(name=nombre_grupo)])

        self.stdout.write(
            "Listo. Crea además el superusuario con: python manage.py createsuperuser"
        )
