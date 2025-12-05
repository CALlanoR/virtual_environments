1. Seleccionar Vertex AI
2. Habilitar Vertex API
3. Crear el contenedor con: docker compose up -d
4. Ingresar al contenedor con: docker exec -ti agent bash
5. Conectar el contenedor con gcp con: gcloud init
6. Crear service account en IAM con rol Owner
7. Crearle key al service account: darle click al Service Account y Add key
8. Descargarlo y copiarlo en el repositorio del codigo del agente
9. Configurar el archivo .env con el gemini api key de: google ai studio, https://aistudio.google.com/apikey
    9.1 se genera para el proyecto donde se va a correr y se copia
10. ejecutar adk web --host 0.0.0.0 fuera de las carpetas de los agentes
11. Abrir la url que muestra y seleccionar el multiagent
12. Preguntar cualquier cosa para ver como pasa la informacion de un agente a otro
