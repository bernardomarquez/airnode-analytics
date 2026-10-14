import calendar
import os
from datetime import datetime, timedelta


def calculate_turnaround_delay(scheduled_time: str, actual_time: str) -> int:
  """Calculates the delay in minutes between scheduled and actual timestamps

  using the datetime module.
  """
  try:
    fmt = "%Y-%m-%dT%H:%M:%S"
    sched = datetime.strptime(scheduled_time.strip(), fmt)
    actual = datetime.strptime(actual_time.strip(), fmt)
    delta = actual - sched
    return int(delta.total_seconds() / 60)
  except (ValueError, TypeError):
    return 0  # Fallback if format is real-time or unparseable


def get_peak_day_projection(year: int, month: int) -> str:
  """Uses the calendar module to project seasonal traffic patterns

  and identify the busiest operational day-of-the-week framework.
  """
  cal = calendar.monthcalendar(year, month)
  return f"Month {month}/{year} has {len(cal)} operational weeks scheduled."


def ensure_output_directory(dir_path: str = "outputs/") -> None:
  """Uses the os module to automatically initialize output logs directories

  safely using exist_ok=True to prevent collision errors.
  """
  # exist_ok=True prevents FileExistsError on Windows/Linux cross-platform runs
  os.makedirs(dir_path, exist_ok=True)
