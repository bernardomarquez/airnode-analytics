
from datetime import datetime

from engine.models import Flight
from engine.simulation import SimulationEngine


# Crear vuelos de prueba
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


# Crear el motor de simulación
simulator = SimulationEngine()

# Ejecutar la simulación
results = simulator.run_simulation(flights)


# Mostrar resultados
print("\nAIRNODE ANALYTICS")
print("========================")

print("Total de vuelos:", results["total_flights"])

print("Vuelos asignados:", results["assigned_flights"])

print("Vuelos sin asignar:", results["unassigned_flights"])


# Mostrar asignaciones
print("\nASIGNACIONES")

for flight in results["assigned"]:

    print(
        flight.flight_number,
        "-> Puerta",
        flight.assigned_gate
    )


# Mostrar vuelos sin asignación
print("\nVUELOS SIN ASIGNAR")

for flight in results["unassigned"]:

    print(flight.flight_number)

