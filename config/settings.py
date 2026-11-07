
import os

# DIRECTORIOS

# Directorio raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Código ICAO del aeropuerto de referencia
AIRPORT_CODE = "LEMD"

# Nombre del aeropuerto
AIRPORT_NAME = "Adolfo Suárez Madrid-Barajas"

# Número de puertas de embarque disponibles
TOTAL_GATES = 10

# Directorios del proyecto

DATA_DIR = os.path.join(BASE_DIR, "data")

CACHE_DIR = os.path.join(DATA_DIR, "incoming_schedules")

DATABASE_DIR = os.path.join(BASE_DIR, "database")

OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")



# ARCHIVOS

# Archivo JSON utilizado para almacenar el caché de vuelos
CACHE_FILE = os.path.join(CACHE_DIR, "flights_cache.json")

# Base de datos SQL
DATABASE_FILE = os.path.join(DATABASE_DIR, "airnode.db")



# PARÁMETROS DE SIMULACIÓN

# Tiempo mínimo entre operaciones consecutivas en una puerta (minutos)
GATE_BUFFER_TIME = 15

# Duración estimada de ocupación de una puerta (minutos)
DEFAULT_TURNAROUND_TIME = 60

