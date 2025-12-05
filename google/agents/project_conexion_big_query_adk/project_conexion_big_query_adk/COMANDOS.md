# Primer paso
- gcloud init

# Segundo paso
- Construimos el proyecto dentro de SRC
- gcloud auth application-default login
- Lanzamos "adk web --host 0.0.0.0"

# Tercer paso: Habilitamos el API de VertexAI
- gcloud services enable aiplatform.googleapis.com --project=project-mlops-10-streamlit

# Cuarto paso: Habilitamos la API de BigQuery


# Cuando quiero hacer la parte de Frontend o Desplegar (Deployar) la aplicación
adk api_server --host 0.0.0.0 --port 8000

streamlit run main.py