import csv
import os
from typing import Generator, Dict, Any
from airnode.exceptions import InvalidScheduleFormatError

def stream_flight_schedules(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Reads a CSV flight schedule file line by line using a generator 
    to optimize RAM memory when handling massive datasets.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for line_num, row in enumerate(reader, start=2):
            try:
                # Basic data normalization and type conversion
                flight_data = {
                    "flight_number": row["flight_number"].strip(),
                    "flight_type": row["type"].strip(),
                    "scheduled_time": row["scheduled_time"].strip(),
                    "passengers": int(row["passengers"]),
                    "aircraft_type": row["aircraft_type"].strip()
                }
                yield flight_data
                
            except (KeyError, ValueError):
                # Raise custom exception if a row is corrupted or missing fields
                raise InvalidScheduleFormatError(file_path, line_num)
