

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

