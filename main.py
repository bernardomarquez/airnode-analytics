
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config.settings import AIRPORT_CODE
from database.repository import (
    initialize_database,
    get_opensky_history_by_range,
    get_aircraft_states_by_range
)
from engine.analytics import (
    classify_aircraft_states,
    calculate_traffic_metrics
)
from engine.map_visualizer import (
    create_historical_aircraft_map,
    open_aircraft_map
)

# SELECCIÓN DEL INTERVALO TEMPORAL

def get_date_range():
    """Solicita fechas locales de Madrid y las convierte a UTC."""

    madrid_timezone = ZoneInfo("Europe/Madrid")

    print("\nINTERVALO DE ANÁLISIS")
    print("--------------------")

    start_input = input("Fecha y hora de inicio (DD/MM/YYYY HH:MM): ")
    end_input = input("Fecha y hora de finalización (DD/MM/YYYY HH:MM): ")

    start_date = datetime.strptime(
        start_input, "%d/%m/%Y %H:%M"
    ).replace(tzinfo=madrid_timezone)

    end_date = datetime.strptime(
        end_input, "%d/%m/%Y %H:%M"
    ).replace(tzinfo=madrid_timezone)

    if start_date > end_date:
        raise ValueError(
            "La fecha de inicio no puede ser posterior a la fecha de finalización."
        )

    return (
        start_date.astimezone(timezone.utc).isoformat(),
        end_date.astimezone(timezone.utc).isoformat()
    )


# EJECUCIÓN PRINCIPAL

def main():
    print("\nAIRNODE ANALYTICS")
    print("========================")

    initialize_database()
    print("\nBase de datos inicializada correctamente.")

    # RECUPERACIÓN DEL HISTÓRICO

    print("\nANÁLISIS HISTÓRICO DE TRÁFICO AÉREO")
    print("----------------------------------")

    try:
        start_date, end_date = get_date_range()

        opensky_history = get_opensky_history_by_range(
            start_date, end_date
        )
        aircraft_history = get_aircraft_states_by_range(
            start_date, end_date
        )

    except ValueError as error:
        print(f"Error en el intervalo temporal: {error}")
        return

    print("\nRESULTADOS DEL ANÁLISIS")
    print("-----------------------")
    print("Aeropuerto:", AIRPORT_CODE)
    print("Capturas recuperadas:", len(opensky_history))
    print("Registros de aeronaves:", len(aircraft_history))

    if not opensky_history:
        print("\nNo existen capturas en el intervalo seleccionado.")
        return


    # INDICADORES DE TRÁFICO

    traffic_metrics = calculate_traffic_metrics(opensky_history)

    print("\nINDICADORES DE TRÁFICO AÉREO")
    print("----------------------------")
    print("Capturas analizadas:", traffic_metrics["total_snapshots"])
    print("Media de aeronaves:", traffic_metrics["average_aircraft"])
    print("Máximo de aeronaves:", traffic_metrics["maximum_aircraft"])
    print("Mínimo de aeronaves:", traffic_metrics["minimum_aircraft"])
    print("Aeronaves en la última captura:", traffic_metrics["latest_aircraft"])

    variation = traffic_metrics["aircraft_variation"]

    if variation is None:
        print("No hay capturas anteriores para comparar.")
    else:
        print("Variación respecto a la captura anterior:", variation, "aeronaves")

    # CLASIFICACIÓN DE LA ÚLTIMA CAPTURA

    latest_snapshot = opensky_history[-1]

    aircraft_states = [
        aircraft for aircraft in aircraft_history
        if aircraft["snapshot_id"] == latest_snapshot["snapshot_id"]
    ]

    classification = classify_aircraft_states(aircraft_states)

    print("\nANÁLISIS OPERACIONAL DE AERONAVES")
    print("--------------------------------")
    print("Aeronaves en vuelo:", len(classification["airborne"]))
    print("Aeronaves en tierra estacionarias:", len(classification["ground_stationary"]))
    print("Aeronaves en tierra en movimiento:", len(classification["ground_moving"]))
    print("Aeronaves con estado desconocido:", len(classification["unknown"]))

    if aircraft_states:
        print("\nAERONAVES DETECTADAS")

        for aircraft in aircraft_states[:10]:
            print(
                aircraft["callsign"],
                "| ICAO24:", aircraft["icao24"],
                "| Latitud:", aircraft["latitude"],
                "| Longitud:", aircraft["longitude"],
                "| Altitud:", aircraft["altitude"], "m",
                "| Velocidad:", aircraft["velocity"], "m/s",
                "| En tierra:", aircraft["on_ground"]
            )
    else:
        print("\nNo hay aeronaves en la última captura.")

    # MAPA HISTÓRICO

    map_file, plotted_aircraft = create_historical_aircraft_map(
        opensky_history,
        aircraft_history
    )

    if map_file:
        print("\nMAPA HISTÓRICO DE AERONAVES")
        print("---------------------------")
        print("Aeronaves representadas en el registro inicial:", plotted_aircraft)
        print("Mapa generado:", map_file)

    print("\nEjecución finalizada correctamente.")

    if map_file:
        open_aircraft_map()


if __name__ == "__main__":
    main()
