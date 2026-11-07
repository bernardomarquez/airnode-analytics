
import os
import functools
import http.server
import webbrowser
import html
import folium
from engine.analytics import classify_aircraft_states
from config.settings import OUTPUTS_DIR



# VISUALIZACIÓN DE AERONAVES EN EL MAPA

def create_aircraft_map(aircraft_states, update_time):
    """
    Genera un mapa interactivo con las posiciones
    de las aeronaves recibidas de OpenSky.
    """

    # Coordenadas aproximadas del aeropuerto de Madrid-Barajas
    airport_location = [40.472, -3.560]

    # Crear el mapa
    airport_map = folium.Map(
        location=airport_location,
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # Clasificar las aeronaves recibidas
    classification = classify_aircraft_states(aircraft_states)

    plotted_aircraft = 0
    aircraft_positions = []

    for aircraft in aircraft_states:

        latitude = aircraft["latitude"]
        longitude = aircraft["longitude"]

        # Ignorar aeronaves sin posición disponible
        if latitude is None or longitude is None:
            continue

        # Obtener información de la aeronave
        callsign = html.escape(str(aircraft["callsign"]))
        icao24 = html.escape(str(aircraft["icao24"]))
        altitude = aircraft["altitude"]
        velocity = aircraft["velocity"]

        # Clasificar el estado operacional
        if aircraft["on_ground"] is False:
            color = "red"
            status = "En vuelo"

        elif aircraft["on_ground"] is True:

            if velocity is not None and velocity > 1.5:
                color = "blue"
                status = "En tierra, en movimiento"
            else:
                color = "green"
                status = "En tierra, estacionada"

        else:
            color = "gray"
            status = "Estado desconocido"

        # Preparar los datos para la ventana informativa
        altitude_text = (
            f"{altitude:.1f} m"
            if altitude is not None else "No disponible"
        )

        velocity_text = (
            f"{velocity:.1f} m/s"
            if velocity is not None else "No disponible"
        )

        # Crear la ventana informativa
        popup_html = f"""
        <div style="width: 220px; font-family: Arial;">
            <h4 style="margin-bottom: 8px;">
                {callsign}
            </h4>

            <table style="width: 100%; font-size: 12px;">
                <tr>
                    <td><b>ICAO24</b></td>
                    <td>{icao24}</td>
                </tr>
                <tr>
                    <td><b>Estado</b></td>
                    <td>{status}</td>
                </tr>
                <tr>
                    <td><b>Altitud</b></td>
                    <td>{altitude_text}</td>
                </tr>
                <tr>
                    <td><b>Velocidad</b></td>
                    <td>{velocity_text}</td>
                </tr>
            </table>
        </div>
        """

        # Añadir el marcador al mapa
        folium.Marker(
            location=[latitude, longitude],
            tooltip=callsign,
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color)
        ).add_to(airport_map)

        aircraft_positions.append([latitude, longitude])
        plotted_aircraft += 1

    # Ajustar automáticamente el zoom a las aeronaves
    if len(aircraft_positions) > 1:
        airport_map.fit_bounds(aircraft_positions)

    # Añadir leyenda al mapa
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 190px;
        background-color: white;
        border: 2px solid #cccccc;
        z-index: 9999;
        padding: 10px;
        border-radius: 6px;
        font-family: Arial;
        font-size: 13px;
    ">

        <b>ESTADO DE LAS AERONAVES</b>
        <hr style="margin: 6px 0;">

        <p style="margin: 5px;">
            <span style="color: red;">●</span>
            En vuelo
        </p>

        <p style="margin: 5px;">
            <span style="color: blue;">●</span>
            En tierra, en movimiento
        </p>

        <p style="margin: 5px;">
            <span style="color: green;">●</span>
            En tierra, estacionada
        </p>

        <p style="margin: 5px;">
            <span style="color: gray;">●</span>
            Estado desconocido
        </p>

    </div>
    """

    airport_map.get_root().html.add_child(
        folium.Element(legend_html)
    )



# PANEL DE ESTADÍSTICAS

    total_aircraft = len(aircraft_states)

    airborne = len(classification["airborne"])
    ground_moving = len(classification["ground_moving"])
    ground_stationary = len(classification["ground_stationary"])
    unknown = len(classification["unknown"])

    # Formatear la fecha y hora de actualización
    formatted_update_time = (
        update_time.replace("T", " ")[:19] + " UTC"
    )


    statistics_html = f"""
    <div style="
        position: fixed;
        top: 15px;
        right: 15px;
        width: 230px;
        background-color: white;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 15px;
        z-index: 9999;
        font-family: Arial;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    ">

        <h3 style="margin-top: 0; margin-bottom: 12px;">
            AIRNODE ANALYTICS
        </h3>

        <p style="font-size: 13px; color: gray;">
            MONITORIZACIÓN DE AERONAVES
        </p>

        <hr>

        <div style="margin-bottom: 12px;">
            <span style="color: gray;">Aeronaves detectadas</span>
            <h2 style="margin: 3px 0;">{total_aircraft}</h2>
        </div>

        <div style="margin-bottom: 8px;">
            <span style="color: red;">●</span>
            En vuelo
            <b style="float: right;">{airborne}</b>
        </div>

        <div style="margin-bottom: 8px;">
            <span style="color: blue;">●</span>
            En tierra, en movimiento
            <b style="float: right;">{ground_moving}</b>
        </div>

        <div style="margin-bottom: 8px;">
            <span style="color: green;">●</span>
            En tierra, estacionaria
            <b style="float: right;">{ground_stationary}</b>
        </div>

        <div style="margin-bottom: 8px;">
            <span style="color: gray;">●</span>
            Estado desconocido
            <b style="float: right;">{unknown}</b>
        </div>

        <hr>

        <p style="font-size: 11px; color: gray; margin-bottom: 8px;">
            Datos proporcionados por OpenSky Network
        </p>

        <hr>

        <p style="font-size: 11px; color: gray; margin-bottom: 0;">
            Última actualización:<br>
            <b>{formatted_update_time}</b>
        </p>

    </div>
    """


    airport_map.get_root().html.add_child(
        folium.Element(statistics_html)
    )



    # Crear el directorio de salida si no existe
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Guardar el mapa
    output_file = os.path.join(
        OUTPUTS_DIR,
        "aircraft_map.html"
    )

    airport_map.save(output_file)

    return output_file, plotted_aircraft




# APERTURA AUTOMÁTICA DEL MAPA

def open_aircraft_map():
    """
    Inicia un servidor local y abre automáticamente
    el mapa de aeronaves en el navegador.
    """

    # Comprobar que el mapa existe
    map_file = os.path.join(
        OUTPUTS_DIR,
        "aircraft_map.html"
    )

    if not os.path.exists(map_file):
        print("Error: no se ha encontrado el archivo del mapa.")
        print("Ruta esperada:", map_file)
        return

    # Configurar el servidor para utilizar la carpeta outputs
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=OUTPUTS_DIR
    )

    # Crear el servidor local
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        handler
    )

    port = server.server_port

    # Construir la dirección del mapa
    map_url = f"http://127.0.0.1:{port}/aircraft_map.html"

    print("\nVISUALIZACIÓN DE AIRNODE ANALYTICS")
    print("---------------------------------")
    print("Archivo encontrado:", map_file)
    print("Abriendo mapa en el navegador...")
    print("Dirección:", map_url)
    print("Pulsa Ctrl + C para cerrar el servidor.")

    # Abrir el navegador
    webbrowser.open(map_url)

    # Mantener activo el servidor
    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServidor de mapas detenido.")

    finally:
        server.server_close()
