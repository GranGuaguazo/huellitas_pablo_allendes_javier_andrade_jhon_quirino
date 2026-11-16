-- =====================================================================
--  Clínica veterinaria «Huellitas» · G02
--  Script 02: datos de ejemplo realistas
--  Las fechas de atenciones están en UTC (Chile en verano = UTC-3).
--  Ejecutar DESPUÉS de 01_crear_tablas.sql
-- =====================================================================

-- DUENOS
INSERT INTO duenos (rut, nombre, telefono, email, comuna) VALUES ('12.345.678-5', 'Carolina Muñoz Soto',     '+56 9 8123 4567', 'carolina.munoz@gmail.com',  'Renca');
INSERT INTO duenos (rut, nombre, telefono, email, comuna) VALUES ('15.678.234-3', 'Felipe Rojas Contreras',  '+56 9 7234 5678', 'felipe.rojas@outlook.com',  'Quinta Normal');
INSERT INTO duenos (rut, nombre, telefono, email, comuna) VALUES ('18.234.567-9', 'Javiera Pérez Lagos',     '+56 9 6345 6789', 'javiera.perez@gmail.com',   'Cerro Navia');
INSERT INTO duenos (rut, nombre, telefono, email, comuna) VALUES ('9.876.543-3',  'Luis Fuentes Araya',      '+56 9 5456 7890', 'lfuentes@yahoo.com',        'Renca');
INSERT INTO duenos (rut, nombre, telefono, email, comuna) VALUES ('20.123.456-5', 'Valentina Castro Díaz',   '+56 9 4567 8901', 'vale.castro@gmail.com',     'Independencia');
INSERT INTO duenos (rut, nombre, telefono, email, comuna) VALUES ('16.543.210-K', 'Rodrigo Vergara Pino',    '+56 9 3678 9012', 'rvergara@empresa.cl',       'Quilicura');

-- MASCOTAS
INSERT INTO mascotas (dueno_id, nombre, especie, raza, sexo, fecha_nacimiento) VALUES ((SELECT id FROM duenos WHERE rut='12.345.678-5'), 'Rocky',   'perro',  'Labrador',          'M', DATE '2019-04-12');
INSERT INTO mascotas (dueno_id, nombre, especie, raza, sexo, fecha_nacimiento) VALUES ((SELECT id FROM duenos WHERE rut='12.345.678-5'), 'Mishi',   'gato',   'Doméstico pelo corto','H', DATE '2021-09-03');
INSERT INTO mascotas (dueno_id, nombre, especie, raza, sexo, fecha_nacimiento) VALUES ((SELECT id FROM duenos WHERE rut='15.678.234-3'), 'Canela',  'perro',  'Quiltro',           'H', DATE '2018-01-20');
INSERT INTO mascotas (dueno_id, nombre, especie, raza, sexo, fecha_nacimiento) VALUES ((SELECT id FROM duenos WHERE rut='18.234.567-9'), 'Pelusa',  'conejo', 'Cabeza de león',    'H', DATE '2023-02-14');
INSERT INTO mascotas (dueno_id, nombre, especie, raza, sexo, fecha_nacimiento) VALUES ((SELECT id FROM duenos WHERE rut='9.876.543-3'),  'Thor',    'perro',  'Pastor alemán',     'M', DATE '2020-07-30');
INSERT INTO mascotas (dueno_id, nombre, especie, raza, sexo, fecha_nacimiento) VALUES ((SELECT id FROM duenos WHERE rut='20.123.456-5'), 'Kiwi',    'ave',    'Catita australiana','M', DATE '2022-11-05');

-- SERVICIOS
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('CON-01', 'Consulta general',          'Evaluación clínica completa de la mascota', 18000, 1);
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('VAC-01', 'Vacuna antirrábica',        'Vacuna anual obligatoria',                  12000, 1);
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('VAC-02', 'Vacuna óctuple',            'Vacuna polivalente para perros',            15000, 1);
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('DES-01', 'Desparasitación interna',   'Dosis según peso',                           8500, 1);
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('DES-02', 'Desparasitación externa',   'Pipeta antipulgas y garrapatas',             9500, 1);
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('CIR-01', 'Esterilización',            'Cirugía con anestesia general',             65000, 1);
INSERT INTO servicios (codigo, nombre, descripcion, precio, activo) VALUES ('ECO-01', 'Ecografía abdominal',       'Servicio suspendido temporalmente',         35000, 0);

-- ATENCIONES (fecha en UTC: 13:00 UTC = 10:00 hora de Chile)
INSERT INTO atenciones (mascota_id, fecha, motivo, total, estado) VALUES ((SELECT id FROM mascotas WHERE nombre='Rocky'),  TIMESTAMP '2026-10-05 13:00:00', 'Control anual y vacuna',        30000, 'pagada');
INSERT INTO atenciones (mascota_id, fecha, motivo, total, estado) VALUES ((SELECT id FROM mascotas WHERE nombre='Mishi'),  TIMESTAMP '2026-10-12 15:30:00', 'Desparasitación de rutina',     18000, 'pagada');
INSERT INTO atenciones (mascota_id, fecha, motivo, total, estado) VALUES ((SELECT id FROM mascotas WHERE nombre='Canela'), TIMESTAMP '2026-10-20 14:00:00', 'Esterilización programada',     83000, 'realizada');
INSERT INTO atenciones (mascota_id, fecha, motivo, total, estado) VALUES ((SELECT id FROM mascotas WHERE nombre='Thor'),   TIMESTAMP '2026-11-16 12:00:00', 'Cojea de la pata trasera',      18000, 'agendada');
INSERT INTO atenciones (mascota_id, fecha, motivo, total, estado) VALUES ((SELECT id FROM mascotas WHERE nombre='Kiwi'),   TIMESTAMP '2026-10-28 16:00:00', 'Revisión de plumaje',           18000, 'cancelada');

-- DETALLE_ATENCION (subtotal lo calcula Oracle: columna virtual)
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Control anual y vacuna'),    (SELECT id FROM servicios WHERE codigo='CON-01'), 1, 18000);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Control anual y vacuna'),    (SELECT id FROM servicios WHERE codigo='VAC-01'), 1, 12000);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Desparasitación de rutina'), (SELECT id FROM servicios WHERE codigo='DES-01'), 1,  8500);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Desparasitación de rutina'), (SELECT id FROM servicios WHERE codigo='DES-02'), 1,  9500);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Esterilización programada'), (SELECT id FROM servicios WHERE codigo='CIR-01'), 1, 65000);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Esterilización programada'), (SELECT id FROM servicios WHERE codigo='CON-01'), 1, 18000);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Cojea de la pata trasera'),  (SELECT id FROM servicios WHERE codigo='CON-01'), 1, 18000);
INSERT INTO detalle_atencion (atencion_id, servicio_id, cantidad, precio_unitario) VALUES ((SELECT id FROM atenciones WHERE motivo='Revisión de plumaje'),       (SELECT id FROM servicios WHERE codigo='CON-01'), 1, 18000);

COMMIT;

-- Verificación rápida
SELECT 'duenos' tabla, COUNT(*) filas FROM duenos
UNION ALL SELECT 'mascotas', COUNT(*) FROM mascotas
UNION ALL SELECT 'servicios', COUNT(*) FROM servicios
UNION ALL SELECT 'atenciones', COUNT(*) FROM atenciones
UNION ALL SELECT 'detalle_atencion', COUNT(*) FROM detalle_atencion;
