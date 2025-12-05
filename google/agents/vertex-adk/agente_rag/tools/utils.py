"""
Funciones utilitarias para las herramientas RAG.
"""

import logging
import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    LOCATION,
    PROJECT_ID,
)

logger = logging.getLogger(__name__)


def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Convierte un nombre de corpus en su nombre de recurso completo si es necesario.
    Maneja varios formatos de entrada y garantiza que el nombre devuelto cumpla
    con los requisitos de Vertex AI.

    Args:
        corpus_name (str): El nombre del corpus o su nombre de visualización

    Returns:
        str: El nombre de recurso completo del corpus
    """
    logger.info(f"Obteniendo el nombre de recurso para el corpus: {corpus_name}")

    # Si ya es un nombre de recurso completo con el formato projects/locations/ragCorpora
    if re.match(r"^projects/[^/]+/locations/[^/]+/ragCorpora/[^/]+$", corpus_name):
        return corpus_name

    # Verifica si este es el nombre de visualización de un corpus existente
    try:
        # Lista todos los corpora y comprueba si hay coincidencias con el nombre de visualización
        corpora = rag.list_corpora()
        for corpus in corpora:
            if hasattr(corpus, "display_name") and corpus.display_name == corpus_name:
                return corpus.name
    except Exception as e:
        logger.warning(f"Error al buscar el nombre de visualización del corpus: {str(e)}")
        # Si no podemos verificar, continuamos con el comportamiento predeterminado
        pass

    # Si contiene elementos de ruta parcial, extrae solo el ID del corpus
    if "/" in corpus_name:
        # Extrae la última parte de la ruta como ID del corpus
        corpus_id = corpus_name.split("/")[-1]
    else:
        corpus_id = corpus_name

    # Elimina caracteres especiales que puedan causar problemas
    corpus_id = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_id)

    # Construye el nombre de recurso estandarizado
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Comprueba si existe un corpus con el nombre dado.

    Args:
        corpus_name (str): El nombre del corpus a verificar
        tool_context (ToolContext): El contexto de la herramienta para la gestión de estado

    Returns:
        bool: True si el corpus existe, False en caso contrario
    """
    # Verifica primero en el estado si se proporcionó tool_context
    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True

    try:
        # Obtiene el nombre de recurso completo
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Lista todos los corpora y comprueba si este existe
        corpora = rag.list_corpora()
        for corpus in corpora:
            if (
                corpus.name == corpus_resource_name
                or corpus.display_name == corpus_name
            ):
                # Actualiza el estado
                tool_context.state[f"corpus_exists_{corpus_name}"] = True
                # También establece este como el corpus actual si no hay ninguno definido
                if not tool_context.state.get("current_corpus"):
                    tool_context.state["current_corpus"] = corpus_name
                return True

        return False
    except Exception as e:
        logger.error(f"Error al comprobar si el corpus existe: {str(e)}")
        # Si no podemos comprobar, asumimos que no existe
        return False


def set_current_corpus(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Establece el corpus actual en el estado del contexto de la herramienta.

    Args:
        corpus_name (str): El nombre del corpus a establecer como actual
        tool_context (ToolContext): El contexto de la herramienta para la gestión de estado

    Returns:
        bool: True si el corpus existe y se estableció como actual, False en caso contrario
    """
    # Comprueba primero si el corpus existe
    if check_corpus_exists(corpus_name, tool_context):
        tool_context.state["current_corpus"] = corpus_name
        return True
    return False
