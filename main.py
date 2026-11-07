
from datetime import datetime

from config.settings import AIRPORT_CODE, TOTAL_GATES
from engine.models import Flight
from engine.simulation import SimulationEngine
from engine.api_client import OpenSkyClient
from engine.data_manager import save_aircraft_cache
from engine.traffic_visualizer import create_traffic_chart

from engine.map_visualizer import (
    create_aircraft_map,
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
    save_aircraft_snapshot,
    get_opensky_history
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


# EJECUCIÓN PRINCIPAL

def main():

    print("\nAIRNODE ANALYTICS")
    print("========================")

    # Inicializar la base de datos
    initialize_database()

    print("\nBase de datos inicializada correctamente.")



    # OBTENCIÓN DE DATOS REALES DE OPENSKY

    print("\nDATOS EN TIEMPO REAL - OPENSKY")
    print("------------------------------")

    opensky_client = OpenSkyClient()

    aircraft_states = opensky_client.get_flights(AIRPORT_CODE)

    print("Aeronaves recibidas:", len(aircraft_states))

    # Obtener la fecha y hora de actualización
    update_time = opensky_client.get_last_update()

    # Guardar los datos recibidos en JSON
    save_aircraft_cache(
        AIRPORT_CODE,
        aircraft_states,
        update_time
    )

    # Guardar la captura en la base de datos
    snapshot_id = save_aircraft_snapshot(
        AIRPORT_CODE,
        update_time,
        aircraft_states
    )

    print("Captura OpenSky guardada:", snapshot_id)

    # CONSULTA DEL HISTÓRICO DE OPENSKY

    print("\nHISTÓRICO DE TRÁFICO AÉREO")
    print("-------------------------")

    opensky_history = get_opensky_history()

    for snapshot in opensky_history:

        print(
            "Captura:", snapshot["snapshot_id"],
            "| Aeropuerto:", snapshot["airport_code"],
            "| Fecha:", snapshot["captured_at"],
            "| Aeronaves:", snapshot["total_aircraft"]
        )


    # GENERACIÓN DE LA GRÁFICA DE TRÁFICO AÉREO

    chart_file = create_traffic_chart(opensky_history)

    if chart_file is not None:

        print("\nGRÁFICA DE TRÁFICO AÉREO")
        print("------------------------")
        print("Gráfica generada:", chart_file)



    # INDICADORES DE TRÁFICO AÉREO

    print("\nINDICADORES DE TRÁFICO AÉREO")
    print("----------------------------")

    traffic_metrics = calculate_traffic_metrics(opensky_history)

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

    else:
        print("No hay datos históricos disponibles.")




    # GENERACIÓN DEL MAPA DE AERONAVES

    map_file, plotted_aircraft = create_aircraft_map(
        aircraft_states,
        update_time
    )

    print("Aeronaves representadas:", plotted_aircraft)
    print("Mapa generado:", map_file)

    # ANÁLISIS DE ESTADOS DE AERONAVES

    classification = classify_aircraft_states(aircraft_states)

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
        print("No se han recibido datos de aeronaves.")



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


