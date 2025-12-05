"""
Herramienta para listar todos los corpus RAG disponibles de Vertex AI.
"""

from typing import Dict, List, Union

from vertexai import rag


def list_corpora() -> dict:
    """
    Lista todos los corpus RAG disponibles de Vertex AI.

    Returns:
        dict: Una lista de corpus disponibles y el estado, donde cada corpus contiene:
            - resource_name: El nombre de recurso completo para usar con otras herramientas.
            - display_name: El nombre legible del corpus.
            - create_time: Fecha de creación del corpus.
            - update_time: Fecha de última actualización del corpus.
    """
    try:
        # Obtiene la lista de corpus
        corpora = rag.list_corpora()

        # Procesa la información de los corpus en un formato más manejable
        corpus_info: List[Dict[str, Union[str, int]]] = []
        for corpus in corpora:
            corpus_data: Dict[str, Union[str, int]] = {
                "resource_name": corpus.name,  # Nombre de recurso completo para usar con otras herramientas
                "display_name": corpus.display_name,
                "create_time": (
                    str(corpus.create_time) if hasattr(corpus, "create_time") else ""
                ),
                "update_time": (
                    str(corpus.update_time) if hasattr(corpus, "update_time") else ""
                ),
            }

            corpus_info.append(corpus_data)

        return {
            "status": "success",
            "message": f"Found {len(corpus_info)} available corpora",
            "corpora": corpus_info,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing corpora: {str(e)}",
            "corpora": [],
        }
