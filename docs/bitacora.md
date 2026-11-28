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
- **Problema y solución:** el diseño debía permitir registrar a cada dueño con sus mascotas sin datos repetidos ni inconsistentes. Se resolvió con restricciones nombradas en Oracle: `uq_duenos_rut` y `uq_duenos_email` (un dueño no se repite), `ck_duenos_email` (el email lleva `@`), `fk_mascotas_dueno` con índice `idx_mascotas_dueno` (toda mascota pertenece a un dueño existente), `ck_mascotas_especie` y `ck_mascotas_sexo` (solo valores permitidos). Los datos de ejemplo usan RUT válidos (dígito verificador correcto).
- **Próxima semana:** capas completas de dueños y mascotas.
- **Uso de IA:** No se uso la IA.

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

- **Problema y solución:**
- **Próxima semana:** capas completas de servicios.
- **Uso de IA:**

## Semana 2 · Capas hexagonales de las entidades maestras

### Javier Andrade

- **Qué hizo:** capas de dominio e infraestructura de la entidad principal `atenciones` y de su detalle `detalle_atencion`: entidades puras con los estados y transiciones permitidas, puertos (ABC) con las operaciones del negocio y las consultas propias (R1 y borrados protegidos), excepciones de negocio base del proyecto y las de atenciones, modelos `managed = False` (clave compuesta y columna virtual), repositorios Oracle con la creación de cabecera + detalle en una sola transacción, contenedor de dependencias `di.py` y casos de uso de consulta (`ListarAtenciones`, `ObtenerAtencion`).
- **Archivos:** `veterinaria/domain/entities/atencion.py`, `domain/entities/detalle_atencion.py`, `domain/ports/atencion_repository.py`, `domain/ports/detalle_atencion_repository.py`, `application/exceptions.py`, `application/use_cases/atenciones.py`, `infrastructure/models/atencion.py`, `infrastructure/models/detalle_atencion.py`, `infrastructure/models/__init__.py`, `infrastructure/repositories/atencion_repository.py`, `infrastructure/repositories/detalle_atencion_repository.py`, `infrastructure/di.py`, `veterinaria/models.py`.
- **Problema y solución:**
    1. `subtotal` es una columna `VIRTUAL` de Oracle: si Django la incluye en el `INSERT`, Oracle responde `ORA-54013`. Se declaró como `GeneratedField(db_persist=False)`, que Django nunca escribe y lee después de insertar.
    2. La clave primaria de `detalle_atencion` es compuesta. Se usó `CompositePrimaryKey("atencion_id", "servicio_id")`, disponible desde Django 5.2.
    3. R1 habla de «el mismo día», pero Oracle guarda las fechas en UTC: una atención a las 22:00 de Chile queda guardada al día siguiente. `existe_agendada_mismo_dia` arma el rango 00:00–24:00 en hora de Chile y Django lo convierte a UTC al consultar.
    4. Los modelos de `mascotas` y `servicios` (Pablo y Jhon) todavía no existen, así que `mascota_id` y `servicio_id` se declararon como enteros. Cuando se suban esos modelos se cambian a `ForeignKey(db_column=...)`; el atributo `mascota_id` / `servicio_id` se mantiene y el repositorio no cambia.
- **Prueba:** desde `manage.py shell` contra mi esquema: listar (con filtros por estado y texto), obtener (y el error `AtencionNoEncontrada` con un id inexistente), crear una atención con dos líneas, cambiar su estado y eliminarla, todo dentro de una transacción que se revirtió al final para no dejar datos de prueba. El `subtotal` lo devolvió Oracle y coincidió con `calcular_total()`.
- **Para mis compañeros:** `AtencionRepository.existe_con_mascota()` (R3, borrado protegido de mascotas) y `DetalleAtencionRepository.existe_con_servicio()` (borrado protegido de servicios) ya están listos. En `application/exceptions.py` y `infrastructure/di.py` hay una sección para cada uno.
- **Próxima semana:** casos de uso `CrearAtencion` (con R1 y R2: solo servicios activos y total recalculado desde el detalle), `CambiarEstadoAtencion` (solo transiciones permitidas) y `EliminarAtencion` (solo `agendada`); cambiar `mascota_id` y `servicio_id` a `ForeignKey`.
- **Uso de IA:** se usó Claude Code para generar las capas de atenciones a partir del diccionario de datos y para probarlas contra FreeSQL.

### Pablo Allendes

- **Qué hizo:** capas completas de `duenos` y `mascotas`: entidades puras (con los valores permitidos de especie y sexo), puertos (ABC) con consultas por RUT, email y por (dueño, nombre) para el control de duplicados, excepciones de negocio, casos de uso (listar, obtener, crear, actualizar y eliminar de cada entidad) con RUT validado por módulo 11, email válido y único, nombre de mascota único por dueño, fecha de nacimiento no futura y la regla R3 (borrado protegido), modelos `managed = False` (`MascotaModel` con `ForeignKey` a `DuenoModel`), repositorios Oracle, mi sección de `di.py` y el comando `probar_duenos_mascotas`. Pruebas de los casos de uso con repositorios falsos en memoria.
- **Archivos:** `veterinaria/domain/entities/dueno.py`, `domain/entities/mascota.py`, `domain/ports/dueno_repository.py`, `domain/ports/mascota_repository.py`, `application/exceptions.py` (sección Dueños y mascotas), `application/use_cases/duenos.py`, `application/use_cases/mascotas.py`, `infrastructure/models/dueno.py`, `infrastructure/models/mascota.py`, `infrastructure/models/__init__.py`, `infrastructure/repositories/dueno_repository.py`, `infrastructure/repositories/mascota_repository.py`, `infrastructure/di.py`, `management/commands/probar_duenos_mascotas.py`, `tests/test_duenos_mascotas.py`.
- **Problema y solución:**
    1. Para probar contra Oracle solo existía `.env.example` con los valores vacíos y no tenía mi `.env`. Se copió a `backEnd/.env`, se completaron `ORACLE_SERVICE`, `ORACLE_USER` y `ORACLE_PASSWORD` con los datos del panel de FreeSQL (puerto 2484, `ORACLE_PROTOCOL` vacío para que use `tcps`) y se verificó que `.env` no se suba a git.
    2. La `DJANGO_SECRET_KEY` se genera con Django, así que hubo que activar primero el entorno virtual `.venv` (que está en la carpeta `huellitas`, fuera de `backEnd`) con `.venv\Scripts\activate`.
    3. `probar_conexion` dio `Conexión OK`, pero mis cinco tablas estaban con 0 filas, así que la prueba no tenía datos (por ejemplo, Rocky para comprobar el borrado protegido). Se ejecutó `02_datos_ejemplo.sql` completo, como script y una sola vez, en mi esquema de FreeSQL.
- **Decisiones de diseño:**
    1. `EliminarDueno` recibe también el repositorio de mascotas y usa `existe_con_dueno()`: un dueño con mascotas no se elimina (R3).
    2. `EliminarMascota` recibe el repositorio de atenciones y usa `existe_con_mascota()` de Javier: una mascota con atenciones no se elimina (R3).
    3. `ActualizarDueno` y `ActualizarMascota` solo tratan RUT, email o nombre como duplicado si pertenecen a **otro** registro, así se puede guardar un registro con sus propios datos.
    4. El RUT se normaliza al formato `12.345.678-5` antes de guardar, para que `uq_duenos_rut` funcione igual sin importar cómo lo escriba el usuario.
