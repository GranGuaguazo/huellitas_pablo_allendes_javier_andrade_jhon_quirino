# Preparación de la defensa · G02 «Huellitas»

Respuestas cortas a las preguntas tipo de cada semana. Las secciones de las semanas siguientes se agregan a medida que avanza el proyecto.

## 1. Arquitectura hexagonal

_(semana 2)_

## 2. Base de datos y conexión (semana 1)

**¿Por qué las tablas internas de Django no van a Oracle?**

- Las tablas de Django (usuarios, grupos, permisos, sesiones, admin, tokens) las crea y modifica `migrate`. Las tablas del negocio, en cambio, se crean a mano con los scripts de `sql/`, donde controlamos los tipos, las restricciones con nombre (`pk_`, `fk_`, `uq_`, `ck_`), la columna IDENTITY y la columna virtual `subtotal`.
- Si `migrate` corriera sobre Oracle, llenaría el esquema de FreeSQL de cada integrante con más de diez tablas que no son parte del modelo de datos. Además, ese esquema tiene una cuota limitada y puede tener tablas de otros ramos.
- Por eso hay dos bases: `default` (SQLite) para lo interno de Django y `negocio` (Oracle) para la clínica. El router `db_router.py` envía los modelos de la app `veterinaria` a `negocio` y su `allow_migrate` devuelve `False` para esa app, así que `migrate` nunca toca las tablas de Oracle (los modelos usan `managed=False`).

**¿Qué hace NOCACHE en la columna IDENTITY?**

- Una columna IDENTITY usa una secuencia interna. Por defecto Oracle reserva en memoria 20 valores de una vez (CACHE 20) para ser más rápido.
- Si la instancia se reinicia o la secuencia se saca de memoria, los valores reservados que no se usaron se pierden y los `id` saltan (por ejemplo de 7 a 21). En una base compartida como FreeSQL esto pasa a menudo.
- Con `NOCACHE`, Oracle no reserva valores por adelantado: cada `id` se pide al momento, así que los números quedan correlativos. El costo es un poco de rendimiento, que no importa con este volumen de datos.
- Aun con NOCACHE puede quedar un hueco si se hace `ROLLBACK` de un `INSERT`, porque el valor de la secuencia ya se consumió. Una secuencia nunca garantiza ausencia total de huecos.

**¿Por qué `subtotal` es una columna virtual?**

- `subtotal` se define como `GENERATED ALWAYS AS (cantidad * precio_unitario) VIRTUAL`: Oracle lo calcula al leer y no ocupa espacio. Nunca puede quedar desalineado con la cantidad o el precio, y no se puede escribir en ella (Django debe tratarla como solo lectura).

**¿Por qué `detalle_atencion` tiene una clave primaria compuesta?**

- La PK `(atencion_id, servicio_id)` impide repetir el mismo servicio dentro de una atención. Si se aplica dos veces, se aumenta `cantidad`.

**¿Por qué la conexión usa `tcps`?**

- FreeSQL solo acepta conexiones cifradas con TLS en el puerto 2484. Sin `tcps://` en el DSN, el servidor cierra la conexión (`DPY-4011`).
