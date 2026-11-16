# Bitácora del proyecto · G02 «Huellitas»

Una entrada por semana y por integrante: qué hizo, en qué archivos, qué problema tuvo y cómo lo resolvió, y qué hará la semana siguiente. **Debe coincidir con los commits** de cada uno.

## Semana 1 · Diseño, base de datos y conexión

### Javier Andrade

- **Qué hizo:** modelo entidad-relación y diccionario de datos de atenciones y detalle_atencion; clave compuesta y columna virtual `subtotal`.
- **Archivos:** `docs/modelo_datos.md`, `docs/modelo_datos.mmd`, `docs/diccionario_datos.md`, `backEnd/sql/01_crear_tablas.sql` (atenciones, detalle_atencion).
- **Problema y solución:**
    1. `probar_conexion` fallaba con `DPY-4011: the database or network closed the connection`. FreeSQL exige TLS en el puerto 2484 y el DSN se armaba sin protocolo (TCP sin cifrar). Se agregó `ORACLE_PROTOCOL` en `settings.py`: usa `tcps` automáticamente para el puerto 2484.
    2. Con el `.env` vacío el error era `DPY-3001: bequeath is only supported in thick mode`, que no explica nada. `probar_conexion` ahora revisa antes de conectar que estén las variables `ORACLE_*` e indica cuáles faltan.
    3. `01_crear_tablas.sql` fallaba al crear `detalle_atencion` con `ORA-02264: name already used by an existing constraint`: mi esquema tiene la tabla `DETALLE_VENTA` de otro ramo, que ya usa `ck_detalle_cantidad`. Los CHECK de detalle se renombraron a `ck_detatencion_cantidad` y `ck_detatencion_precio` (también en el diccionario de datos).
- **Archivos (correcciones a la configuración, hechas al probar la conexión en mi esquema):** `backEnd/veterinaria_project/settings.py`, `backEnd/veterinaria/management/commands/probar_conexion.py`, `backEnd/sql/01_crear_tablas.sql`, `backEnd/.env.example`, `docs/diccionario_datos.md`, `README.md`.
- **Próxima semana:** entidades de dominio y puertos de atenciones y detalle.
- **Uso de IA:** Se usó Claude Code para instalar el entorno virtual, ejecutar los pasos del README y diagnosticar los tres errores anteriores. La IA propuso las correcciones; se comprobaron ejecutando `probar_conexion` contra FreeSQL hasta obtener las 5 tablas con datos.

### Pablo Allendes

- **Qué hizo:** tablas duenos y mascotas con sus restricciones; datos de ejemplo realistas con RUT válidos.
- **Archivos:** `backEnd/sql/01_crear_tablas.sql` (duenos, mascotas), `backEnd/sql/02_datos_ejemplo.sql`.
- **Problema y solución:** _(completar)_
- **Próxima semana:** capas completas de dueños y mascotas.
- **Uso de IA:** _(qué se le preguntó a la IA y qué se cambió del resultado)_

### Jhon Quirino

- **Qué hizo:** tabla servicios; proyecto Django, entorno virtual, `.env`, `settings.py` con dos bases (SQLite + Oracle), router y comando `probar_conexion` (paso 11). Repositorio con `.gitignore` y `.env.example`.
- **Archivos:** `backEnd/veterinaria_project/settings.py`, `db_router.py`, `veterinaria/management/commands/probar_conexion.py`, `.gitignore`, `backEnd/.env.example`.
- **Evidencia de conexión:** salida de `python manage.py probar_conexion` de cada integrante.

    Javier Andrade (15-11-2026):

    ```
    Conexión OK
      Usuario (esquema): JAVIER_ANDRADE09_SCHEMA_Z9S5W
      Base de datos:     FREESQLPRD_SCHEMA_PDB01
      Hora UTC Oracle:   2026-11-15 23:58:15
      DUENOS             6 filas
      MASCOTAS           6 filas
      SERVICIOS          7 filas
      ATENCIONES         5 filas
      DETALLE_ATENCION   8 filas
    ```

    Pablo Allendes: _(pegar)_

    Jhon Quirino: _(pegar)_

- **Problema y solución:** _(completar)_
- **Próxima semana:** capas completas de servicios.
- **Uso de IA:** _(qué se le preguntó a la IA y qué se cambió del resultado)_
