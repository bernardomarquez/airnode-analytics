
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config.settings import AIRPORT_CODE, TOTAL_GATES
from engine.models import Flight
from engine.simulation import SimulationEngine
from engine.traffic_visualizer import create_traffic_chart

from engine.map_visualizer import (
    create_historical_aircraft_map,
    open_aircraft_map
)

from engine.analytics import (
    calculate_metrics,
    compare_simulations,
    classify_aircraft_states,
    calculate_traffic_metrics
)

from database.repository import (
    initialize_database,
    save_simulation,
    save_allocations,
    save_metrics,
    get_simulation_history,
    get_opensky_history_by_range,
    get_aircraft_states_by_range
)

# DATOS DE PRUEBA

# Crear vuelos ficticios para probar la simulación
flights = [

    Flight(
        "IBE123",
        "MAD",
        "LHR",
        datetime(2026, 11, 10, 10, 0),
        datetime(2026, 11, 10, 11, 0),
        "A320"
    ),

    Flight(
        "IBE456",
        "MAD",
        "CDG",
        datetime(2026, 11, 10, 10, 30),
        datetime(2026, 11, 10, 12, 0),
        "A320"
    ),

    Flight(
        "IBE789",
        "MAD",
        "FRA",
        datetime(2026, 11, 10, 11, 30),
        datetime(2026, 11, 10, 12, 30),
        "A321"
    )
]



# SELECCIÓN DEL INTERVALO TEMPORAL

def get_date_range():
    """
    Solicita un intervalo temporal al usuario.
    Convierte las fechas locales de Madrid a UTC.
    """

    airport_timezone = ZoneInfo("Europe/Madrid")

    print("\nINTERVALO DE ANÁLISIS")
    print("--------------------")

    start_input = input(
        "Fecha y hora de inicio (DD/MM/YYYY HH:MM): "
    )

    end_input = input(
        "Fecha y hora de finalización (DD/MM/YYYY HH:MM): "
    )

    start_date = datetime.strptime(
        start_input,
        "%d/%m/%Y %H:%M"
    ).replace(tzinfo=airport_timezone)

    end_date = datetime.strptime(
        end_input,
        "%d/%m/%Y %H:%M"
    ).replace(tzinfo=airport_timezone)

    if start_date > end_date:
        raise ValueError(
            "La fecha de inicio no puede ser posterior "
            "a la fecha de finalización."
        )

    start_date = start_date.astimezone(
        timezone.utc
    ).isoformat()

    end_date = end_date.astimezone(
        timezone.utc
    ).isoformat()

    return start_date, end_date

# EJECUCIÓN PRINCIPAL

