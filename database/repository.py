def save_simulation(airport_code, simulation_date,
                    total_flights, assigned_flights,
                    unassigned_flights):
    """
    Guarda los resultados de una simulación
    y devuelve su identificador.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Insertar los resultados de la simulación
        cursor.execute("""
            INSERT INTO simulations (
                airport_code,
                simulation_date,
                total_flights,
                assigned_flights,
                unassigned_flights
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            airport_code,
            simulation_date,
            total_flights,
            assigned_flights,
            unassigned_flights
        ))

        connection.commit()

        # Devolver el identificador generado
        return cursor.lastrowid

    finally:
        connection.close()
