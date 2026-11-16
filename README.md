# Clínica veterinaria «Huellitas» · G02

Proyecto final de **Back End** (INACAP 2026): backEnd con arquitectura hexagonal en **Django 5.2 LTS** sobre **Oracle 26ai (FreeSQL)**, API REST con **Django REST Framework** y frontend **React + Vite**.

La clínica registra a los dueños, sus mascotas y las atenciones, en las que se aplican uno o más servicios (consulta, vacuna, desparasitación). La entidad principal es **atenciones**, con los estados `agendada → realizada → pagada` y `agendada → cancelada`.

> **Estado del repositorio: Semana 1 · Diseño, base de datos y conexión**


## Estructura del repositorio

Estructura final del proyecto. Lo marcado con *(semana N)* todavía no existe y se agrega en esa semana.

```
huellitas/
├── backEnd/
│   ├── sql/                         01_crear_tablas.sql · 02_datos_ejemplo.sql
│   ├── veterinaria_project/         settings.py · urls.py · db_router.py
│   ├── veterinaria/
│   │   ├── domain/                  CORE: entidades puras y puertos (sin Django)
│   │   │   ├── entities/            un archivo por tabla
│   │   │   └── ports/               un contrato (ABC) por tabla
│   │   ├── application/             casos de uso (reglas R1–R3) y excepciones
│   │   ├── infrastructure/          modelos ORM (managed=False), repositorios, di.py (semana 2)
│   │   ├── api/                     adaptador primario: vistas, serializers, rutas, auth (semana 3)
│   │   └── management/commands/     probar_conexion · crear_roles (semana 3)
│   ├── requirements.txt
│   └── .env.example
├── frontend/                        React + Vite (semana 6)
├── docs/                            modelo, diccionario, bitácora, reparto, defensa · Postman (semana 5)
└── README.md
```

Regla de dependencia: las importaciones apuntan hacia el centro. `api/` e `infrastructure/` conocen a `application/` y `domain/`; `domain/` y `application/` no importan nada de Django.


## Instalación del backEnd (Windows)

1. Crear las tablas en **tu propio esquema** de FreeSQL: abrir el SQL Worksheet de freesql.com y ejecutar, en orden, `backEnd/sql/01_crear_tablas.sql` y `backEnd/sql/02_datos_ejemplo.sql`.
2. Instalar y configurar. El entorno virtual `.venv` se crea en la carpeta `huellitas` (fuera de `backEnd`); los comandos se ejecutan desde `huellitas`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r backEnd\requirements.txt
cd backEnd
```

En Linux/macOS: `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r backEnd/requirements.txt` y `cd backEnd`.

3. Copiar la plantilla (`copy .env.example .env` en Windows, `cp .env.example .env` en Linux/macOS) y completar `backEnd/.env` con tus datos de FreeSQL (host, puerto, service name, usuario y contraseña) y una `DJANGO_SECRET_KEY`. El `.env` nunca se sube a git.

FreeSQL exige conexión con TLS en el puerto 2484. `settings.py` usa `tcps` automáticamente para ese puerto; con `ORACLE_PROTOCOL=tcp` o `tcps` se puede forzar otro protocolo. Escribe la clave entre comillas simples (`DJANGO_SECRET_KEY='...'`), porque puede contener `#` o `$`. Para generar una clave (con el entorno activado):

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. Probar la conexión a Oracle (paso 11 del manual):

```powershell
python manage.py probar_conexion
```

Debe mostrar `Conexión OK`, tu usuario de FreeSQL y las 5 tablas con sus filas. Si dice `Faltan datos de Oracle en backEnd/.env`, revisa el paso 3. Si alguna tabla aparece como `NO EXISTE`, revisa el paso 1.

5. Crear las tablas internas de Django en SQLite (usuarios, permisos, sesiones):

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver localhost:8000
```

**Dos bases de datos.** `default` es SQLite y guarda lo interno de Django (usuarios, grupos, permisos, tokens, admin, sesiones). `negocio` es Oracle y guarda solo las tablas de la clínica. El router `veterinaria_project/db_router.py` envía los modelos de la app `veterinaria` a Oracle y nunca deja que `migrate` toque esas tablas.


## Avance semanal

| Semana | Contenido | Estado |
|---|---|---|
| 1 | Diseño, base de datos Oracle y conexión | ✅ Listo |
| 2 | Capas hexagonales de las entidades maestras | Pendiente |
| 3 | Entidad principal, reglas R1–R3, admin, roles y autenticación | Pendiente |
| 4 | Revisión del backEnd terminado (Nota 1) · tag `nota1` | Pendiente |
| 5 | API RESTful completa, reporte y Postman | Pendiente |
| 6 | Frontend React + Vite | Pendiente |
| 7 | Demostración final y defensa (Nota 2) · tag `nota2` | Pendiente |


## Uso de IA

Se usó un asistente de IA para apoyar la escritura del código y de la documentación. Lo que se le preguntó y lo que el grupo cambió quedan registrados en `docs/bitacora.md` (sección 12 del enunciado).
