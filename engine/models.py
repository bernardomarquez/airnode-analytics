
from datetime import timedelta



# CLASE: FLIGHT

class Flight:

    def __init__(self, flight_number, origin, destination,
                 arrival_time, departure_time, aircraft_type):

        # Información básica del vuelo
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.aircraft_type = aircraft_type

        # Puerta asignada inicialmente
        self.assigned_gate = None

    def get_occupancy_period(self):
        """
        Devuelve el intervalo de tiempo durante
        el cual el vuelo ocupa una puerta.
        """

        return self.arrival_time, self.departure_time

    def __str__(self):

        return f"{self.flight_number}: {self.origin} -> {self.destination}"



# CLASE: GATE

class Gate:

    def __init__(self, gate_id):

        # Identificador de la puerta
        self.gate_id = gate_id

        # Lista de vuelos asignados a esta puerta
        self.assigned_flights = []

    def is_available(self, arrival_time, departure_time, buffer_time=15):
        """
        Comprueba si la puerta está disponible
        durante el intervalo solicitado.
        """

        for flight in self.assigned_flights:

            # Obtener el intervalo del vuelo existente
            existing_start = flight.arrival_time
            existing_end = flight.departure_time

            # Aplicar el margen de separación entre vuelos
            new_start = arrival_time - timedelta(minutes=buffer_time)
            new_end = departure_time + timedelta(minutes=buffer_time)

            # Comprobar si existe solapamiento temporal
            if new_start < existing_end and new_end > existing_start:

                return False

        return True

    def assign_flight(self, flight):
        """
        Asigna un vuelo a esta puerta.
        """

        self.assigned_flights.append(flight)

        flight.assigned_gate = self.gate_id

    def __str__(self):

        return f"Gate {self.gate_id}"


# CLASE: HUB MANAGER

class HubManager:

    def __init__(self, total_gates):

        # Lista de puertas disponibles en el aeropuerto
        self.gates = []

        # Crear las puertas del aeropuerto
        for i in range(1, total_gates + 1):

            gate = Gate(i)

            self.gates.append(gate)

    def get_available_gate(self, arrival_time, departure_time, buffer_time=15):
        """
        Devuelve la primera puerta disponible.
        Si no existe ninguna, devuelve None.
        """

        for gate in self.gates:

            # Comprobar disponibilidad de cada puerta
            if gate.is_available(arrival_time, departure_time, buffer_time):

                return gate

        return None

    def get_total_gates(self):
        """
        Devuelve el número total de puertas.
        """

        return len(self.gates)

