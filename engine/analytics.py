# ANÁLISIS DE RESULTADOS


def calculate_metrics(results):
    """Calcula los indicadores principales de una simulación."""

    total_flights = results["total_flights"]

    assignment_rate = (
        results["assigned_flights"] / total_flights * 100
        if total_flights > 0 else 0
    )

    return {
        "assignment_rate": round(assignment_rate, 2),
        "unassigned_flights": results["unassigned_flights"]
    }


# COMPARACIÓN ENTRE SIMULACIONES

def compare_simulations(history):
    """Compara la tasa de asignación de las dos simulaciones más recientes."""

    if len(history) < 2:
        return None

    current, previous = history[:2]

    current_rate = current["assignment_rate"]
    previous_rate = previous["assignment_rate"]

    change = (
        round(current_rate - previous_rate, 2)
        if current_rate is not None and previous_rate is not None
        else None
    )

    return {
        "current_id": current["simulation_id"],
        "previous_id": previous["simulation_id"],
        "changes": {
            "assignment_rate": change
        }
    }


# CLASIFICACIÓN DE ESTADOS DE AERONAVES

def classify_aircraft_states(aircraft_states):
    """Clasifica las aeronaves según su estado operacional."""

    classification = {
        "airborne": [],
        "ground_stationary": [],
        "ground_moving": [],
        "unknown": []
    }

    for aircraft in aircraft_states:
        on_ground = aircraft["on_ground"]
        velocity = aircraft["velocity"]

        if on_ground is None:
            status = "unknown"
        elif not bool(on_ground):
            status = "airborne"
        elif velocity is not None and velocity > 1.5:
            status = "ground_moving"
        else:
            status = "ground_stationary"

        classification[status].append(aircraft)

    return classification


# INDICADORES DE TRÁFICO AÉREO

def calculate_traffic_metrics(history):
    """Calcula indicadores básicos del histórico de OpenSky."""

    if not history:
        return None

    aircraft_counts = [
        snapshot["total_aircraft"]
        for snapshot in history
    ]

    latest_aircraft = aircraft_counts[-1]

    return {
        "total_snapshots": len(aircraft_counts),
        "average_aircraft": round(sum(aircraft_counts) / len(aircraft_counts), 2),
        "maximum_aircraft": max(aircraft_counts),
        "minimum_aircraft": min(aircraft_counts),
        "latest_aircraft": latest_aircraft,
        "aircraft_variation": (
            latest_aircraft - aircraft_counts[-2]
            if len(aircraft_counts) > 1 else None
        )
    }
