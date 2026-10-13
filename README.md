# AirNode Analytics – Airport Capacity & Operations Simulation Engine

>  Python simulation engine designed to analyze airport gate availability, model operational turnaround bottlenecks, and project baseline carbon emission metrics during peak traffic hours.

---

## Business Overview & Value Proposition

Major hub airports face severe congestion and ground-handling constraints. **AirNode Analytics** provides an operational simulation framework for aviation consultants to:
- **Identify Runway & Gate Capacity Bottlenecks:** Detect conflicting flight arrivals before operational failure.
- **Model Ground Handling Dynamics:** Calculate turnaround delays and gate occupancy rates.
- **Track ESG & Sustainability Metrics:** Estimate carbon output based on taxi times and aircraft categories.

---

## Architecture & Core Python Capabilities

This project demonstrates production-ready Python patterns and object-oriented architecture:

- **Object-Oriented Programming (OOP):** Encapsulated models for `Airport`, `Terminal`, `Gate`, and `Flight` hierarchies.
- **Custom Exception Handling:** Robust error domain tree rooted at `AirportOperationsError` to handle schedule conflicts gracefully.
- **Memory-Efficient Data Streaming:** Uses Python `generators` (`yield`) to process large daily schedule CSV logs without memory spikes.
- **Functional Data Processing:** Utilizes `map`, `filter`, and `lambda` functions for quick analytical metrics.

---

## Quick Start & Example Usage

```python
from airnode.models import Airport, Flight
from airnode.processor import stream_flight_schedules

# Initialize Airport Hub
mad_airport = Airport(name="Madrid-Barajas (MAD)", total_gates=15)

# Stream incoming flight schedule
for flight in stream_flight_schedules("data/sample_schedule.csv"):
    mad_airport.assign_gate(flight)
