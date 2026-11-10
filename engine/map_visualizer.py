import os
import json
import functools
import http.server
import webbrowser
import html

from collections import defaultdict

import folium

from config.settings import OUTPUTS_DIR
from engine.analytics import classify_aircraft_states


# CONFIGURACIÓN DE LOS ESTADOS DE LAS AERONAVES

AIRCRAFT_STATES = {
    "airborne": ("red", "En vuelo"),
    "ground_moving": ("blue", "En tierra, en movimiento"),
    "ground_stationary": ("green", "En tierra, estacionada"),
    "unknown": ("gray", "Estado desconocido")
}


# PREPARACIÓN DE LOS DATOS HISTÓRICOS

def prepare_snapshot_data(opensky_history, aircraft_history):
    """Agrupa las aeronaves por captura y calcula sus estadísticas."""

    snapshots = sorted(
        opensky_history,
        key=lambda snapshot: snapshot["captured_at"]
    )

    aircraft_by_snapshot = defaultdict(list)

    for aircraft in aircraft_history:
        aircraft_by_snapshot[aircraft["snapshot_id"]].append(aircraft)

    status_by_aircraft = {}
    snapshot_information = []

    for snapshot in snapshots:
        snapshot_id = snapshot["snapshot_id"]
        aircraft_states = aircraft_by_snapshot[snapshot_id]
        classification = classify_aircraft_states(aircraft_states)

        counts = {}

        for state, (color, label) in AIRCRAFT_STATES.items():
            aircraft_group = classification[state]
            counts[state] = len(aircraft_group)

            for aircraft in aircraft_group:
                status_by_aircraft[id(aircraft)] = (color, label)

        snapshot_information.append({
            "date": snapshot["captured_at"],
            "total": len(aircraft_states),
            **counts
        })

    return (
        snapshots,
        aircraft_by_snapshot,
        status_by_aircraft,
        snapshot_information
    )

# MAPA HISTÓRICO DE AERONAVES

