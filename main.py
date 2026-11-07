
from datetime import datetime

from config.settings import AIRPORT_CODE
from engine.models import Flight
from engine.simulation import SimulationEngine

from database.repository import (
    initialize_database,
    save_simulation,
    save_allocations
)


# =====================================================
# DATOS DE PRUEBA
# =====================================================

def create_sample_flights():
    """
    Crea una lista de vuelos ficticios para probar
    el funcionamiento de AirNode Analytics.
    """

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

    return flights


# =====================================================
# EJECUCIÓN PRINCIPAL
# =====================================================

def main():

    print("\n================================")
    print("       AIRNODE ANALYTICS")
    print("================================")

    # Inicializar la base de datos
    initialize_database()

    print("\nBase de datos inicializada correctamente.")

    # Obtener los vuelos de entrada
    flights = create_sample_flights()

    # Crear el motor de simulación
    simulator = SimulationEngine()

    # Ejecutar la simulación
    results = simulator.run_simulation(flights)

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

    # Mostrar los resultados
    print("\nRESULTADOS DE LA SIMULACIÓN")
    print("--------------------------------")

    print("Aeropuerto:", AIRPORT_CODE)
    print("Identificador:", simulation_id)
    print("Total de vuelos:", results["total_flights"])
    print("Vuelos asignados:", results["assigned_flights"])
    print("Vuelos sin asignar:", results["unassigned_flights"])

    # Mostrar las puertas asignadas
    print("\nASIGNACIONES")
    print("--------------------------------")

    for flight in results["assigned"]:

        print(
            flight.flight_number,
            "-> Puerta",
            flight.assigned_gate
        )

    # Mostrar los vuelos sin puerta
    print("\nVUELOS SIN ASIGNAR")
    print("--------------------------------")

    for flight in results["unassigned"]:

        print(flight.flight_number)

    print("\nSimulación finalizada correctamente.")


# Ejecutar el programa
if __name__ == "__main__":
    main()
