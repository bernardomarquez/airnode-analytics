
import os

from config.settings import BASE_DIR
from database.connection import get_connection


# INICIALIZACIÓN DE LA BASE DE DATOS

def initialize_database():
    """
    Crea las tablas de la base de datos e inserta
    los roles iniciales.
    """

    schema_path = os.path.join(
        BASE_DIR,
        "database",
        "schema.sql"
    )

    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    connection = get_connection()

    try:

        # Crear las tablas definidas en el esquema
        connection.executescript(schema)

        # Insertar los roles iniciales
        connection.execute(
            "INSERT OR IGNORE INTO roles (role_name) VALUES (?)",
            ("admin",)
        )

        connection.execute(
            "INSERT OR IGNORE INTO roles (role_name) VALUES (?)",
            ("analyst",)
        )

        connection.commit()

    finally:
        connection.close()



# GESTIÓN DE SIMULACIONES

def save_simulation(airport_code, simulation_date,
                    total_flights, assigned_flights,
                    unassigned_flights):
    """
    Guarda los resultados generales de una simulación
    y devuelve su identificador.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Insertar los resultados de la simulación
        cursor.execute("""
            INSERT INTO simulations (
                airport_code,
                simulation_date,
                total_flights,
                assigned_flights,
                unassigned_flights
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            airport_code,
            simulation_date,
            total_flights,
            assigned_flights,
            unassigned_flights
        ))

        connection.commit()

        # Devolver el identificador generado
        return cursor.lastrowid

    finally:
        connection.close()



# GESTIÓN DE ASIGNACIONES

def save_allocations(simulation_id, flights):
    """
    Guarda las asignaciones de puertas de una simulación.
    Solo almacena los vuelos que tienen una puerta asignada.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        for flight in flights:

            if flight.assigned_gate is not None:

                cursor.execute("""
                    INSERT INTO allocations (
                        simulation_id,
                        flight_number,
                        gate_id,
                        arrival_time,
                        departure_time
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    simulation_id,
                    flight.flight_number,
                    flight.assigned_gate,
                    flight.arrival_time.isoformat(),
                    flight.departure_time.isoformat()
                ))

        connection.commit()

    finally:
        connection.close()



# GESTIÓN DE INDICADORES OPERATIVOS

def save_metrics(simulation_id, metrics):
    """
    Guarda los indicadores operativos de una simulación.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Insertar los indicadores calculados
        cursor.execute("""
            INSERT INTO simulation_metrics (
                simulation_id,
                assignment_rate,
                gate_utilization,
                average_turnaround_time,
                unassigned_flights
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            simulation_id,
            metrics["assignment_rate"],
            metrics["gate_utilization"],
            metrics["average_turnaround_time"],
            metrics["unassigned_flights"]
        ))

        connection.commit()

    finally:
        connection.close()




# CONSULTA DEL HISTÓRICO DE SIMULACIONES

def get_simulation_history():
    """
    Recupera el histórico de simulaciones y sus indicadores.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                simulations.simulation_id,
                simulations.airport_code,
                simulations.simulation_date,
                simulations.total_flights,
                simulations.assigned_flights,
                simulations.unassigned_flights,
                simulation_metrics.assignment_rate,
                simulation_metrics.gate_utilization,
                simulation_metrics.average_turnaround_time
            FROM simulations
            LEFT JOIN simulation_metrics
                ON simulations.simulation_id =
                   simulation_metrics.simulation_id
            ORDER BY simulations.simulation_id DESC
        """)

        rows = cursor.fetchall()

        # Convertir los resultados en una lista de diccionarios
        columns = [description[0] for description in cursor.description]

        history = []

        for row in rows:
            simulation = dict(zip(columns, row))
            history.append(simulation)

        return history

    finally:
        connection.close()




# ALMACENAMIENTO DE DATOS DE OPENSKY

def save_aircraft_snapshot(airport_code, captured_at, aircraft_states):
    """
    Guarda una captura de OpenSky y las aeronaves detectadas.
    Devuelve el identificador de la captura almacenada.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Guardar la información general de la captura
        cursor.execute("""
            INSERT INTO opensky_snapshots (
                airport_code,
                captured_at,
                total_aircraft
            )
            VALUES (?, ?, ?)
        """, (
            airport_code,
            captured_at,
            len(aircraft_states)
        ))

        snapshot_id = cursor.lastrowid

        # Guardar las aeronaves correspondientes a la captura
        for aircraft in aircraft_states:

            cursor.execute("""
                INSERT INTO aircraft_states (
                    snapshot_id,
                    icao24,
                    callsign,
                    origin_country,
                    latitude,
                    longitude,
                    altitude,
                    velocity,
                    on_ground,
                    last_contact
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                aircraft["icao24"],
                aircraft["callsign"],
                aircraft["origin_country"],
                aircraft["latitude"],
                aircraft["longitude"],
                aircraft["altitude"],
                aircraft["velocity"],
                aircraft["on_ground"],
                aircraft["last_contact"]
            ))

        connection.commit()

        return snapshot_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# CONSULTA DEL HISTÓRICO DE OPENSKY

def get_opensky_history(limit=10):
    """
    Recupera las últimas capturas de OpenSky.
    Devuelve una lista de diccionarios.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                snapshot_id,
                airport_code,
                captured_at,
                total_aircraft
            FROM opensky_snapshots
            ORDER BY captured_at DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        # Convertir los resultados en diccionarios
        columns = [
            description[0]
            for description in cursor.description
        ]

        history = []

        for row in rows:
            snapshot = dict(zip(columns, row))
            history.append(snapshot)

        return history

    finally:
        connection.close()

# CONSULTA DE AERONAVES POR INTERVALO TEMPORAL

def get_aircraft_states_by_range(start_date, end_date):
    """
    Recupera las aeronaves registradas en las capturas
    de OpenSky comprendidas entre dos fechas y horas.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                opensky_snapshots.snapshot_id,
                opensky_snapshots.captured_at,
                opensky_snapshots.airport_code,
                aircraft_states.icao24,
                aircraft_states.callsign,
                aircraft_states.origin_country,
                aircraft_states.latitude,
                aircraft_states.longitude,
                aircraft_states.altitude,
                aircraft_states.velocity,
                aircraft_states.on_ground,
                aircraft_states.last_contact

            FROM aircraft_states

            INNER JOIN opensky_snapshots
                ON aircraft_states.snapshot_id =
                   opensky_snapshots.snapshot_id

            WHERE opensky_snapshots.captured_at >= ?
            AND opensky_snapshots.captured_at <= ?

            ORDER BY
                opensky_snapshots.captured_at ASC,
                aircraft_states.icao24 ASC
        """, (
            start_date,
            end_date
        ))

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        aircraft_history = []

        for row in rows:
            aircraft = dict(zip(columns, row))
            aircraft_history.append(aircraft)

        return aircraft_history

    finally:
        connection.close()