def create_historical_aircraft_map(opensky_history, aircraft_history):
    """Genera el mapa histórico y el dashboard de monitorización."""

    if not opensky_history:
        print("No hay registros para generar el mapa.")
        return None, 0

    (
        snapshots,
        aircraft_by_snapshot,
        status_by_aircraft,
        snapshot_information
    ) = prepare_snapshot_data(opensky_history, aircraft_history)

    airport_map = folium.Map(
        location=[40.472, -3.560],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # CABECERA PRINCIPAL

    header_html = """
    <div style="
        position: fixed;
        top: 15px;
        left: 15px;
        width: 395px;
        box-sizing: border-box;
        background: white;
        padding: 12px 20px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        z-index: 10000;
        text-align: center;
        font-family: Arial;
        pointer-events: none;
    ">
        <h2 style="margin: 0; font-size: 22px; letter-spacing: 1px; color: #333;">
            AIRNODE ANALYTICS
        </h2>

        <p style="margin: 5px 0; font-size: 13px; color: #555; font-weight: bold;">
            AIR TRAFFIC MONITORING & ANALYTICS
        </p>

        <p style="margin: 0; font-size: 10px; color: #888;">
            MADRID-BARAJAS AIRPORT (LEMD) | OPENSKY NETWORK
        </p>

        <hr style="margin: 8px 0 5px; border: 0; border-top: 1px solid #eee;">

        <p style="margin: 0; font-size: 10px; color: #777;">
            Developed by Bernardo Márquez
        </p>
    </div>
    """

    airport_map.get_root().html.add_child(folium.Element(header_html))

    # CARGA DE CHART.JS

    airport_map.get_root().header.add_child(
        folium.Element(
            '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        )
    )

    # CAPAS DE AERONAVES

    layers = []

    for index, snapshot in enumerate(snapshots):
        snapshot_id = snapshot["snapshot_id"]

        aircraft_layer = folium.FeatureGroup(
            name=f"Registro {snapshot_id}",
            show=(index == 0)
        )

        for aircraft in aircraft_by_snapshot[snapshot_id]:
            latitude = aircraft["latitude"]
            longitude = aircraft["longitude"]

            if latitude is None or longitude is None:
                continue

            color, status = status_by_aircraft[id(aircraft)]

            callsign = html.escape(str(aircraft["callsign"]))
            icao24 = html.escape(str(aircraft["icao24"]))

            altitude = aircraft["altitude"]
            velocity = aircraft["velocity"]

            altitude_text = (
                f"{altitude:.1f} m"
                if altitude is not None else "No disponible"
            )

            velocity_text = (
                f"{velocity:.1f} m/s"
                if velocity is not None else "No disponible"
            )

            popup_html = f"""
            <div style="width: 220px; font-family: Arial;">
                <h4>{callsign}</h4>
                <p><b>ICAO24:</b> {icao24}</p>
                <p><b>Estado:</b> {status}</p>
                <p><b>Altitud:</b> {altitude_text}</p>
                <p><b>Velocidad:</b> {velocity_text}</p>
            </div>
            """

            folium.Marker(
                location=[latitude, longitude],
                tooltip=callsign,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(aircraft_layer)

        aircraft_layer.add_to(airport_map)
        layers.append(aircraft_layer)

    # DATOS PARA JAVASCRIPT

    layer_references = ", ".join(
        layer.get_name() for layer in layers
    )

    information_json = json.dumps(snapshot_information)
    map_name = airport_map.get_name()
    initial = snapshot_information[0]

    # INDICADORES KPI

    average_aircraft = sum(
        snapshot["total"] for snapshot in snapshot_information
    ) / len(snapshot_information)

    maximum_aircraft = max(
        snapshot["total"] for snapshot in snapshot_information
    )

    kpi_html = f"""
    <div style="
        position: fixed;
        top: 160px;
        left: 15px;
        width: 395px;
        box-sizing: border-box;
        display: flex;
        gap: 10px;
        z-index: 9997;
        font-family: Arial;
        pointer-events: none;
    ">
        {"".join(f'''
        <div style="
            flex: 1;
            box-sizing: border-box;
            background: white;
            padding: 12px;
            border: 1px solid #cccccc;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        ">
            <span style="font-size: 11px; color: gray;">
                {label}
            </span>
            <h2 style="margin: 6px 0; color: {color};">
                {value}
            </h2>
        </div>
        ''' for label, value, color in [
            ("MEDIA DE AERONAVES", f"{average_aircraft:.1f}", "#2878B5"),
            ("MÁXIMO REGISTRADO", maximum_aircraft, "#299B50"),
            ("REGISTROS", len(snapshot_information), "#7955A1")
        ])}
    </div>
    """

    airport_map.get_root().html.add_child(folium.Element(kpi_html))


    # ESTILOS COMUNES DEL DASHBOARD

    dashboard_css = """
    <style>
        .dashboard-panel {
            background: white;
            border: 1px solid #cccccc;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            font-family: Arial;
        }

        .dashboard-panel h3 {
            margin-top: 0;
        }
    </style>
    """

    airport_map.get_root().header.add_child(
        folium.Element(dashboard_css)
    )

    # PANEL DE MONITORIZACIÓN

    statistics_html = f"""
    <div class="dashboard-panel" style="
        position: fixed;
        top: 15px;
        right: 20px;
        width: 260px;
        padding: 15px;
        z-index: 9999;
    ">
        <h3>AIRNODE ANALYTICS</h3>

        <p style="font-size: 13px; color: gray;">
            MONITORIZACIÓN DE AERONAVES
        </p>

        <hr>

        <span>Aeronaves detectadas</span>
        <h2 id="total-aircraft">{initial["total"]}</h2>

        {"".join(f'''
        <p style="color: {color};">
            ● {label}
            <b id="{element_id}" style="float: right;">
                {initial[state]}
            </b>
        </p>
        ''' for state, color, label, element_id in [
            ("airborne", "red", "En vuelo", "airborne"),
            ("ground_moving", "blue", "En tierra, en movimiento", "ground-moving"),
            ("ground_stationary", "green", "En tierra, estacionada", "ground-stationary"),
            ("unknown", "gray", "Estado desconocido", "unknown")
        ])}

        <hr>

        <p style="font-size: 11px; color: gray;">
            Datos proporcionados por OpenSky Network
        </p>

        <p style="font-size: 11px;">
            Registro seleccionado:<br>
            <b id="panel-date">{initial["date"]}</b>
        </p>
    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(statistics_html)
    )

    # LEYENDA DE ESTADOS

    legend_html = """
    <div class="dashboard-panel" style="
        position: fixed;
        bottom: 15px;
        left: 15px;
        width: 395px;
        box-sizing: border-box;
        padding: 10px;
        border: 2px solid #cccccc;
        border-radius: 6px;
        z-index: 9999;
        font-size: 13px;
    ">
        <b>ESTADO DE LAS AERONAVES</b>
        <hr>

        <p><span style="color: red;">●</span> En vuelo</p>
        <p><span style="color: blue;">●</span> En movimiento</p>
        <p><span style="color: green;">●</span> Estacionada</p>
        <p><span style="color: gray;">●</span> Desconocido</p>
    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(legend_html)
    )

    # GRÁFICO HISTÓRICO DE TRÁFICO AÉREO

    chart_html = """
    <div class="dashboard-panel" style="
        position: fixed;
        top: 300px;
        left: 15px;
        width: 395px;
        height: 350px;
        box-sizing: border-box;
        padding: 15px;
        z-index: 9998;
    ">
        <b>DISTRIBUCION HISTORICA DEL TRAFICO AEREO</b>

        <div style="width: 100%; height: 305px;">
            <canvas id="traffic-chart"></canvas>
        </div>
    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(chart_html)
    )

    # GRÁFICO DE DISTRIBUCIÓN OPERACIONAL

    distribution_html = """
    <div class="dashboard-panel" style="
        position: fixed;
        top: 45%;
        right: 15px;
        width: 260px;
        height: 260px;
        padding: 15px;
        z-index: 9998;
    ">
        <b>DISTRIBUCIÓN OPERACIONAL</b>

        <p style="font-size: 11px; color: gray; margin-top: 5px;">
            Estado de las aeronaves seleccionadas
        </p>

        <div style="width: 100%; height: 200px;">
            <canvas id="distribution-chart"></canvas>
        </div>
    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(distribution_html)
    )

    # PANEL DE INTENSIDAD DEL TRÁFICO

    traffic_status_html = """
    <div class="dashboard-panel" style="
        position: fixed;
        top: calc(45% + 278px);
        right: 15px;
        width: 260px;
        height: 90px;
        padding: 12px 15px;
        z-index: 9998;
    ">
        <b style="font-size: 13px;">NIVEL DE TRÁFICO AÉREO</b>

        <h3 id="traffic-level" style="
            margin: 8px 0 4px;
            font-size: 17px;
            color: #299B50;
        ">TRÁFICO NORMAL</h3>

        <p id="traffic-description" style="
            margin: 0;
            font-size: 11px;
            color: gray;
        ">Actividad dentro de los niveles habituales</p>
    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(traffic_status_html)
    )

    # SLIDER TEMPORAL

    slider_html = f"""
    <div class="dashboard-panel" style="
        position: fixed;
        bottom: 15px;
        left: 425px;
        right: 15px;
        width: auto;
        padding: 15px 20px;
        z-index: 9999;
    ">
        <b>HISTORIAL DE TRÁFICO AÉREO</b>
        <span id="snapshot-date" style="float: right;"></span>

        <input
            id="time-slider"
            type="range"
            min="0"
            max="{len(snapshots) - 1}"
            value="0"
            step="1"
            style="width: 100%; margin-top: 12px;"
        >

        <div style="display: flex; justify-content: space-between;">
            <span>Primer registro</span>
            <span id="snapshot-count"></span>
            <span>Último registro</span>
        </div>
    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(slider_html)
    )


    # CONTROL DEL MAPA, SLIDER Y GRÁFICOS

    slider_script = f"""
    <script>
    window.addEventListener("load", function() {{

        const map = {map_name};
        const layers = [{layer_references}];
        const snapshots = {information_json};
        const slider = document.getElementById("time-slider");

        const states = [
            ["airborne", "En vuelo", "red"],
            ["ground_moving", "En movimiento", "blue"],
            ["ground_stationary", "Estacionadas", "green"],
            ["unknown", "Desconocidas", "gray"]
        ];

        const stateValues = snapshot => states.map(
            ([key]) => snapshot[key]
        );

        // CLASIFICACIÓN DEL TRÁFICO

        const averageTraffic = snapshots.reduce(
            (sum, snapshot) => sum + snapshot.total, 0
        ) / snapshots.length;

        function classifyTraffic(total) {{
            const ratio = total / Math.max(averageTraffic, 1);

            if (ratio < 0.75) {{
                return ["TRÁFICO REDUCIDO", "Actividad inferior a la media", "#2878B5"];
            }}

            if (ratio <= 1.25) {{
                return ["TRÁFICO NORMAL", "Actividad próxima a la media", "#299B50"];
            }}

            if (ratio <= 1.75) {{
                return ["TRÁFICO ELEVADO", "Actividad superior a la media", "#E69B23"];
            }}

            return ["TRÁFICO MUY ELEVADO", "Actividad muy superior a la media", "#D93636"];
        }}

        // GRÁFICO HISTÓRICO

        const maxAircraft = Math.max(
            ...snapshots.map(snapshot => snapshot.total), 1
        );

        const chart = new Chart(
            document.getElementById("traffic-chart"),
            {{
                type: "bar",
                data: {{
                    labels: snapshots.map(snapshot =>
                        snapshot.date.replace("T", " ").substring(0, 16)
                    ),
                    datasets: [
                        ...states.map(([key, label, color]) => ({{
                            label,
                            data: snapshots.map(snapshot => snapshot[key]),
                            backgroundColor: color,
                            stack: "aircraft",
                            order: 2
                        }})),
                        {{
                            type: "line",
                            label: "Total de aeronaves",
                            data: snapshots.map(snapshot => snapshot.total),
                            borderColor: "black",
                            backgroundColor: "black",
                            borderWidth: 2,
                            pointRadius: 3,
                            tension: 0.2,
                            yAxisID: "yTotal",
                            order: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: "bottom",
                            labels: {{
                                boxWidth: 10,
                                font: {{ size: 10 }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            stacked: true,
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 30,
                                autoSkip: true,
                                maxTicksLimit: 8
                            }}
                        }},
                        y: {{
                            stacked: true,
                            beginAtZero: true,
                            max: maxAircraft,
                            title: {{
                                display: true,
                                text: "Aeronaves"
                            }}
                        }},
                        yTotal: {{
                            beginAtZero: true,
                            max: maxAircraft,
                            display: false
                        }}
                    }}
                }}
            }}
        );

        // GRÁFICO DE DISTRIBUCIÓN OPERACIONAL

        const stateChart = new Chart(
            document.getElementById("distribution-chart"),
            {{
                type: "doughnut",
                data: {{
                    labels: states.map(([, label]) => label),
                    datasets: [{{
                        data: stateValues(snapshots[0]),
                        backgroundColor: states.map(([, , color]) => color),
                        borderWidth: 2,
                        borderColor: "white"
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: "bottom",
                            labels: {{
                                boxWidth: 10,
                                font: {{ size: 10 }}
                            }}
                        }}
                    }}
                }}
            }}
        );

        // ACTUALIZACIÓN DEL REGISTRO SELECCIONADO

        function updateSnapshot(index) {{
            layers.forEach((layer, layerIndex) => {{
                if (layerIndex === index) {{
                    map.addLayer(layer);
                }} else {{
                    map.removeLayer(layer);
                }}
            }});

            const snapshot = snapshots[index];
            const formattedDate = snapshot.date.replace("T", " ");

            document.getElementById("snapshot-date").textContent =
                formattedDate;

            document.getElementById("panel-date").textContent =
                formattedDate;

            document.getElementById("snapshot-count").textContent =
                `Registro ${{index + 1}} de ${{snapshots.length}}`;

            document.getElementById("total-aircraft").textContent =
                snapshot.total;

            const states = [
                ["airborne", "En vuelo", "red", "airborne"],
                ["ground_moving", "En movimiento", "blue", "ground-moving"],
                ["ground_stationary", "Estacionadas", "green", "ground-stationary"],
                ["unknown", "Desconocidas", "gray", "unknown"]
            ];

                document.getElementById(elementId).textContent =
                    snapshot[key];
            }});

            const [level, description, color] =
                classifyTraffic(snapshot.total);

            document.getElementById("traffic-level").textContent = level;
            document.getElementById("traffic-level").style.color = color;

            document.getElementById("traffic-description").textContent =
                description;

            stateChart.data.datasets[0].data = stateValues(snapshot);
            stateChart.update();
        }}

        // CONTROL DEL SLIDER

        slider.addEventListener("input", function() {{
            updateSnapshot(Number(this.value));
        }});

        updateSnapshot(0);
    }});
    </script>
    """

    airport_map.get_root().html.add_child(
        folium.Element(slider_script)
    )

    # GUARDAR MAPA

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    output_file = os.path.join(
        OUTPUTS_DIR,
        "aircraft_map.html"
    )

    airport_map.save(output_file)

    return output_file, initial["total"]


# APERTURA DEL MAPA

def open_aircraft_map():
    """Abre el mapa mediante un servidor local."""

    map_file = os.path.join(
        OUTPUTS_DIR,
        "aircraft_map.html"
    )

    if not os.path.exists(map_file):
        print("No se ha encontrado el archivo del mapa.")
        return

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=OUTPUTS_DIR
    )

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        handler
    )

    map_url = (
        f"http://127.0.0.1:{server.server_port}/aircraft_map.html"
    )

    print("\nAbriendo mapa de AirNode Analytics...")
    print("Pulsa Ctrl + C para cerrar el servidor.")

    webbrowser.open(map_url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor de mapas detenido.")
    finally:
        server.server_close()