from airnode.exceptions import AirportOperationsError
from airnode.models import Airport, CommercialPassengerFlight
from airnode.processor import stream_daily_flight_schedules
from airnode.utils import ensure_output_directory, get_peak_day_projection
from datetime import datetime


def main():
  print("==================================================")
  print("    AirNode Analytics - Live Operational Engine   ")
  print("==================================================")

  ensure_output_directory("outputs/")
  ensure_output_directory("data/incoming_schedules/")

  # Initialize Hub
  hub_name = "Madrid-Barajas (LEMD)"
  mad_airport = Airport(name=hub_name, total_gates=10)
  print(f"-> Initialized hub: {hub_name} (Capacity: 10 gates)")

  # Calendar projection
  now = datetime.now()
  print(f"-> Seasonal Outlook: {get_peak_day_projection(now.year, now.month)}")

  print("\n-> Streaming today's live updated flight schedule...")
  try:
    flight_stream = stream_daily_flight_schedules("LEMD")

    success_count = 0
    rejected_count = 0

    for flight_data in flight_stream:
      flight = CommercialPassengerFlight(
          flight_number=flight_data["flight_number"],
          airline=flight_data["airline"],
          scheduled_time=datetime.now(),
          passengers=flight_data["passengers"],
          aircraft_type=flight_data["aircraft_type"],
      )

      # Attempt gate allocation
      assigned = mad_airport.assign_gate(flight)
      if assigned:
        success_count += 1
      else:
        rejected_count += 1

    print(f"\n[SIMULATION RESULTS] For {datetime.now().strftime('%Y-%m-%d')}:")
    print(
        f" - Successfully Docked / Allocated Gates: {success_count} flights"
    )
    print(f" - Gate Bottleneck / Overflow (Rejected): {rejected_count} flights")
    print(
        " - Estimated Carbon Footprint Logged: Active across all docked"
        " aircraft."
    )

  except AirportOperationsError as e:
    print(f"[ERROR CAUGHT]: {e}")
  except Exception as e:
    print(f"[UNEXPECTED ERROR]: {e}")

  print("\n==================================================")
  print("         Daily Live Simulation Complete           ")
  print("==================================================")


if __name__ == "__main__":
  main()
