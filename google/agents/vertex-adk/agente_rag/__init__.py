"""
Agente RAG de Vertex AI

Un paquete para interactuar con las capacidades RAG de Google Cloud Vertex AI.
"""

import os

import vertexai
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

# Obtiene la configuración de Vertex AI desde el entorno
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")

# Inicializa Vertex AI al cargar el paquete
try:
    if PROJECT_ID and LOCATION:
        print(f"Inicializando Vertex AI con project={PROJECT_ID}, location={LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("Inicialización de Vertex AI exitosa")
    else:
        print(
            f"Falta configuración de Vertex AI. PROJECT_ID={PROJECT_ID}, LOCATION={LOCATION}. "
            f"Las herramientas que requieren Vertex AI podrían no funcionar correctamente."
        )
except Exception as e:
    print(f"No se pudo inicializar Vertex AI: {str(e)}")
    print("Por favor, verifica tus credenciales de Google Cloud y la configuración del proyecto.")

# Importa el agente después de completar la inicialización
from . import agent
