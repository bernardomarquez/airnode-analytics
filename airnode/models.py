from datetime import datetime
from airnode.exceptions import GateCapacityExceededError


class Flight:
  """Base class representing a generic aircraft movement."""

  def __init__(
      self, flight_number: str, airline: str, scheduled_time: datetime
  ):
    self.flight_number = flight_number
    self.airline = airline
    self.scheduled_time = scheduled_time

  def __str__(self):
    return (
        f"Flight {self.flight_number} ({self.airline}) at"
        f" {self.scheduled_time.strftime('%H:%M')}"
    )


class CommercialPassengerFlight(Flight):
  """Subclass representing scheduled commercial passenger operations."""

  def __init__(
      self,
      flight_number: str,
      airline: str,
      scheduled_time: datetime,
      passengers: int,
      aircraft_type: str,
  ):
    super().__init__(flight_number, airline, scheduled_time)
    self.passengers = passengers
    self.aircraft_type = aircraft_type
    
    # Encapsulated carbon footprint attribute (private via name mangling)
    self.__carbon_emissions_kg = self._calculate_baseline_emissions()

  def _calculate_baseline_emissions(self) -> float:
    """Estimates baseline carbon output based on passenger load and type."""
    return round(self.passengers * 95.5, 2)  # ESG metric approximation

  def get_carbon_footprint(self) -> float:
    """Getter to safely access private ESG data (Encapsulation principle)."""
    return self.__carbon_emissions_kg


class Airport:
  """Represents an airport hub managing terminal gates and capacity."""

  def __init__(self, name: str, total_gates: int):
    self.name = name
    self.__total_gates = total_gates  # Private attribute
    self.__assigned_flights = []

  def assign_gate(self, flight: Flight) -> bool:
    """Attempts to allocate a gate to an incoming flight."""
    if len(self.__assigned_flights) >= self.__total_gates:
      return False

    self.__assigned_flights.append(flight)
    return True

  def get_active_gate_count(self) -> int:
    return len(self.__assigned_flights)
