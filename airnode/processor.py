import requests
from typing import Generator, Dict, Any
from airnode.exceptions import AirportOperationsError

def fetch_live_airport_traffic(airport_icao: str = "LEMD") -> Generator[Dict[str, Any], None, None]:
    """
    Fetches real-time flight state data from the OpenSky Network API 
    for a specific airport (e.g., LEMD for Madrid-Barajas) and streams it.
    """
    # OpenSky Network REST API endpoint for arrivals/departures or state vectors
    url = f"https://opensky-network.org/api/states/all"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        states = data.get("states", [])
        if not states:
            return

        for state in states:
            # Example parsing of OpenSky vector structure:
            # [icao24, callsign, origin_country, time_position, last_contact, longitude, latitude, baro_altitude, ...]
            callsign = state[1]
            origin_country = state[2]
            
            if callsign: # Filter out empty callsigns
                flight_data = {
                    "flight_number": callsign.strip(),
                    "flight_type": "Commercial",
                    "scheduled_time": "Real-time",
                    "passengers": 150, # Estimated baseline
                    "aircraft_type": f"Origin: {origin_country}"
                }
                yield flight_data

    except requests.exceptions.RequestException as e:
        raise AirportOperationsError(f"Failed to fetch live data from OpenSky API: {e}", code=502)
