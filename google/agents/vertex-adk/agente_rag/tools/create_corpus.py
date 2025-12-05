"""
Herramienta para crear un nuevo corpus RAG en Vertex AI.
"""

import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    DEFAULT_EMBEDDING_MODEL,
)
from .utils import check_corpus_exists


def create_corpus(
    corpus_name: str,
    tool_context: ToolContext,
) -> dict:
    """
    Crea un nuevo corpus RAG de Vertex AI con el nombre especificado.

    Args:
        corpus_name (str): El nombre para el nuevo corpus
        tool_context (ToolContext): El contexto de la herramienta para gestión de estado

    Returns:
        dict: Información de estado sobre la operación
    """
    # Comprueba si el corpus ya existe
    if check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "info",
            "message": f"El corpus '{corpus_name}' ya existe",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }

    try:
        # Limpia el nombre del corpus para usarlo como nombre de pantalla
        display_name = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_name)

        # Configura el modelo de embeddings
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model=DEFAULT_EMBEDDING_MODEL
            )
        )

        # Crea el corpus
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )

        # Actualiza el estado para rastrear la existencia del corpus
        tool_context.state[f"corpus_exists_{corpus_name}"] = True

        # Establece este corpus como el actual
        tool_context.state["current_corpus"] = corpus_name

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' creado correctamente",
            "corpus_name": rag_corpus.name,
            "display_name": rag_corpus.display_name,
            "corpus_created": True,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al crear el corpus: {str(e)}",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }
