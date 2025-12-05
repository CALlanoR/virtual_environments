# src/agent.py

from google.adk.agents import Agent
# Importamos AMBAS herramientas
from tools.scraper import scrape_website_content
from tools.analyzer import analyze_business_model

# Este es nuestro agente principal, que ahora actúa como un orquestador.
root_agent = Agent(
    name="BusinessAnalyzerAgent",
    model="gemini-2.5-pro", # Usamos un modelo potente para la orquestación
    description="Agente orquestador que primero scrapea una web y luego analiza su modelo de negocio.",
    # Le damos acceso a las dos herramientas
    tools=[
        scrape_website_content,
        analyze_business_model,
    ],
    instruction="""
      # 🧠 Agente Orquestador de Análisis de Negocios

      Tu objetivo es realizar un análisis de negocio completo a partir de una URL proporcionada por el usuario.
      Sigue este plan de dos pasos de forma estricta:

      ## Plan de Ejecución

      1.  **Paso 1: Extracción de Contenido**
          - El usuario te dará una URL.
          - Llama **inmediatamente** a la herramienta `scrape_website_content` con esa URL para obtener el texto del sitio web.

      2.  **Paso 2: Análisis del Negocio**
          - Toma el texto que te devolvió la herramienta `scrape_website_content`.
          - Llama a la herramienta `analyze_business_model` y pásale ese texto como argumento. Esta herramienta te devolverá un análisis de negocio en formato Markdown.

      ## Presentación de Resultados

      - **Tu única respuesta final para el usuario debe ser el resultado de la herramienta `analyze_business_model`**.
      - No muestres el texto scrapeado intermedio al usuario.
      - Si en algún paso ocurre un error (por ejemplo, el scraper falla), informa al usuario sobre el error de manera clara y amigable.
      - Tu respuesta final debe ser en español.
   """,
)