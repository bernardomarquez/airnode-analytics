
import os

from config.settings import BASE_DIR
from database.connection import get_connection


# INICIALIZACIÓN DE LA BASE DE DATOS

def initialize_database():
    """Crea las tablas definidas en schema.sql."""

    schema_path = os.path.join(BASE_DIR, "database", "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    connection = get_connection()

    try:
        connection.executescript(schema)
    finally:
        connection.close()


# ALMACENAMIENTO DE CAPTURAS DE OPENSKY

def save_aircraft_snapshot(airport_code, captured_at, aircraft_states):
    """Guarda una captura de OpenSky y sus aeronaves."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
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

        for aircraft in aircraft_states:
            connection.execute("""
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


# CONSULTA DE AERONAVES POR INTERVALO TEMPORAL

def get_aircraft_states_by_range(start_date, end_date):
    """Recupera las aeronaves registradas entre dos fechas."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
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
        """, (start_date, end_date))

        columns = [column[0] for column in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


# CONSULTA DE CAPTURAS POR INTERVALO TEMPORAL

def get_opensky_history_by_range(start_date, end_date):
    """Recupera las capturas de OpenSky comprendidas entre dos fechas."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                snapshot_id,
                airport_code,
                captured_at,
                total_aircraft
            FROM opensky_snapshots
            WHERE captured_at >= ?
            AND captured_at <= ?
            ORDER BY captured_at ASC
        """, (start_date, end_date))

        columns = [column[0] for column in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()
