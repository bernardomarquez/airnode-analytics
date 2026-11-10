
-- HISTÓRICO DE CAPTURAS DE OPENSKY

CREATE TABLE IF NOT EXISTS opensky_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_code TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    total_aircraft INTEGER DEFAULT 0
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


-- ÍNDICE PARA CONSULTAS HISTÓRICAS

CREATE INDEX IF NOT EXISTS idx_snapshots_date
ON opensky_snapshots(captured_at);