def main():

    print("\nAIRNODE ANALYTICS")
    print("========================")

    # Inicializar la base de datos
    initialize_database()

    print("\nBase de datos inicializada correctamente.")




    # ANÁLISIS HISTÓRICO DE OPENSKY

    print("\nANÁLISIS HISTÓRICO DE TRÁFICO AÉREO")
    print("----------------------------------")

    map_generated = False

    try:

        start_date, end_date = get_date_range()

        # Recuperar las capturas del intervalo
        opensky_history = get_opensky_history_by_range(
            start_date,
            end_date
        )

        # Recuperar las posiciones de las aeronaves
        aircraft_history = get_aircraft_states_by_range(
            start_date,
            end_date
        )

    except ValueError as error:

        print(f"Error en el intervalo temporal: {error}")

        opensky_history = []
        aircraft_history = []

    print("\nRESULTADOS DEL ANÁLISIS")
    print("-----------------------")

    print("Aeropuerto:", AIRPORT_CODE)
    print("Capturas recuperadas:", len(opensky_history))
    print("Registros de aeronaves:", len(aircraft_history))

    if opensky_history:

        # GRÁFICA DE TRÁFICO AÉREO

        chart_file = create_traffic_chart(opensky_history)

        if chart_file is not None:

            print("\nGRÁFICA DE TRÁFICO AÉREO")
            print("-----------------------")
            print("Gráfica generada:", chart_file)

        # INDICADORES DE TRÁFICO AÉREO

        print("\nINDICADORES DE TRÁFICO AÉREO")
        print("----------------------------")

        traffic_metrics = calculate_traffic_metrics(
            opensky_history
        )

        if traffic_metrics is not None:

            print(
                "Capturas analizadas:",
                traffic_metrics["total_snapshots"]
            )

            print(
                "Media de aeronaves:",
                traffic_metrics["average_aircraft"]
            )

            print(
                "Máximo de aeronaves:",
                traffic_metrics["maximum_aircraft"]
            )

            print(
                "Mínimo de aeronaves:",
                traffic_metrics["minimum_aircraft"]
            )

            print(
                "Aeronaves en la última captura:",
                traffic_metrics["latest_aircraft"]
            )

            variation = traffic_metrics["aircraft_variation"]

            if variation is not None:

                print(
                    "Variación respecto a la captura anterior:",
                    variation,
                    "aeronaves"
                )

            else:

                print("No hay capturas anteriores para comparar.")

        # SELECCIONAR LA ÚLTIMA CAPTURA DEL INTERVALO

        latest_snapshot = opensky_history[-1]

        aircraft_states = [
            aircraft
            for aircraft in aircraft_history
            if aircraft["snapshot_id"] == latest_snapshot["snapshot_id"]
        ]

        update_time = latest_snapshot["captured_at"]

        # AGRUPAR AERONAVES POR CAPTURA HISTÓRICA

        aircraft_by_snapshot = {}

        for snapshot in opensky_history:
            snapshot_id = snapshot["snapshot_id"]

            aircraft_by_snapshot[snapshot_id] = [
                aircraft for aircraft in aircraft_history
                if aircraft["snapshot_id"] == snapshot_id
            ]

        print("\nCAPTURAS PREPARADAS PARA EL MAPA HISTÓRICO")
        print("-----------------------------------------")

        for snapshot in opensky_history:
            snapshot_id = snapshot["snapshot_id"]

            print(
                f"Captura {snapshot_id}: "
                f"{len(aircraft_by_snapshot[snapshot_id])} aeronaves"
            )


        # ANÁLISIS OPERACIONAL DE AERONAVES

        classification = classify_aircraft_states(
            aircraft_states
        )

        print("\nANÁLISIS OPERACIONAL DE AERONAVES")
        print("--------------------------------")

        print(
            "Aeronaves en vuelo:",
            len(classification["airborne"])
        )

        print(
            "Aeronaves en tierra estacionarias:",
            len(classification["ground_stationary"])
        )

        print(
            "Aeronaves en tierra en movimiento:",
            len(classification["ground_moving"])
        )

        print(
            "Aeronaves con estado desconocido:",
            len(classification["unknown"])
        )

        # MOSTRAR AERONAVES DE LA ÚLTIMA CAPTURA

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

            # MAPA DE LA ÚLTIMA CAPTURA DEL INTERVALO

            map_file, plotted_aircraft = create_historical_aircraft_map(
                opensky_history,
                aircraft_history
            )

            print("\nMAPA DE AERONAVES")
            print("-----------------")
            print("Aeronaves representadas:", plotted_aircraft)
            print("Mapa generado:", map_file)

            map_generated = True

        else:

            print("\nNo hay aeronaves para representar en el mapa.")

    else:

        print("\nNo existen capturas en el intervalo seleccionado.")



    # Crear el motor de simulación
    simulator = SimulationEngine()

    # Ejecutar la simulación
    results = simulator.run_simulation(flights)

    # Calcular los indicadores operativos
    metrics = calculate_metrics(results, TOTAL_GATES)

    # Guardar los resultados generales
    simulation_id = save_simulation(
        airport_code=AIRPORT_CODE,
        simulation_date=datetime.now().isoformat(timespec="seconds"),
        total_flights=results["total_flights"],
        assigned_flights=results["assigned_flights"],
        unassigned_flights=results["unassigned_flights"]
    )

    # Guardar las asignaciones de puertas
    save_allocations(
        simulation_id,
        results["assigned"]
    )

    # Guardar los indicadores operativos
    save_metrics(
        simulation_id,
        metrics
    )

    # Mostrar los resultados
    print("\nRESULTADOS DE LA SIMULACIÓN")
    print("---------------------------")

    print("Aeropuerto:", AIRPORT_CODE)
    print("Identificador:", simulation_id)
    print("Total de vuelos:", results["total_flights"])
    print("Vuelos asignados:", results["assigned_flights"])
    print("Vuelos sin asignar:", results["unassigned_flights"])

    # Mostrar las asignaciones
    print("\nASIGNACIONES")

    for flight in results["assigned"]:

        print(
            flight.flight_number,
            "-> Puerta",
            flight.assigned_gate
        )

    # Mostrar los vuelos sin asignar
    print("\nVUELOS SIN ASIGNAR")

    for flight in results["unassigned"]:

        print(flight.flight_number)



    # INDICADORES OPERATIVOS

    print("\nINDICADORES OPERATIVOS")
    print("---------------------------")

    print(
        "Tasa de asignación:",
        metrics["assignment_rate"], "%"
    )

    print(
        "Utilización de puertas:",
        metrics["gate_utilization"], "%"
    )

    print(
        "Tiempo medio de ocupación:",
        metrics["average_turnaround_time"],
        "minutos"
    )

    print(
        "Vuelos sin asignar:",
        metrics["unassigned_flights"]
    )



    # HISTÓRICO DE SIMULACIONES

    print("\nHISTÓRICO DE SIMULACIONES")
    print("---------------------------")

    history = get_simulation_history()

    for simulation in history:
        print(
            "ID:", simulation["simulation_id"],
            "| Aeropuerto:", simulation["airport_code"],
            "| Vuelos:", simulation["total_flights"],
            "| Asignación:", simulation["assignment_rate"],
            "%",
            "| Utilización:", simulation["gate_utilization"],
            "%"
        )

    # COMPARACIÓN ENTRE SIMULACIONES
    print("\nCOMPARACIÓN DE SIMULACIONES")
    print("---------------------------")

    comparison = compare_simulations(history)

    if comparison is not None:

        print(
            "Simulación actual:",
            comparison["current_id"]
        )

        print(
            "Simulación anterior:",
            comparison["previous_id"]
        )

        changes = comparison["changes"]

        print(
            "Variación de la tasa de asignación:",
            changes["assignment_rate"],
            "puntos porcentuales"
        )

        print(
            "Variación de la utilización de puertas:",
            changes["gate_utilization"],
            "puntos porcentuales"
        )

        print(
            "Variación del tiempo medio de ocupación:",
            changes["average_turnaround_time"],
            "minutos"
        )

    else:
        print("No hay suficientes simulaciones para comparar.")


    print("\nSimulación finalizada correctamente.")


    # APERTURA DEL MAPA INTERACTIVO

    open_aircraft_map()

# PUNTO DE ENTRADA

if __name__ == "__main__":
    main()


