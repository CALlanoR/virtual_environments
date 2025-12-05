"""
Herramienta para eliminar un corpus RAG de Vertex AI cuando ya no se necesita.
"""

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from .utils import check_corpus_exists, get_corpus_resource_name


def delete_corpus(
    corpus_name: str,
    confirm: bool,
    tool_context: ToolContext,
) -> dict:
    """
    Elimina un corpus RAG de Vertex AI cuando ya no se necesita.
    Requiere confirmación para evitar eliminaciones accidentales.

    Args:
        corpus_name (str): El nombre de recurso completo del corpus a eliminar.
                           Preferiblemente utilice el resource_name de los resultados de list_corpora.
        confirm (bool): Debe establecerse en True para confirmar la eliminación.
        tool_context (ToolContext): El contexto de la herramienta.

    Returns:
        dict: Información de estado sobre la operación de eliminación.
    """
    # Comprueba si existe el corpus
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"El corpus '{corpus_name}' no existe",
            "corpus_name": corpus_name,
        }

    # Comprueba si la eliminación está confirmada
    if not confirm:
        return {
            "status": "error",
            "message": "La eliminación requiere confirmación explícita. Establece confirm=True para eliminar este corpus.",
            "corpus_name": corpus_name,
        }

    try:
        # Obtiene el nombre de recurso completo del corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Elimina el corpus
        rag.delete_corpus(corpus_resource_name)

        # Elimina del estado estableciéndolo en False
        state_key = f"corpus_exists_{corpus_name}"
        if state_key in tool_context.state:
            tool_context.state[state_key] = False

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' eliminado correctamente",
            "corpus_name": corpus_name,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al eliminar el corpus: {str(e)}",
            "corpus_name": corpus_name,
        }
