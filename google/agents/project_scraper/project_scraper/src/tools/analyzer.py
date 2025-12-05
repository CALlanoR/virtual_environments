# src/tools/analyzer.py

import os
import google.generativeai as genai

# Configuramos la API de Gemini desde el entorno
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_business_model(scraped_text: str) -> str:
    """
    Analiza el texto extraído de un sitio web para determinar el modelo de negocio,
    el rubro, los productos/servicios principales y el público objetivo de la empresa.

    Args:
        scraped_text (str): El contenido completo extraído de la web por el scraper.

    Returns:
        str: Un análisis detallado en formato Markdown.
    """
    if not api_key:
        # Esto es un fallback en caso de que la autenticación de ADC no funcione, aunque no debería pasar.
        # En tu caso, se está usando la autenticación del gcloud que ya configuraste.
        # El ADK se encargará de la autenticación al llamar a este agente,
        # pero es buena práctica tener esta verificación.
        pass

    # Creamos una instancia del modelo de Gemini para el análisis
    model = genai.GenerativeModel('gemini-2.0-flash') # Usamos el 1.5 que es excelente para análisis de texto largo

    prompt = f"""
    Eres un analista de negocios experto. Tu tarea es analizar el siguiente texto,
    que ha sido extraído del sitio web de una empresa. Basándote únicamente en esta información,
    responde a las siguientes preguntas de forma clara y estructurada en formato Markdown:

    1.  **Empresa/Producto:** ¿Cuál es el nombre de la empresa o producto principal?
    2.  **Rubro/Industria:** ¿A qué sector o industria pertenece? (Ej: SaaS, E-commerce, Consultoría, Educación, etc.)
    3.  **Modelo de Negocio:** ¿Cómo crees que gana dinero? (Ej: Venta de software por suscripción, venta de productos físicos, comisiones, publicidad, etc.)
    4.  **Propuesta de Valor:** ¿Qué problema principal resuelve para sus clientes? ¿Cuál es su principal beneficio?
    5.  **Público Objetivo:** ¿A quién parece estar dirigido su producto o servicio? (Ej: Pequeñas empresas, desarrolladores, equipos de marketing, consumidores finales, etc.)
    6.  **Servicios/Productos Clave:** Enumera los 3-5 servicios o productos más importantes que se mencionan.

    Aquí está el texto del sitio web:
    ---
    {scraped_text}
    ---
    """

    try:
        print("INFO: Enviando texto a Gemini para análisis de negocio...")
        response = model.generate_content(prompt)
        print("INFO: Análisis de negocio completado.")
        return response.text
    except Exception as e:
        return f"Error al analizar el contenido con Gemini: {e}"