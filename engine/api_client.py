
import requests

from datetime import datetime, timezone


class OpenSkyClient:
    """Cliente para obtener datos de aeronaves desde OpenSky."""

    BASE_URL = "https://opensky-network.org/api/states/all"

    AIRPORT_AREAS = {
        "LEMD": {
            "lamin": 40.35,
            "lamax": 40.60,
            "lomin": -3.70,
            "lomax": -3.45
        }
    }

    def __init__(self):
        self.session = requests.Session()
        self.last_update = None

    def get_flights(self, airport_code="LEMD"):
        """Obtiene las aeronaves dentro del área del aeropuerto."""

        self.last_update = None

        if airport_code not in self.AIRPORT_AREAS:
            print("Código de aeropuerto no disponible.")
            return []

        try:
            response = self.session.get(
                self.BASE_URL,
                params=self.AIRPORT_AREAS[airport_code],
                timeout=20
            )
            response.raise_for_status()

            data = response.json()

            timestamp = data.get("time")

            self.last_update = (
                datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
                if timestamp is not None
                else datetime.now(timezone.utc).isoformat()
            )

            flights = []

            for aircraft in data.get("states") or []:

                if aircraft[5] is None or aircraft[6] is None:
                    continue

                flights.append({
                    "icao24": aircraft[0],
                    "callsign": aircraft[1].strip() if aircraft[1] else "UNKNOWN",
                    "origin_country": aircraft[2],
                    "longitude": aircraft[5],
                    "latitude": aircraft[6],
                    "altitude": aircraft[7],
                    "on_ground": aircraft[8],
                    "velocity": aircraft[9],
                    "last_contact": aircraft[4]
                })

            return flights

        except requests.exceptions.RequestException as error:
            print(f"Error de conexión con OpenSky: {error}")

        except (ValueError, TypeError, KeyError, IndexError) as error:
            print(f"Error al procesar los datos de OpenSky: {error}")

        return []

    def get_last_update(self):
        """Devuelve la última actualización en formato UTC."""

        return self.last_update or datetime.now(timezone.utc).isoformat()
