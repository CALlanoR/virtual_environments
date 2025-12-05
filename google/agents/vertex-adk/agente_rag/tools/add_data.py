"""
Herramienta para agregar nuevas fuentes de datos a un corpus RAG de Vertex AI.
"""

import re
from typing import List

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
)
from .utils import check_corpus_exists, get_corpus_resource_name


def add_data(
    corpus_name: str,
    paths: List[str],
    tool_context: ToolContext,
) -> dict:
    """
    Agrega nuevas fuentes de datos a un corpus RAG de Vertex AI.

    Args:
        corpus_name (str): El nombre del corpus al que agregar datos. Si está vacío, se usará el corpus actual.
        paths (List[str]): Lista de URLs o rutas GCS para agregar al corpus.
                           Formatos soportados:
                           - Google Drive: "https://drive.google.com/file/d/{FILE_ID}/view"
                           - Google Docs/Sheets/Slides: "https://docs.google.com/{tipo}/d/{FILE_ID}/..."
                           - Google Cloud Storage: "gs://{BUCKET}/{PATH}"
                           Ejemplo: ["https://drive.google.com/file/d/123", "gs://mi_bucket/mi_directorio"]
        tool_context (ToolContext): El contexto de la herramienta

    Returns:
        dict: Información sobre los datos agregados y el estado de la operación
    """
    # Comprueba si el corpus existe
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"El corpus '{corpus_name}' no existe. Por favor, créalo primero usando la herramienta create_corpus.",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Valida las entradas
    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Rutas inválidas: Proporciona una lista de URLs o rutas GCS",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Preprocesa las rutas para validar y convertir URLs de Google Docs al formato de Drive si es necesario
    validated_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (No es una cadena válida)")
            continue

        # Detecta URLs de Google Docs/Sheets/Slides y las convierte al formato de Drive
        docs_match = re.match(
            r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            conversions.append(f"{path} → {drive_url}")
            continue

        # Comprueba rutas de Drive y las normaliza al formato estándar
        drive_match = re.match(
            r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if drive_match:
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} → {drive_url}")
            continue

        # Comprueba rutas GCS
        if path.startswith("gs://"):
            validated_paths.append(path)
            continue

        # Si llegamos aquí, la ruta no tiene un formato reconocido
        invalid_paths.append(f"{path} (Formato inválido)")

    # Comprueba si hay rutas válidas tras la validación
    if not validated_paths:
        return {
            "status": "error",
            "message": "No se proporcionaron rutas válidas. Por favor, proporciona URLs de Google Drive o rutas GCS.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths,
        }

    try:
        # Obtiene el nombre de recurso del corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configura el particionado de texto (chunking)
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            ),
        )

        # Importa archivos al corpus
        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )

        # Establece este corpus como el actual si no está definido
        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        # Construye el mensaje de éxito
        conversion_msg = ""
        if conversions:
            conversion_msg = " (URLs de Google Docs convertidas al formato de Drive)"

        return {
            "status": "success",
            "message": f"Se añadieron correctamente {import_result.imported_rag_files_count} archivo(s) al corpus '{corpus_name}'{conversion_msg}",
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validated_paths,
            "invalid_paths": invalid_paths,
            "conversions": conversions,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al agregar datos al corpus: {str(e)}",
            "corpus_name": corpus_name,
            "paths": paths,
        }