- **Prueba:** `python -m unittest veterinaria.tests.test_duenos_mascotas -v` (33 pruebas, sin Django ni Oracle) y `python manage.py probar_duenos_mascotas` contra mi esquema de FreeSQL: crear, obtener, listar con filtros, actualizar, RUT y email duplicados, RUT y email inválidos, nombre de mascota repetido para el mismo dueño, dueño inexistente, especie y sexo inválidos, fecha de nacimiento futura, no encontrado, borrado protegido (un dueño con mascotas y Rocky, que tiene atenciones) y eliminar registros libres; todo dentro de una transacción que se revirtió. Captura: `docs/capturas/evidencia_duenos_mascotas_pablo.png`.
- **Para mis compañeros:** `MascotaModel` ya existe, así que Javier puede cambiar `mascota_id` de `AtencionModel` a `ForeignKey(MascotaModel, db_column="mascota_id")`, y `ObtenerMascota` sirve para validar que la mascota exista al crear una atención.
- **Próxima semana:** panel de administración, `crear_roles` y estructura del frontend.
- **Uso de IA:** se usó Claude (chat) para generar el código de pruebas de dueños y mascotas en `backEnd/veterinaria/managament/commands/probar_duenos_mascotas.py`.

### Jhon Quirino

- **Qué hizo:** capas completas de la entidad `servicios`: entidad pura, puerto (ABC) con consultas por código y por nombre para el control de duplicados, excepciones de negocio, casos de uso (listar, obtener, crear, actualizar y eliminar) con validación del código `AAA-00`, precio ≥ 0, duplicados y borrado protegido, modelo `managed = False`, repositorio Oracle y contenedor de dependencias. Pruebas de los casos de uso con repositorios falsos en memoria y comando `probar_servicios` contra Oracle.
- **Archivos:** `veterinaria/domain/entities/servicio.py`, `domain/ports/servicio_repository.py`, `application/exceptions.py` (sección Servicios), `application/use_cases/servicios.py`, `infrastructure/models/servicio.py`, `infrastructure/models/__init__.py`, `infrastructure/repositories/servicio_repository.py`, `infrastructure/di.py`, `management/commands/probar_servicios.py`, `tests/__init__.py`, `tests/test_servicios.py`.
- **Problema y solución:**
    1. Al crear `servicio.py` y `servicio_repository.py` en el lugar equivocado (carpetas `docs` y `domain`, y con el nombre en plural), Python respondía `ModuleNotFoundError`. Se movieron a `domain/entities` y `domain/ports` con el nombre exacto y se verificó con un `python -c` de importación.
    2. Al probar el repositorio con el archivo todavía vacío, Python respondía `ImportError: cannot import name 'OracleServicioRepository'`. Se pegó el código, se guardó y la comprobación pasó.
- **Decisiones de diseño:**
    1. `ActualizarServicio` solo trata el código o el nombre como duplicado si pertenecen a **otro** servicio; así se puede guardar un servicio con su propio código.
    2. `EliminarServicio` recibe también el repositorio de detalle de atenciones y usa `existe_con_servicio()` (de Javier): un servicio usado en una atención no se elimina, se desactiva (`activo = 0`), que es la base de la regla R2.
- **Prueba:** `python -m unittest veterinaria.tests.test_servicios -v` (14 pruebas, sin Django ni Oracle) y `python manage.py probar_servicios` contra mi esquema de FreeSQL: crear, obtener, listar con filtros, actualizar, duplicados, código inválido, precio negativo, no encontrado, borrado protegido (CON-01 está en atenciones) y eliminar uno libre; todo dentro de una transacción que se revirtió. Capturas: `docs/capturas/evidencia_servicios_oracle_jhon.png` y `docs/capturas/evidencia_pruebas_servicios_jhon.png`.
- **Para mis compañeros:** `ServicioModel` ya existe, así que Javier puede cambiar `servicio_id` a `ForeignKey(db_column="servicio_id")`, y `ObtenerServicio` sirve para validar en R2 que el servicio esté activo.
- **Próxima semana:** autenticación de la API (login, logout, `/api/auth/me/` con cookie HttpOnly y CSRF).
- **Uso de IA:** se usó Claude (chat) para generar el código de servicios capa por capa y para diagnosticar los errores de ruta. Cada capa se comprobó con comandos en la terminal, con las 14 pruebas unitarias y con la prueba real contra Oracle.

