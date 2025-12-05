# src/tools/scraper.py

import os
from dotenv import load_dotenv
from apify_client import ApifyClient

# Carga las variables de entorno desde el archivo .env que está en el mismo directorio (src)
load_dotenv()


def scrape_website_content(start_url: str) -> str:
    """
    Utiliza el actor "Website Content Crawler" de Apify para extraer el contenido de texto de un sitio web.

    Args:
        start_url (str): La URL principal del sitio web que se desea scrapear.

    Returns:
        str: El contenido extraído en formato Markdown o un mensaje de error si algo sale mal.
    """
    apify_token = os.getenv("APIFY_API_TOKEN")

    if not apify_token:
        return (
            "Error: La variable de entorno APIFY_API_TOKEN no está configurada o no se pudo leer. "
            "Asegúrate de que el archivo .env esté en la carpeta 'src' y contenga la clave."
        )

    try:
        client = ApifyClient(apify_token)

        # Configuración optimizada del crawler
        run_input = {
            "startUrls": [{"url": start_url}],
            "maxCrawlPages": 20,
            "maxCrawlingDepth": 2,
            "includeUrlGlobs": [f"{start_url.rstrip('/')}/**"],
            "crawlerType": "playwright:adaptive",
            "proxyConfiguration": {"useApifyProxy": True},
            "pageLoadTimeoutSecs": 60,
            "infiniteScroll": {
                "scrollDownInPx": 500,
                "timeoutSecs": 2
            }
        }

        print(f"INFO: Iniciando el actor 'website-content-crawler' para la URL: {start_url}")
        run = client.actor("apify/website-content-crawler").call(run_input=run_input)
        print("INFO: El actor finalizó la ejecución. Recuperando resultados...")

        # Recopilar y formatear cada página
        items = []
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            return "Error: No se encontró el dataset de resultados."

        for item in client.dataset(dataset_id).iterate_items():
            title = item.get('title') or 'Sin Título'
            text = item.get('text', '').strip()
            if text:
                items.append(f"## {title}\n\n{text}\n\n---\n")

        if not items:
            return (
                "El scraper se ejecutó correctamente, pero no se encontró contenido textual relevante "
                "en la URL proporcionada."
            )

        return "".join(items)

    except Exception as e:
        error_msg = str(e)
        if "Authentication failed" in error_msg:
            return (
                f"Error de Apify: Falló la autenticación. Por favor, verifica que el APIFY_API_TOKEN "
                f"en tu archivo .env sea el correcto. Error original: {error_msg}"
            )
        return f"Error al ejecutar el scraper de Apify: {error_msg}"
