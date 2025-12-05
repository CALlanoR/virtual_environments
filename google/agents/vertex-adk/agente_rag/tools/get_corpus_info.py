"""
Herramienta para obtener información detallada sobre un corpus RAG específico.
"""

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from .utils import check_corpus_exists, get_corpus_resource_name


def get_corpus_info(
    corpus_name: str,
    tool_context: ToolContext,
) -> dict:
    """
    Obtiene información detallada sobre un corpus RAG específico, incluidos sus archivos.

    Args:
        corpus_name (str): El nombre de recurso completo del corpus sobre el que obtener información.
                           Preferiblemente utilice el resource_name de los resultados de list_corpora.
        tool_context (ToolContext): El contexto de la herramienta.

    Returns:
        dict: Información sobre el corpus y sus archivos.
    """
    try:
        # Comprueba si existe el corpus
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' no existe",
                "corpus_name": corpus_name,
            }

        # Obtiene el nombre de recurso completo del corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Intenta obtener el nombre de visualización del corpus (si fuera posible)
        corpus_display_name = corpus_name  # Valor predeterminado si no se puede obtener el nombre real

        # Procesa la información de los archivos
        file_details = []
        try:
            # Obtiene la lista de archivos del corpus
            files = rag.list_files(corpus_resource_name)
            for rag_file in files:
                # Obtiene detalles específicos de cada documento
                try:
                    # Extrae el ID del archivo a partir del nombre
                    file_id = rag_file.name.split("/")[-1]

                    file_info = {
                        "file_id": file_id,
                        "display_name": (
                            rag_file.display_name
                            if hasattr(rag_file, "display_name")
                            else ""
                        ),
                        "source_uri": (
                            rag_file.source_uri
                            if hasattr(rag_file, "source_uri")
                            else ""
                        ),
                        "create_time": (
                            str(rag_file.create_time)
                            if hasattr(rag_file, "create_time")
                            else ""
                        ),
                        "update_time": (
                            str(rag_file.update_time)
                            if hasattr(rag_file, "update_time")
                            else ""
                        ),
                    }

                    file_details.append(file_info)
                except Exception:
                    # Si falla con este archivo, continúa con el siguiente
                    continue
        except Exception:
            # Si no se pueden obtener detalles de archivos, continúa sin ellos
            pass

        # Devuelve la información básica del corpus junto con los detalles de archivos
        return {
            "status": "success",
            "message": f"Información del corpus '{corpus_display_name}' recuperada correctamente",
            "corpus_name": corpus_name,
            "corpus_display_name": corpus_display_name,
            "file_count": len(file_details),
            "files": file_details,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener información del corpus: {str(e)}",
            "corpus_name": corpus_name,
        }
