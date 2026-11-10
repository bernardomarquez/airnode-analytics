
import time

from config.settings import AIRPORT_CODE, COLLECTION_INTERVAL
from engine.api_client import OpenSkyClient
from database.repository import initialize_database, save_aircraft_snapshot


def collect_data(client):
    """Consulta OpenSky y guarda una captura en SQLite."""

    print("\nConsultando datos de OpenSky...")

    aircraft_states = client.get_flights(AIRPORT_CODE)

    if client.last_update is None:
        print("No se ha podido obtener información de OpenSky.")
        return

    update_time = client.get_last_update()

    snapshot_id = save_aircraft_snapshot(
        AIRPORT_CODE,
        update_time,
        aircraft_states
    )

    print("Captura guardada correctamente.")
    print("Identificador:", snapshot_id)
    print("Aeronaves detectadas:", len(aircraft_states))
    print("Fecha de captura:", update_time)


def run_collector():
    """Ejecuta la recopilación periódica de datos."""

    print("AIRNODE ANALYTICS - DATA COLLECTOR")
    print("==================================")

    initialize_database()

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
