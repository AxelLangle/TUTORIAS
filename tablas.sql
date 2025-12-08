CREATE TABLE IF NOT EXISTS asesorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido_p TEXT NOT NULL,
    apellido_m TEXT NOT NULL,
    unidad TEXT NOT NULL,
    parcial TEXT NOT NULL,
    periodo TEXT NOT NULL,
    tema TEXT NOT NULL,
    fecha TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tutorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido_p TEXT NOT NULL,
    apellido_m TEXT NOT NULL,
    matricula TEXT NOT NULL,
    cuatrimestre TEXT NOT NULL,
    motivo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    descripcion TEXT,
    observaciones TEXT,
    seguimiento TEXT
);

CREATE TABLE IF NOT EXISTS tutorias_grupales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo TEXT NOT NULL,
    cuatrimestre TEXT NOT NULL,
    motivo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    descripcion TEXT,
    observaciones TEXT,
    seguimiento TEXT
);


