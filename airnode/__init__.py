"""AirNode Analytics Package.

An aviation consultancy simulation engine for airport capacity, gate
allocation, and traffic analytics.
"""

from airnode.exceptions import (
    AirportOperationsError,
    GateCapacityExceededError,
    InvalidScheduleFormatError,
    RunwayOccupiedError,
)
from airnode.models import Airport, CommercialPassengerFlight, Flight
from airnode.processor import stream_daily_flight_schedules
from airnode.utils import (
    calculate_turnaround_delay,
    ensure_output_directory,
    get_peak_day_projection,
)

__version__ = "1.0.0"
__author__ = "Bernardo Marquez"
