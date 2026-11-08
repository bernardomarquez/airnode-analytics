
import os
import json
import functools
import http.server
import webbrowser
import html
import folium

from config.settings import OUTPUTS_DIR


# MAPA HISTORICO DE AERONAVES

def create_historical_aircraft_map(opensky_history, aircraft_history):
    """
    Genera un mapa histórico con un slider temporal
    y un panel de estadísticas de aeronaves.
    """

    if not opensky_history:
        print("No hay registros para generar el mapa.")
        return None, 0

    airport_map = folium.Map(
        location=[40.472, -3.560],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # CABECERA PRINCIPAL DEL DASHBOARD

    header_html = """
    <div style="
        position: fixed;
        top: 15px;
        left: 15px;
        width: 395px;
        box-sizing: border-box;
        background-color: white;
        padding: 12px 20px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        z-index: 10000;
        text-align: center;
        font-family: Arial;
        pointer-events: none;
    ">

        <h2 style="
            margin: 0;
            font-size: 22px;
            letter-spacing: 1px;
            color: #333333;
        ">
            AIRNODE ANALYTICS
        </h2>

        <p style="
            margin: 5px 0;
            font-size: 13px;
            color: #555555;
            font-weight: bold;
        ">
            AIR TRAFFIC MONITORING & ANALYTICS
        </p>

        <p style="
            margin: 0;
            font-size: 10px;
            color: #888888;
        ">
            MADRID-BARAJAS AIRPORT (LEMD) |
            OPENSKY NETWORK
        </p>

        <hr style="
            margin: 8px 0 5px 0;
            border: 0;
            border-top: 1px solid #eeeeee;
        ">

        <p style="
            margin: 0;
            font-size: 10px;
            color: #777777;
        ">
            Developed by Bernardo Márquez
        </p>

    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(header_html)
    )

    snapshots = sorted(
        opensky_history,
        key=lambda snapshot: snapshot["captured_at"]
    )

    layers = []
    snapshot_information = []

    # Cargar librería para gráficos
    airport_map.get_root().header.add_child(
        folium.Element(
            '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        )
    )

    # Crear una capa de marcadores por registro
    for index, snapshot in enumerate(snapshots):

        snapshot_id = snapshot["snapshot_id"]
        captured_at = snapshot["captured_at"]

        aircraft_states = [
            aircraft for aircraft in aircraft_history
            if aircraft["snapshot_id"] == snapshot_id
        ]

        aircraft_layer = folium.FeatureGroup(
            name=f"Registro {snapshot_id}",
            show=(index == 0)
        )

        # Contadores de estados
        airborne = 0
        ground_moving = 0
        ground_stationary = 0
        unknown = 0

        for aircraft in aircraft_states:

            latitude = aircraft["latitude"]
            longitude = aircraft["longitude"]

            on_ground = aircraft["on_ground"]
            velocity = aircraft["velocity"]

            # Clasificar la aeronave
            if on_ground is None:
                color = "gray"
                status = "Estado desconocido"
                unknown += 1

            elif not bool(on_ground):
                color = "red"
                status = "En vuelo"
                airborne += 1

            elif velocity is not None and velocity > 1.5:
                color = "blue"
                status = "En tierra, en movimiento"
                ground_moving += 1

            else:
                color = "green"
                status = "En tierra, estacionada"
                ground_stationary += 1

            # Ignorar aeronaves sin posición
            if latitude is None or longitude is None:
                continue

            callsign = html.escape(str(aircraft["callsign"]))
            icao24 = html.escape(str(aircraft["icao24"]))

            altitude = aircraft["altitude"]

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

        snapshot_information.append({
            "date": captured_at,
            "total": len(aircraft_states),
            "airborne": airborne,
            "ground_moving": ground_moving,
            "ground_stationary": ground_stationary,
            "unknown": unknown
        })

    # Referencias para JavaScript
    layer_names = [layer.get_name() for layer in layers]
    layer_references = ", ".join(layer_names)

    information_json = json.dumps(snapshot_information)
    map_name = airport_map.get_name()

    initial = snapshot_information[0]


    # INDICADORES KPI DEL DASHBOARD

    average_aircraft = sum(
        snapshot["total"] for snapshot in snapshot_information
    ) / len(snapshot_information)

    maximum_aircraft = max(
        snapshot["total"] for snapshot in snapshot_information
    )

    total_snapshots = len(snapshot_information)

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
                MEDIA DE AERONAVES
            </span>
            <h2 style="margin: 6px 0; color: #2878B5;">
                {average_aircraft:.1f}
            </h2>
        </div>

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
                MÁXIMO REGISTRADO
            </span>
            <h2 style="margin: 6px 0; color: #299B50;">
                {maximum_aircraft}
            </h2>
        </div>

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
                REGISTROS
            </span>
            <h2 style="margin: 6px 0; color: #7955A1;">
                {total_snapshots}
            </h2>
        </div>

    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(kpi_html)
    )

    # Panel de monitorización
    statistics_html = f"""
    <div style="
        position: fixed;
        top: 15px;
        right: 20px;
        width: 260px;
        background: white;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 15px;
        z-index: 9999;
        font-family: Arial;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    ">
        <h3>AIRNODE ANALYTICS</h3>
        <p style="font-size: 13px; color: gray;">
            MONITORIZACIÓN DE AERONAVES
        </p>
        <hr>

        <span>Aeronaves detectadas</span>
        <h2 id="total-aircraft">{initial["total"]}</h2>

        <p style="color: red;">
            ● En vuelo
            <b id="airborne" style="float: right;">
                {initial["airborne"]}
            </b>
        </p>

        <p style="color: blue;">
            ● En tierra, en movimiento
            <b id="ground-moving" style="float: right;">
                {initial["ground_moving"]}
            </b>
        </p>

        <p style="color: green;">
            ● En tierra, estacionada
            <b id="ground-stationary" style="float: right;">
                {initial["ground_stationary"]}
            </b>
        </p>

        <p style="color: gray;">
            ● Estado desconocido
            <b id="unknown" style="float: right;">
                {initial["unknown"]}
            </b>
        </p>

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

    # Leyenda de colores
    legend_html = """
    <div style="
        position: fixed;
        bottom: 15px;
        left: 15px;
        width: 395px;
        box-sizing: border-box;
        background: white;
        border: 2px solid #cccccc;
        padding: 10px;
        border-radius: 6px;
        z-index: 9999;
        font-family: Arial;
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

    # GRAFICO HISTORICO DE TRAFICO AEREO

    chart_html = """
    <div style="
        position: fixed;
        top: 300px;
        left: 15px;
        width: 395px;
        height: 350px;
        box-sizing: border-box;
        background: white;
        padding: 15px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        z-index: 9998;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
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


    # GRAFICO DE DISTRIBUCION OPERACIONAL

    distribution_html = """
    <div style="
        position: fixed;
        top: 45%;
        right: 15px;
        width: 260px;
        height: 260px;
        background: white;
        padding: 15px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        z-index: 9998;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        font-family: Arial;
    ">

        <b>DISTRIBUCIÓN OPERACIONAL</b>

        <p style="
            font-size: 11px;
            color: gray;
            margin-top: 5px;
        ">
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

    # PANEL DE INTENSIDAD DEL TRAFICO AEREO

    traffic_status_html = """
    <div style="
        position: fixed;
        top: calc(45% + 278px);
        right: 15px;
        width: 260px;
        height: 90px;
        background: white;
        padding: 12px 15px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        z-index: 9998;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        font-family: Arial;
    ">

        <b style="font-size: 13px;">
            NIVEL DE TRÁFICO AÉREO
        </b>

        <h3 id="traffic-level" style="
            margin: 8px 0 4px 0;
            font-size: 17px;
            color: #299B50;
        ">
            TRÁFICO NORMAL
        </h3>

        <p id="traffic-description" style="
            margin: 0;
            font-size: 11px;
            color: gray;
        ">
            Actividad dentro de los niveles habituales
        </p>

    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(traffic_status_html)
    )

    # SLIDER TEMPORAL

    slider_html = f"""
    <div style="
        position: fixed;
        bottom: 15px;
        left: 425px;
        right: 15px;
        width: auto;
        background: white;
        padding: 15px 20px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        z-index: 9999;
        font-family: Arial;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
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


    # CONTROL DEL MAPA, SLIDER Y GRAFICO

    slider_script = f"""
    <script>
    window.addEventListener("load", function() {{

        // Datos del mapa
        const map = {map_name};
        const layers = [{layer_references}];
        const snapshots = {information_json};
        const initial = snapshots[0];
        const slider = document.getElementById("time-slider");

        
        // Clasificacion de intensidad del trafico

        const averageTraffic = snapshots.reduce(
            (sum, snapshot) => sum + snapshot.total,
            0
        ) / snapshots.length;

        function classifyTraffic(total) {{

            const ratio = total / Math.max(averageTraffic, 1);

            if (ratio < 0.75) {{
                return {{
                    level: "TRÁFICO REDUCIDO",
                    description: "Actividad inferior a la media del periodo",
                    color: "#2878B5"
                }};
            }}

            if (ratio <= 1.25) {{
                return {{
                    level: "TRÁFICO NORMAL",
                    description: "Actividad próxima a la media del periodo",
                    color: "#299B50"
                }};
            }}

            if (ratio <= 1.75) {{
                return {{
                    level: "TRÁFICO ELEVADO",
                    description: "Actividad significativamente superior a la media",
                    color: "#E69B23"
                }};
            }}

            return {{
                level: "TRAFICO MUY ELEVADO",
                description: "Actividad muy superior a la media del periodo",
                color: "#D93636"
            }};
        }}

        // Crear grafico historico
        const maxAircraft = Math.max(
            ...snapshots.map(s => s.total),
            1
        );

        const chart = new Chart(
            document.getElementById("traffic-chart"),
            {{
                type: "bar",

                data: {{
                    labels: snapshots.map(s =>
                        s.date.replace("T", " ").substring(0, 16)
                    ),

                    datasets: [
                        {{
                            label: "En vuelo",
                            data: snapshots.map(s => s.airborne),
                            backgroundColor: "red",
                            stack: "aircraft",
                            order: 2
                        }},
                        {{
                            label: "En movimiento",
                            data: snapshots.map(s => s.ground_moving),
                            backgroundColor: "blue",
                            stack: "aircraft",
                            order: 2
                        }},
                        {{
                            label: "Estacionadas",
                            data: snapshots.map(s => s.ground_stationary),
                            backgroundColor: "green",
                            stack: "aircraft",
                            order: 2
                        }},
                        {{
                            label: "Desconocidas",
                            data: snapshots.map(s => s.unknown),
                            backgroundColor: "gray",
                            stack: "aircraft",
                            order: 2
                        }},
                        {{
                            type: "line",
                            label: "Total de aeronaves",
                            data: snapshots.map(s => s.total),
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
                                font: {{
                                    size: 10
                                }}
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

        // Crear grafico circular de distribucion operacional

        const stateChart = new Chart(
            document.getElementById("distribution-chart"),
            {{
                type: "doughnut",

                data: {{
                    labels: [
                        "En vuelo",
                        "En movimiento",
                        "Estacionadas",
                        "Desconocidas"
                    ],

                    datasets: [{{
                        data: [
                            initial.airborne,
                            initial.ground_moving,
                            initial.ground_stationary,
                            initial.unknown
                        ],

                        backgroundColor: [
                            "red",
                            "blue",
                            "green",
                            "gray"
                        ],

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
                                font: {{
                                    size: 10
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        );

        
        // Actualizar mapa y estadisticas
        function updateSnapshot(index) {{

            layers.forEach((layer, i) => {{
                if (i === index) {{
                    map.addLayer(layer);
                }} else {{
                    map.removeLayer(layer);
                }}
            }});

            const snapshot = snapshots[index];

            document.getElementById("snapshot-date").textContent =
                snapshot.date.replace("T", " ");

        // Actualizar estado de intensidad del trafico

        const trafficStatus = classifyTraffic(snapshot.total);

        document.getElementById("traffic-level").textContent =
            trafficStatus.level;

        document.getElementById("traffic-level").style.color =
            trafficStatus.color;

        document.getElementById("traffic-description").textContent =
            trafficStatus.description;

            document.getElementById("snapshot-count").textContent =
                "Registro " + (index + 1) + " de " + snapshots.length;

            document.getElementById("total-aircraft").textContent =
                snapshot.total;

            document.getElementById("airborne").textContent =
                snapshot.airborne;

            document.getElementById("ground-moving").textContent =
                snapshot.ground_moving;

            document.getElementById("ground-stationary").textContent =
                snapshot.ground_stationary;

            document.getElementById("unknown").textContent =
                snapshot.unknown;
                
            document.getElementById("panel-date").textContent =
                snapshot.date.replace("T", " ");

            // Actualizar distribucion operacional

            stateChart.data.datasets[0].data = [
                snapshot.airborne,
                snapshot.ground_moving,
                snapshot.ground_stationary,
                snapshot.unknown
            ];

            stateChart.update();
        }}

        slider.addEventListener("input", function() {{
            updateSnapshot(parseInt(this.value));
        }});

        updateSnapshot(0);

    }});
    </script>
    """

    airport_map.get_root().html.add_child(
        folium.Element(slider_script)
    )

    # Guardar mapa
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

    map_url = f"http://127.0.0.1:{server.server_port}/aircraft_map.html"

    print("\nAbriendo mapa de AirNode Analytics...")
    print("Pulsa Ctrl + C para cerrar el servidor.")

    webbrowser.open(map_url)

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServidor de mapas detenido.")

    finally:
        server.server_close()
