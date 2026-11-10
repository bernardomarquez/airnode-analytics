# AirNode Analytics – Análisis del Tráfico Aéreo Aeroportuario

Aplicación desarrollada en Python para recopilar, almacenar y analizar datos históricos del tráfico aéreo en el entorno del aeropuerto Adolfo Suárez Madrid-Barajas (LEMD), utilizando la API de OpenSky Network.

## Descripción del Proyecto

AirNode Analytics proporciona una herramienta de análisis y visualización del tráfico aéreo que permite estudiar la actividad de las aeronaves a lo largo del tiempo.

La aplicación obtiene información sobre el estado de las aeronaves mediante OpenSky Network, almacena las capturas históricas en una base de datos SQLite y genera un panel interactivo para analizar la evolución del tráfico y la distribución de las aeronaves.

### Funcionalidades principales

- **Recopilación de datos en tiempo real:** Obtención periódica de información sobre las aeronaves presentes en el área del aeropuerto mediante la API de OpenSky Network.
- **Almacenamiento histórico:** Registro de capturas y estados individuales de las aeronaves en una base de datos SQLite.
- **Análisis del tráfico aéreo:** Cálculo de indicadores como el número medio, máximo y mínimo de aeronaves, así como las variaciones entre capturas consecutivas.
- **Clasificación de estados operacionales:** Identificación de aeronaves en vuelo, estacionarias en tierra, en movimiento en tierra o con estado desconocido.
- **Mapa histórico interactivo:** Representación geográfica de las aeronaves y visualización de su evolución durante un intervalo temporal seleccionado.
- **Panel de análisis:** Visualización de tendencias del tráfico, distribución de aeronaves e indicadores operacionales mediante gráficos interactivos.

## Arquitectura y Tecnologías

El proyecto sigue una arquitectura modular en Python que separa la adquisición de datos, el almacenamiento, el análisis y la visualización.

### Tecnologías utilizadas

- **Python:** Lenguaje principal de desarrollo.
- **OpenSky Network API:** Fuente de datos sobre el estado de las aeronaves.
- **SQLite:** Almacenamiento local de capturas históricas y registros de aeronaves.
- **Folium:** Generación de mapas geográficos interactivos.
- **HTML, CSS y JavaScript:** Desarrollo de la interfaz del panel de visualización.
- **Chart.js:** Representación gráfica de la evolución del tráfico y la distribución de aeronaves.

### Estructura del proyecto

```text
airnode-analytics/
├── config/
│   └── settings.py
├── database/
│   ├── connection.py
│   ├── repository.py
│   └── schema.sql
├── engine/
│   ├── analytics.py
│   ├── api_client.py
│   └── map_visualizer.py
├── outputs/
├── collector.py
├── main.py
├── README.md
└── requirements.txt