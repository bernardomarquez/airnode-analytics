

from engine.models import HubManager
from config.settings import TOTAL_GATES, GATE_BUFFER_TIME


# =====================================================
# CLASE: MOTOR DE SIMULACIÓN
# =====================================================

class SimulationEngine:

    def __init__(self):

        # Configuración inicial del aeropuerto
        self.total_gates = TOTAL_GATES
        self.buffer_time = GATE_BUFFER_TIME

        # Administrador de puertas
        self.hub_manager = HubManager(self.total_gates)

    def run_simulation(self, flights):
        """
        Ejecuta la simulación de asignación de vuelos
        a las puertas de embarque disponibles.
        """

        # Reiniciar las puertas para comenzar una nueva simulación
        self.hub_manager = HubManager(self.total_gates)

        # Reiniciar las asignaciones anteriores
        for flight in flights:
            flight.assigned_gate = None

        # Ordenar los vuelos según su hora de llegada
        flights.sort(key=lambda flight: flight.arrival_time)

        assigned_flights = []
        unassigned_flights = []

        # Procesar cada vuelo
        for flight in flights:

            # Buscar una puerta disponible
            gate = self.hub_manager.get_available_gate(
                flight.arrival_time,
                flight.departure_time,
                self.buffer_time
            )

            if gate is not None:

                # Asignar el vuelo a la puerta encontrada
                gate.assign_flight(flight)

                assigned_flights.append(flight)

            else:

                # Registrar el vuelo si no hay puertas disponibles
                unassigned_flights.append(flight)

        # Calcular los resultados de la simulación
        results = {
            "total_flights": len(flights),
            "assigned_flights": len(assigned_flights),
            "unassigned_flights": len(unassigned_flights),
            "assigned": assigned_flights,
            "unassigned": unassigned_flights
        }

        return results
