
import requests

from datetime import datetime, timezone


# CLASE: OPEN SKY CLIENT

class OpenSkyClient:

    BASE_URL = "https://opensky-network.org/api/states/all"

    # Coordenadas aproximadas del área de Madrid-Barajas
    AIRPORT_AREAS = {
        "LEMD": {
            "lamin": 40.35,
            "lamax": 40.60,
            "lomin": -3.70,
            "lomax": -3.45
        }
    }

    def __init__(self):

        # Crear una sesión para realizar peticiones HTTP
        self.session = requests.Session()

        self.last_update = None

    def get_flights(self, airport_code="LEMD"):
        """
        Obtiene los estados de las aeronaves situadas
        dentro del área geográfica del aeropuerto.
        Devuelve una lista de aeronaves en formato JSON.
        """
        self.last_update = None
        try:

            # Comprobar que el aeropuerto está definido
            if airport_code not in self.AIRPORT_AREAS:

                print("Código de aeropuerto no disponible.")

                return []

            # Obtener los límites geográficos del aeropuerto
            area = self.AIRPORT_AREAS[airport_code]

            # Realizar la petición a OpenSky
            response = self.session.get(
                self.BASE_URL,
                params=area,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            # Guardar la fecha de actualización de OpenSky
            if data.get("time") is not None:

                self.last_update = datetime.fromtimestamp(
                    data["time"],
                    timezone.utc
                ).isoformat()

            else:

                self.last_update = datetime.now(
                    timezone.utc
                ).isoformat()

            flights = []

            # Comprobar si existen aeronaves disponibles
            if data.get("states") is None:

                return flights

            # Procesar la información de cada aeronave
            for aircraft in data["states"]:

                # Ignorar aeronaves sin posición geográfica
                if aircraft[5] is None or aircraft[6] is None:

                    continue

                flight = {
                    "icao24": aircraft[0],
                    "callsign": aircraft[1].strip() if aircraft[1] else "UNKNOWN",
                    "origin_country": aircraft[2],
                    "longitude": aircraft[5],
                    "latitude": aircraft[6],
                    "altitude": aircraft[7],
                    "on_ground": aircraft[8],
                    "velocity": aircraft[9],
                    "last_contact": aircraft[4]
                }

                flights.append(flight)

            return flights

        except requests.exceptions.RequestException as error:

            print(f"Error de conexión con OpenSky: {error}")

            return []

        except (ValueError, TypeError, KeyError, IndexError) as error:

            print(f"Error al procesar los datos de OpenSky: {error}")

            return []

    def get_last_update(self):
        """
        Devuelve la fecha y hora de actualización de OpenSky
        en formato UTC.
        """

        if self.last_update is None:

            return datetime.now(timezone.utc).isoformat()

        return self.last_update