## Semana 3 · Entidad principal, reglas de negocio y seguridad

### Javier Andrade

- **Qué hizo:** casos de uso de escritura de la entidad principal: `CrearAtencion` (atención + líneas de detalle en una sola transacción, con R1 y R2), `CambiarEstadoAtencion` (solo transiciones permitidas: `agendada → realizada → pagada` y `agendada → cancelada`) y `EliminarAtencion` (solo en `agendada`). `mascota_id` y `servicio_id` pasaron a `ForeignKey` hacia `MascotaModel` y `ServicioModel`, y la atención ahora se devuelve con el nombre de la mascota y de cada servicio. Pruebas unitarias con repositorios falsos y comando `probar_atenciones` contra Oracle.
- **Archivos:** `veterinaria/application/use_cases/atenciones.py`, `application/exceptions.py` (sección Atenciones), `domain/entities/atencion.py`, `domain/entities/detalle_atencion.py`, `domain/ports/atencion_repository.py`, `infrastructure/models/atencion.py`, `infrastructure/models/detalle_atencion.py`, `infrastructure/repositories/atencion_repository.py`, `infrastructure/repositories/detalle_atencion_repository.py`, `infrastructure/di.py`, `management/commands/probar_atenciones.py`, `tests/test_atenciones.py`.
- **Reglas en los casos de uso:**
    - **R1** `CrearAtencion` consulta `existe_agendada_mismo_dia()` antes de guardar. Una atención cancelada ya no bloquea el día.
    - **R2** cada línea se valida contra el catálogo: el servicio debe existir y estar activo. El `precio_unitario` se toma del servicio (si el cliente lo envía, se ignora) y el total se calcula con `calcular_total()` al crear y se vuelve a calcular en cada cambio de estado.
    - Otras validaciones: mascota existente, motivo obligatorio de hasta 200 caracteres, al menos una línea, servicio no repetido (clave compuesta) y cantidad entera entre 1 y 99999.
- **Problema y solución:**
    1. El puerto recibía `dia: date` para R1, así que el caso de uso tenía que calcular «el día en Chile» y para eso necesitaba conocer zonas horarias, que es tarea de la infraestructura. Ahora el puerto recibe la fecha completa y el repositorio la pasa a hora de Chile con `timezone.localtime`. Se probó con una atención a las 22:30 de Chile, que Oracle guarda a la 01:30 UTC del día siguiente: R1 la detecta igual.
    2. Al pasar a `ForeignKey`, cada línea consultaba su servicio por separado (N+1 consultas). Se usó `select_related("mascota")` y un `Prefetch` de los detalles con `select_related("servicio")`.
- **Prueba:** `python -m unittest veterinaria.tests.test_atenciones -v` (23 pruebas, sin Django ni Oracle; junto con las de mis compañeros son 70 y todas pasan) y `python manage.py probar_atenciones` contra mi esquema de FreeSQL: crear con dos líneas (total 42.000 = 18.000 + 2 × 12.000), R1 fallando y permitido con otra mascota, R2 con ECO-01 inactivo, sin detalle, servicio repetido, mascota inexistente, transiciones permitidas y no permitidas, eliminar una realizada (falla) y una agendada (OK); todo dentro de una transacción que se revirtió (27-11-2026). Captura: `docs/capturas/evidencia_atenciones_javier.png`.
- **Para mis compañeros:** en `di.py` están listos `crear_atencion`, `cambiar_estado_atencion` y `eliminar_atencion` para las vistas. `AtencionModel.mascota` y `DetalleAtencionModel.servicio` ya son `ForeignKey`, así que en el admin se pueden usar `list_display = ("mascota", ...)` y `search_fields = ("mascota__nombre",)`.
- **Próxima semana:** revisión de la Nota 1; después, serializers de entrada y salida de atenciones (detalle anidado), manejo uniforme de errores y paginación, y el endpoint de reporte (ingresos por servicio en un rango de fechas).
- **Uso de IA:** se le pidió a Claude Code implementar mi parte de la semana 3 a partir del enunciado y de mi plan de la semana 2. Generó los casos de uso, las pruebas y el comando `probar_atenciones`, y los ejecutó contra FreeSQL. El cambio del puerto de R1 (recibir la fecha completa en vez del día) lo propuso la IA. También se le pidió revisar qué debía completar yo en la bitácora: indicó agregar la captura de evidencia y precisar este punto. No se modificó a mano el código generado; se comprobó ejecutando las pruebas y `probar_atenciones` en mi esquema.

