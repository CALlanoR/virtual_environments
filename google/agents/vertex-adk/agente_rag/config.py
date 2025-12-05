"""
Configuración para el Agente RAG.

Estos ajustes son utilizados por las distintas herramientas RAG.
La inicialización de Vertex AI se realiza en __init__.py del paquete.
"""

import os

from dotenv import load_dotenv

# Carga variables de entorno (esto es redundante si se importa __init__.py primero,
# pero se incluye por seguridad al importar config directamente)
load_dotenv()

# Ajustes de Vertex AI
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")

# Ajustes de RAG
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_TOP_K = 3
DEFAULT_DISTANCE_THRESHOLD = 0.5
DEFAULT_EMBEDDING_MODEL = "publishers/google/models/text-embedding-005"
DEFAULT_EMBEDDING_REQUESTS_PER_MIN = 1000
