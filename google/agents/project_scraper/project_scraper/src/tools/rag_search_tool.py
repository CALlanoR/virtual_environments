# src/tools/rag_search_tool.py

import os
from google.cloud import discoveryengine

PROJECT_ID     = os.getenv("GOOGLE_CLOUD_PROJECT",   "")
LOCATION       = os.getenv("GOOGLE_CLOUD_LOCATION",  "global")
DATASTORE_ID   = os.getenv("GOOGLE_CLOUD_DATASTORE_ID", "")

def search_datapath_knowledge_base(query: str) -> str:
    try:
        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=PROJECT_ID,
            location=LOCATION,
            data_store=DATASTORE_ID,
            serving_config="default_config",
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=3,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=3,
                    include_citations=False,
                )
            )
        )
        response = client.search(request)
        return response.summary.summary_text or "Sin resultados."
    except Exception as e:
        return f"Error al conectar con Discovery Engine: {e}"
