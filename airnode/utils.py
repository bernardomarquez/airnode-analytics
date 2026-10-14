import calendar
import os
from datetime import datetime


def calculate_turnaround_delay(scheduled_time: str, actual_time: str) -> int:
  """Calcula el retraso en minutos entre horas programadas y reales."""
  try:
    fmt = "%Y-%m-%dT%H:%M:%S"
    sched = datetime.strptime(scheduled_time.strip(), fmt)
    actual = datetime.strptime(actual_time.strip(), fmt)
    delta = actual - sched
    return int(delta.total_seconds() / 60)
  except (ValueError, TypeError):
    return 0


def get_peak_day_projection(year: int, month: int) -> str:
  """Utiliza el módulo calendar para proyectar patrones de tráfico."""
  cal = calendar.monthcalendar(year, month)
  return f"Month {month}/{year} has {len(cal)} operational weeks scheduled."


def ensure_output_directory(dir_path: str = "outputs/") -> None:
  """Crea directorios de salida de forma segura evitando errores si ya existen."""
  # exist_ok=True evita el error FileExistsError en Windows
  os.makedirs(dir_path, exist_ok=True)
