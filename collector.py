import time

from config.settings import AIRPORT_CODE, COLLECTION_INTERVAL

from engine.api_client import OpenSkyClient

from database.repository import (
    initialize_database,
    save_aircraft_snapshot
)


def collect_data(client):
    """
    Consulta OpenSky y guarda una captura en la base de datos.
    """

    print("\nConsultando datos de OpenSky...")

    aircraft_states = client.get_flights(AIRPORT_CODE)

    update_time = client.get_last_update()

    # Comprobar si la consulta se ha realizado correctamente
    if client.last_update is None:

        print("No se ha podido obtener información de OpenSky.")

        return

    # Guardar la captura en SQLite
    snapshot_id = save_aircraft_snapshot(
        AIRPORT_CODE,
        update_time,
        aircraft_states
    )

    print(f"Captura guardada correctamente.")
    print(f"Identificador: {snapshot_id}")
    print(f"Aeronaves detectadas: {len(aircraft_states)}")
    print(f"Fecha de captura: {update_time}")


def run_collector():
    """
    Ejecuta el recopilador de forma continua.
    """

    print("AIRNODE ANALYTICS - DATA COLLECTOR")
    print("==================================")

    # Inicializar la base de datos
    initialize_database()

    # Crear cliente OpenSky
    client = OpenSkyClient()

    print(f"Intervalo de captura: {COLLECTION_INTERVAL} segundos")

    try:

        while True:

            collect_data(client)

            print(
                f"\nPróxima captura en "
                f"{COLLECTION_INTERVAL // 60} minutos."
            )

            time.sleep(COLLECTION_INTERVAL)

    except KeyboardInterrupt:

        print("\nRecopilación interrumpida por el usuario.")

    finally:

        client.session.close()

        print("Conexión cerrada.")


if __name__ == "__main__":

    run_collector()
