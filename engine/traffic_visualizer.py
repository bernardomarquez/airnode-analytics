
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from config.settings import OUTPUTS_DIR



# VISUALIZACIÓN DEL HISTÓRICO DE TRÁFICO

def create_traffic_chart(history):
    """
    Genera una gráfica con la evolución del número
    de aeronaves detectadas en las capturas de OpenSky.
    """

    # Comprobar que existen datos históricos
    if not history:
        print("No hay datos para generar la gráfica.")
        return None

    # Ordenar las capturas de más antigua a más reciente
    ordered_history = sorted(
        history,
        key=lambda snapshot: snapshot["captured_at"]
    )

    dates = [
        datetime.fromisoformat(snapshot["captured_at"])
        for snapshot in ordered_history
    ]

    aircraft_counts = [
        snapshot["total_aircraft"]
        for snapshot in ordered_history
    ]

    # Crear la gráfica
    plt.figure(figsize=(10, 5))

    plt.plot(
        dates,
        aircraft_counts,
        marker="o",
        linewidth=2,
        markersize=6
    )

    plt.title("Evolución del tráfico aéreo - Aeropuerto de Madrid-Barajas (LEMD)")
    plt.xlabel("Fecha y hora")
    plt.ylabel("Aeronaves detectadas")

    plt.grid(True, alpha=0.3)

    # Formato de fecha: día/mes/año y hora:minuto
    date_format = mdates.DateFormatter("%d/%m/%Y %H:%M")

    plt.gca().xaxis.set_major_formatter(date_format)

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    # Crear el directorio de salida
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Guardar la gráfica
    output_file = os.path.join(
        OUTPUTS_DIR,
        "traffic_history.png"
    )

    plt.savefig(output_file, dpi=150)

    plt.close()

    return output_file