### Pablo Allendes

* **Qué hizo:** panel de administración de Django (`admin.py`) con las 5 entidades de la clínica, y el comando `crear\\\_roles` que crea los grupos `veterinario` y `recepcion` con sus permisos y un usuario de prueba por rol.
* **Archivos:** `veterinaria/admin.py`, `veterinaria/management/commands/crear\\\_roles.py`.
* **Panel de administración:**

  * `DuenoAdmin`, `MascotaAdmin`, `ServicioAdmin` y `AtencionAdmin`, con `list\\\_display`, `search\\\_fields` y `list\\\_filter` (por ejemplo, atenciones filtradas por `estado` y buscadas por `mascota\\\_\\\_nombre`).
  * `detalle\\\_atencion` no se registra con su propio `ModelAdmin`: tiene clave primaria compuesta y Django lanza `ImproperlyConfigured`. Va como `TabularInline` de solo lectura dentro de la atención (`extra = 0`, `can\\\_delete = False`, sin permiso para agregar ni cambiar).
  * El `total` de la atención es de solo lectura, porque se calcula desde el detalle (R2).
  * El borrado protegido (R3) también rige en el panel: `has\\\_delete\\\_permission` no permite eliminar un dueño con mascotas, una mascota con atenciones, un servicio usado en una atención ni una atención que no esté `agendada`. Sin esto, Oracle respondería con `ORA-02292` y el panel mostraría un error 500.
* **Roles (`crear\\\_roles`):**

  * `veterinario`: todos los permisos de la app. `recepcion`: agregar, cambiar y ver atenciones, dueños y mascotas; en servicios solo ver (no cambia precios); sin borrar nada.
  * A `recepcion` se le agregó además `view\\\_detalleatencionmodel`, para que pueda ver las líneas de la atención dentro del panel.
  * Los códigos de permiso llevan el sufijo del modelo (`view\\\_serviciomodel`, `change\\\_atencionmodel`).
  * Crea `veterinario1` y `recepcion1` con `is\\\_staff = True`; se puede ejecutar varias veces sin duplicar nada. El superusuario se crea con `createsuperuser`.
* **Problema y solución:**

  1. *(completar con un problema REAL que tuviste al ejecutar `migrate`, `crear\\\_roles` o al entrar al panel, y cómo lo resolviste)*
* **Prueba:** *(completar: qué viste en `/admin/` con cada usuario; por ejemplo, que `recepcion1` no puede agregar servicios y que `veterinario1` sí. Agrega tus capturas en `docs/capturas/`)*
* **Próxima semana:** *(completar según el reparto)*
* **Uso de IA:** se usó Claude (chat) para generar `admin.py` y `crear\\\_roles.py`

### Jhon Quirino

