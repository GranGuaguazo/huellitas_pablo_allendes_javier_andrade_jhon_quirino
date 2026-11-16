"""
Paso 11 del manual: prueba la conexión a Oracle (alias "negocio").
Uso:  python manage.py probar_conexion
"""
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

TABLAS = ["DUENOS", "MASCOTAS", "SERVICIOS", "ATENCIONES", "DETALLE_ATENCION"]
VARIABLES = ["ORACLE_HOST", "ORACLE_PORT", "ORACLE_SERVICE", "ORACLE_USER", "ORACLE_PASSWORD"]


class Command(BaseCommand):
    help = "Prueba la conexión a Oracle y cuenta las filas de las tablas del negocio"

    def handle(self, *args, **options):
        # Sin estos datos el DSN queda ":1521/" y oracledb da un error confuso (DPY-3001)
        faltan = [v for v in VARIABLES if os.getenv(v, "").strip() == ""]
        if faltan:
            raise CommandError("Faltan datos de Oracle en backEnd/.env: " + ", ".join(faltan))

        conexion = connections["negocio"]
        with conexion.cursor() as cursor:
            cursor.execute("SELECT USER, SYS_CONTEXT('USERENV','DB_NAME'), "
                           "TO_CHAR(SYS_EXTRACT_UTC(SYSTIMESTAMP),'YYYY-MM-DD HH24:MI:SS') FROM dual")
            usuario, base, hora_utc = cursor.fetchone()
            self.stdout.write(self.style.SUCCESS("Conexión OK"))
            self.stdout.write("  Usuario (esquema): " + str(usuario))
            self.stdout.write("  Base de datos:     " + str(base))
            self.stdout.write("  Hora UTC Oracle:   " + str(hora_utc))

            for tabla in TABLAS:
                cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = %s", [tabla])
                existe = cursor.fetchone()[0] == 1
                if existe:
                    cursor.execute("SELECT COUNT(*) FROM " + tabla)
                    filas = cursor.fetchone()[0]
                    self.stdout.write("  " + tabla.ljust(18) + " " + str(filas) + " filas")
                else:
                    self.stdout.write(self.style.ERROR("  " + tabla.ljust(18) + " NO EXISTE (ejecuta sql/01_crear_tablas.sql)"))
