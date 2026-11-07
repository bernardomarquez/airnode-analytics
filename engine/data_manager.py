
import json
import os

from config.settings import CACHE_FILE



# ALMACENAMIENTO DE DATOS DE OPENSKY

def save_aircraft_cache(airport_code, aircraft_states, update_time):
    """
    Guarda los estados de aeronaves recibidos de OpenSky
    en un archivo JSON.
    """

    # Crear el directorio si todavía no existe
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    # Preparar la información que se almacenará
    cache_data = {
        "airport_code": airport_code,
        "last_update": update_time,
        "aircraft_count": len(aircraft_states),
        "aircraft": aircraft_states
    }

    # Guardar los datos en formato JSON
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            cache_data,
            file,
            indent=4,
            ensure_ascii=False
        )
