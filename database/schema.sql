

-- BASE DE DATOS

PRAGMA foreign_keys = ON;


-- TABLE: ROLES
CREATE TABLE IF NOT EXISTS roles (

    role_id INTEGER PRIMARY KEY AUTOINCREMENT,

    role_name TEXT NOT NULL UNIQUE

);



-- TABLE: USERS
CREATE TABLE IF NOT EXISTS users (

    user_id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL,

    role_id INTEGER NOT NULL,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (role_id) REFERENCES roles(role_id)

);


-- TABLE: SIMULATIONS
CREATE TABLE IF NOT EXISTS simulations (

    simulation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    airport_code TEXT NOT NULL,

    simulation_date TEXT NOT NULL,

    total_flights INTEGER DEFAULT 0,

    assigned_flights INTEGER DEFAULT 0,

    unassigned_flights INTEGER DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

);


-- TABLE: ALLOCATIONS
CREATE TABLE IF NOT EXISTS allocations (

    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    simulation_id INTEGER NOT NULL,

    flight_number TEXT NOT NULL,

    gate_id INTEGER NOT NULL,

    arrival_time TEXT NOT NULL,

    departure_time TEXT NOT NULL,

    FOREIGN KEY (simulation_id)
        REFERENCES simulations(simulation_id)

);



-- TABLE: SIMULATION METRICS

CREATE TABLE IF NOT EXISTS simulation_metrics (

    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,

    simulation_id INTEGER NOT NULL UNIQUE,

    assignment_rate REAL DEFAULT 0,

    gate_utilization REAL DEFAULT 0,

    average_turnaround_time REAL DEFAULT 0,

    unassigned_flights INTEGER DEFAULT 0,

    FOREIGN KEY (simulation_id)
        REFERENCES simulations(simulation_id)
);



-- HISTÓRICO DE CAPTURAS DE OPENSKY

CREATE TABLE IF NOT EXISTS opensky_snapshots (

    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,

    airport_code TEXT NOT NULL,

    captured_at TEXT NOT NULL,

    total_aircraft INTEGER DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

);



-- AERONAVES REGISTRADAS EN CADA CAPTURA

CREATE TABLE IF NOT EXISTS aircraft_states (

    state_id INTEGER PRIMARY KEY AUTOINCREMENT,

    snapshot_id INTEGER NOT NULL,

    icao24 TEXT NOT NULL,

    callsign TEXT,

    origin_country TEXT,

    latitude REAL,

    longitude REAL,

    altitude REAL,

    velocity REAL,

    on_ground INTEGER,

    last_contact INTEGER,

    FOREIGN KEY (snapshot_id)
        REFERENCES opensky_snapshots(snapshot_id)
        ON DELETE CASCADE,

    UNIQUE (snapshot_id, icao24)

);



-- ÍNDICES PARA CONSULTAS

CREATE INDEX IF NOT EXISTS idx_snapshots_date
ON opensky_snapshots(captured_at);

CREATE INDEX IF NOT EXISTS idx_aircraft_snapshot
ON aircraft_states(snapshot_id);
