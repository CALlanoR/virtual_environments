# tools/run_sql_query.py

from sqlalchemy import create_engine, text
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd

# --- Configuración de conexión a BigQuery ---
# Reemplaza con tu propio ID de proyecto de Google Cloud
TU_PROYECTO_GCP_ID = "datapath-agent-bigquery-v1" #******************************************************************************
# URI de conexión que indica a SQLAlchemy usar BigQuery y la tabla pública de CitiBike
# bigquery://<dataset>/<table>
db_uri = "bigquery://bigquery-public-data/new_york_citibike"

def get_bigquery_connection():
    # Inicializamos el cliente de BigQuery con nuestro proyecto
    client = bigquery.Client(project=TU_PROYECTO_GCP_ID)
    # Creamos y devolvemos la conexión DB-API compatible con SQLAlchemy
    connection = dbapi.connect(client=client)
    return connection

engine = create_engine(db_uri, creator=get_bigquery_connection)
# -----------------------------------------------------------


# Esta es ahora una función de Python normal, al igual que tus herramientas de RAG.
# El ADK la convertirá en una herramienta automáticamente.
def run_sql_query(query: str) -> str:
    """
    Ejecuta una consulta SQL en una base de datos de BigQuery que contiene datos de viajes de CitiBike en Nueva York
    y devuelve el resultado como una tabla formateada. La consulta debe ser compatible
    con el dialecto SQL de Google BigQuery.

    Args:
        query (str): La consulta SQL completa a ejecutar en BigQuery.

    Returns:
        str: El resultado de la consulta como una tabla de texto (Markdown) o un mensaje de error.
    """
    try:
        with engine.connect() as connection:
            # Usamos text() para asegurar que SQLAlchemy trate el string como SQL literal
            result_proxy = connection.execute(text(query))
            
            # Convertimos el resultado a un DataFrame de Pandas para un formato bonito
            df = pd.DataFrame(result_proxy.fetchall(), columns=result_proxy.keys())
            
            # Si el DataFrame está vacío, devuelve un mensaje
            if df.empty:
                return "La consulta se ejecutó correctamente, pero no devolvió resultados."
            
            # Convertimos el DataFrame a un string (Markdown) para que el LLM lo pueda leer
            return df.to_markdown(index=False)

    except Exception as e:
        # Si hay un error de SQL, devuélvelo para que el agente pueda intentar corregirlo.
        return f"Error al ejecutar la consulta: {e}"