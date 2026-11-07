
# =====================================================
# ANÁLISIS DE RESULTADOS
# =====================================================

def calculate_metrics(results, total_gates):
    """
    Calcula los principales indicadores operativos
    de una simulación aeroportuaria.
    """

    # Obtener los vuelos de la simulación
    assigned_flights = results["assigned"]
    total_flights = results["total_flights"]

    # Calcular el porcentaje de vuelos asignados
    if total_flights > 0:

        assignment_rate = (
            results["assigned_flights"] / total_flights
        ) * 100

    else:
        assignment_rate = 0

    # Calcular la duración total de ocupación de puertas
    total_occupancy_time = 0

    for flight in assigned_flights:

        duration = (
            flight.departure_time - flight.arrival_time
        ).total_seconds() / 60

        total_occupancy_time += duration

    # Calcular el tiempo medio de ocupación por vuelo
    if assigned_flights:

        average_turnaround_time = (
            total_occupancy_time / len(assigned_flights)
        )

    else:
        average_turnaround_time = 0

    # Calcular el intervalo temporal de la simulación
    all_flights = assigned_flights + results["unassigned"]

    if all_flights and total_gates > 0:

        start_time = min(
            flight.arrival_time for flight in all_flights
        )

        end_time = max(
            flight.departure_time for flight in all_flights
        )

        simulation_duration = (
            end_time - start_time
        ).total_seconds() / 60

        # Calcular el porcentaje de utilización de puertas
        available_capacity = total_gates * simulation_duration

        if available_capacity > 0:

            gate_utilization = (
                total_occupancy_time / available_capacity
            ) * 100

        else:
            gate_utilization = 0

    else:
        gate_utilization = 0

    # Preparar los indicadores
    metrics = {
        "assignment_rate": round(assignment_rate, 2),
        "gate_utilization": round(gate_utilization, 2),
        "average_turnaround_time": round(
            average_turnaround_time, 2
        ),
        "unassigned_flights": results["unassigned_flights"]
    }

    return metrics


# COMPARACIÓN ENTRE SIMULACIONES

def compare_simulations(history):
    """
    Compara los indicadores de las dos últimas simulaciones.
    """

    if len(history) < 2:
        return None

    current = history[0]
    previous = history[1]

    # Indicadores que se van a comparar
    metric_names = [
        "assignment_rate",
        "gate_utilization",
        "average_turnaround_time"
    ]

    changes = {}

    for metric in metric_names:

        current_value = current[metric]
        previous_value = previous[metric]

        # Comprobar que ambas simulaciones tienen el indicador
        if current_value is not None and previous_value is not None:
            changes[metric] = round(
                current_value - previous_value,
                2
            )
        else:
            changes[metric] = None

    comparison = {
        "current_id": current["simulation_id"],
        "previous_id": previous["simulation_id"],
        "changes": changes
    }

    return comparison

# CLASIFICACIÓN DE ESTADOS DE AERONAVES

def classify_aircraft_states(aircraft_states):
    """
    Clasifica las aeronaves según su situación operacional.
    """

    classification = {
        "airborne": [],
        "ground_stationary": [],
        "ground_moving": [],
        "unknown": []
    }

    for aircraft in aircraft_states:

        on_ground = aircraft["on_ground"]
        velocity = aircraft["velocity"]

        # Comprobar si la aeronave está en vuelo
        if on_ground is False:

            classification["airborne"].append(aircraft)

        # Comprobar si la aeronave está en tierra
        elif on_ground is True:

            if velocity is not None and velocity > 1.5:

                classification["ground_moving"].append(aircraft)

            else:

                classification["ground_stationary"].append(aircraft)

        # Estado desconocido
        else:

            classification["unknown"].append(aircraft)

    return classification



# INDICADORES DE TRÁFICO AÉREO

def calculate_traffic_metrics(history):
    """
    Calcula indicadores básicos a partir del histórico de OpenSky.
    """

    # Comprobar que existen capturas
    if not history:
        return None

    # Obtener el número de aeronaves de cada captura
    aircraft_counts = [
        snapshot["total_aircraft"]
        for snapshot in history
    ]

    # Calcular indicadores generales
    total_snapshots = len(history)
    average_aircraft = sum(aircraft_counts) / total_snapshots
    maximum_aircraft = max(aircraft_counts)
    minimum_aircraft = min(aircraft_counts)

    # Obtener los datos de las dos últimas capturas
    latest_aircraft = history[0]["total_aircraft"]

    if total_snapshots > 1:
        previous_aircraft = history[1]["total_aircraft"]
        aircraft_variation = latest_aircraft - previous_aircraft
    else:
        aircraft_variation = None

    return {
        "total_snapshots": total_snapshots,
        "average_aircraft": round(average_aircraft, 2),
        "maximum_aircraft": maximum_aircraft,
        "minimum_aircraft": minimum_aircraft,
        "latest_aircraft": latest_aircraft,
        "aircraft_variation": aircraft_variation
    }
