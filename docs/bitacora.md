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
- **Problema y solución:** Se soluciono el problema para llevar un registro de los dueños y las mascotas
- **Próxima semana:** capas completas de dueños y mascotas.
- **Uso de IA:** _(qué se le preguntó a la IA y qué se cambió del resultado)_

### Jhon Quirino

- **Qué hizo:** tabla servicios; proyecto Django, entorno virtual, `.env`, `settings.py` con dos bases (SQLite + Oracle), router y comando `probar_conexion` (paso 11). Repositorio con `.gitignore` y `.env.example`.
- **Archivos:** `backEnd/veterinaria_project/settings.py`, `db_router.py`, `veterinaria/management/commands/probar_conexion.py`, `.gitignore`, `backEnd/.env.example`.
- **Problema y solución:**
    1. En mi esquema solo existía la tabla `SERVICIOS`, así que `probar_conexion` iba a marcar las otras cuatro como `NO EXISTE`. Se ejecutaron completos `01_crear_tablas.sql` y `02_datos_ejemplo.sql` en mi esquema, como script y no sentencia por sentencia. Quedaron las 5 tablas con 6, 6, 7, 5 y 8 filas.
    2. `probar_conexion` fallaba con `RuntimeError: Falta DJANGO_SECRET_KEY en el archivo .env`. El `.env` existía y estaba en `backEnd/`, pero usaba otros nombres de variables (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` y un único `ORACLE_DSN`) que `settings.py` no lee. Se renombraron a `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` y `DJANGO_ALLOWED_HOSTS`, y el DSN se separó en `ORACLE_HOST`, `ORACLE_PORT` y `ORACLE_SERVICE`, siguiendo `.env.example`. Se verificó que `.env` esté en `.gitignore`.
    3. `git push` fue rechazado porque mi rama estaba un commit atrasada respecto de `origin/main` (un compañero había subido cambios). Se hizo `git pull` antes de volver a subir, para no pisar su trabajo en `docs/bitacora.md`.
- **Próxima semana:** capas completas de servicios (entidad y puerto en `domain/`, casos de uso en `application/`, modelo ORM y repositorio en `infrastructure/`).
- **Uso de IA:** Se usó Claude (chat) para entender los errores de `probar_conexion` y de git, y para ordenar los pasos de entrega. La IA detectó que los nombres de las variables del `.env` no coincidían con los de `.env.example`; la corrección se comprobó ejecutando `probar_conexion` hasta obtener `Conexión OK` y las 5 tablas con datos.


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

    Pablo Allendes: _(16-11-2026)_

    ```
    Conexión OK
      Usuario (esquema): PABLO_ALLENDES07_SCHEMA_38WPO
      Base de datos:     FREESQLPRD_SCHEMA_PDB01
      Hora UTC Oracle:   2026-11-16 12:32:43
      DUENOS             6 filas
      MASCOTAS           6 filas
      SERVICIOS          7 filas
      ATENCIONES         5 filas
      DETALLE_ATENCION   8 filas
    ```

    Jhon Quirino: _(16-11-2026)_

    ```
    Conexión OK
      Usuario (esquema): JHONQUIRINO14_SCHEMA_II2RP
      Base de datos:     FREESQLPRD_SCHEMA_PDB01
      Hora UTC Oracle:   2026-11-16 02:20:12
      DUENOS             6 filas
      MASCOTAS           6 filas
      SERVICIOS          7 filas
      ATENCIONES         5 filas
      DETALLE_ATENCION   8 filas
    ```
     Capturas: `docs/capturas/evidencia_conexion_jhon.png` (salida de `probar_conexion`), `docs/capturas/evidencia_tablas_jhon.png` (`user_tables` con las 5 tablas) y `docs/capturas/evidencia_filas_jhon.png` (filas por tabla).

- **Problema y solución:** _(completar)_
- **Próxima semana:** capas completas de servicios.
- **Uso de IA:** _(qué se le preguntó a la IA y qué se cambió del resultado)_