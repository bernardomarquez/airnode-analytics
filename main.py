from airnode.models import Airport, CommercialPassengerFlight
from airnode.processor import fetch_live_airport_traffic
from airnode.exceptions import AirportOperationsError
from datetime import datetime

def main():
    print("==================================================")
    print("    AirNode Analytics - Operational Simulation    ")
    print("==================================================")
    
    # Initialize Hub with strict gate constraints
    hub_name = "Madrid-Barajas (LEMD)"
    max_gates = 5
    mad_airport = Airport(name=hub_name, total_gates=max_gates)
    print(f"-> Initialized hub: {hub_name} (Capacity: {max_gates} gates)")

    print("\n-> Fetching live traffic stream via OpenSky Network API...")
    try:
        flight_stream = fetch_live_airport_traffic("LEMD")
        
        processed_count = 0
        for flight_data in flight_stream:
            # Limit the demo batch for clean console output
            if processed_count >= 5:
                break
                
            flight = CommercialPassengerFlight(
                flight_number=flight_data["flight_number"],
                airline="Commercial Carrier",
                scheduled_time=datetime.now(),
                passengers=flight_data["passengers"],
                aircraft_type=flight_data["aircraft_type"]
            )
            
            # Attempt gate allocation (triggers encapsulation and logic)
            success = mad_airport.assign_gate(flight)
            if success:
                print(f"[SUCCESS] Gate assigned for Flight: {flight.flight_number} | Details: {flight.aircraft_type}")
            else:
                print(f"[WARNING] Gate capacity exceeded for Flight: {flight.flight_number}")
            
            processed_count += 1
            
    except AirportOperationsError as e:
        print(f"[ERROR CAUGHT]: {e}")
    except Exception as e:
        print(f"[UNEXPECTED ERROR]: {e}")

    print("\n==================================================")
    print("            Simulation Run Finished               ")
    print("==================================================")

if __name__ == "__main__":
    main()
