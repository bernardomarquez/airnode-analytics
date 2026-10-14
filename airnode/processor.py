import json
import os
from datetime import datetime
from typing import Any, Dict, Generator
import requests
from airnode.exceptions import AirportOperationsError


def fetch_daily_airport_schedule(
    airport_icao: str = "LEMD",
) -> str:
  """Downloads or retrieves today's live flight schedule for an airport.

  Uses datetime to name files by date, and os to cache them daily.
  """
  today_str = datetime.now().strftime("%Y-%m-%d")
  cache_dir = "data/incoming_schedules"
  cache_file = os.path.join(cache_dir, f"schedule_{airport_icao}_{today_str}.json")

  # Ensure directory exists via os automation
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

  # If cached file for today already exists, use it (prevents API rate-limiting)
  if os.path.exists(cache_file):
    print(f"-> [Cache Hit] Loaded daily schedule for {today_str} from disk.")
    return cache_file

  print(
      f"-> [Live Fetch] Querying live schedule for {airport_icao} on"
      f" {today_str}..."
  )

  # Example using a public aviation endpoint or fallback simulation structure
  # For production portfolio, you can plug in AeroDataBox or Aviationstack here.
  url = f"https://opensky-network.org/api/states/all"

  try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    states = data.get("states", [])
    formatted_flights = []

    for state in states[:50]:  # Capture top 50 active movements for simulation
      callsign = state[1]
      origin = state[2]
      if callsign:
        formatted_flights.append({
            "flight_number": callsign.strip(),
            "airline": "Commercial Carrier",
            "scheduled_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "passengers": 160,
            "aircraft_type": f"Origin: {origin}",
        })

    # Save to local daily file for persistence
    with open(cache_file, "w", encoding="utf-8") as f:
      json.dump(formatted_flights, f, indent=4)

    print(f"-> [Success] Saved fresh daily schedule to {cache_file}")
    return cache_file

  except requests.exceptions.RequestException as e:
    raise AirportOperationsError(
        f"Failed to fetch live daily traffic: {e}", code=502
    )


def stream_daily_flight_schedules(
    airport_icao: str = "LEMD",
) -> Generator[Dict[str, Any], None, None]:
  """Generator that fetches today's live file and yields flights one-by-one

  to prevent memory spikes.
  """
  file_path = fetch_daily_airport_schedule(airport_icao)

  try:
    with open(file_path, "r", encoding="utf-8") as f:
      flights = json.load(f)
      for flight in flights:
        yield flight
  except Exception as e:
    raise AirportOperationsError(f"Error streaming daily schedule: {e}", code=500)