- **Qué hizo:** autenticación de la API: `GET /api/auth/csrf/`, `POST /api/auth/login/`, `GET /api/auth/me/` (con usuario y rol) y `POST /api/auth/logout/`. El token viaja en una cookie `auth_token` HttpOnly y las peticiones que modifican datos (POST, PUT, PATCH, DELETE) exigen el header `X-CSRFToken`. Sin sesión, la API responde 401. También configuré Django REST Framework, `authtoken` y CORS en `settings.py` y dejé montadas las rutas bajo `/api/`.
- **Archivos:** `backEnd/veterinaria_project/settings.py`, `veterinaria_project/urls.py`, `veterinaria/api/__init__.py`, `api/authentication.py`, `api/views_auth.py`, `api/urls.py`.
- **Cómo funciona:**
    - `settings.py`: se agregaron `rest_framework`, `rest_framework.authtoken` y `corsheaders`; `CorsMiddleware` antes de `CommonMiddleware`; CORS limitado a `FRONTEND_ORIGIN` con credenciales; `CSRF_COOKIE_HTTPONLY = False` (el frontend debe leer `csrftoken`) y un bloque `REST_FRAMEWORK` con autenticación por cookie y `IsAuthenticated` como permiso por defecto.
    - `CookieTokenAuthentication` lee el token desde la cookie y llama a `enforce_csrf()`, que solo bloquea los métodos que modifican datos.
    - `login` valida usuario y contraseña, crea o reutiliza el token y lo entrega solo como cookie HttpOnly: el JSON no lleva el token, así que el JavaScript de la página no puede leerlo.
    - `me` devuelve usuario, correo, `is_superuser`, `rol` (`superusuario` o el nombre del grupo) y la lista de grupos. `logout` borra el token en el servidor y la cookie, y responde 204.
    - Códigos según el Anexo B: contraseña incorrecta 400, login correcto 200, logout 204, sin sesión 401, falta de CSRF 403.
- **Problema y solución:**
    1. `runserver` fallaba con `Falta DJANGO_SECRET_KEY`: el `.env` no se sube a git y hay que crearlo en cada copia del proyecto. Se copió `.env.example` a `.env`, se generó la clave con Django y se completaron los datos de Oracle.
    2. La carpeta `api/` se creó con la terminal en la raíz del repositorio, así que quedó fuera de `backEnd/veterinaria/` y Django no la encontraba. Se movió con `Move-Item` y se comprobó con `python manage.py check` (0 problemas).
    3. En Postman el login respondía 403: Django exige la cookie `csrftoken` y el header `X-CSRFToken` con el mismo valor, y Postman no estaba enviando las cookies por sí solo. Los mensajes (`CSRF token missing`, `incorrect length`, `CSRF cookie not set`) indicaron cada vez qué faltaba. Se resolvió enviando a mano los headers `X-CSRFToken` y `Cookie`.
    4. El login con la contraseña correcta daba 400 porque el nombre de usuario era `jhon` y no `jhonq`. Se listaron los usuarios con `manage.py shell` y se cambió la contraseña con `changepassword`.
- **Prueba:** en Postman, según el Anexo B: login incorrecto 400, login correcto 200 con la cookie `auth_token` HttpOnly y sin token en el JSON, `me` 200 con el rol, logout 204 y `me` después del logout 401. Además, `Token.objects.count()` desde `manage.py shell` dio 0 tras el logout, lo que confirma que el token se borra en el servidor.
- **Para mis compañeros:** el frontend debe llamar primero a `GET /api/auth/csrf/` para recibir la cookie `csrftoken` y enviar su valor en el header `X-CSRFToken` en cada POST, PUT, PATCH y DELETE (incluido el login). Como `IsAuthenticated` es el permiso por defecto, todas las vistas nuevas quedan protegidas sin código extra, y `me` informa el rol según el grupo de Django, así que los grupos que cree `crear_roles` aparecerán ahí.
- **Próxima semana:** revisión de la Nota 1; después, permisos por rol en las vistas (403) y que el header `Authorization: Token ...` siga funcionando en Postman, como pide la sección 4.1.
- **Uso de IA:** se usó Claude (chat) para generar el código de autenticación (`authentication.py`, `views_auth.py`, `urls.py` y el bloque de `settings.py`) y para guiar las pruebas en Postman y diagnosticar los errores 403. Se cambió el resultado después de leer la pauta (400 en vez de 401, 204 en el logout y el rol en `me`). Cada cambio se comprobó con las peticiones de Postman y con `manage.py check`.