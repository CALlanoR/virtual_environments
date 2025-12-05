# src/main.py

import streamlit as st
import requests
import json

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Agente de Scraping Web",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.image("./images/datapath-logo.png", use_container_width=True)
st.sidebar.markdown("### Agente con Apify & Google ADK")
st.sidebar.info("Este agente usa el 'Website Content Crawler' para extraer el texto de un sitio web. Modificado por Carlos Llano")

# URL del servidor ADK. Asumimos que se ejecuta en localhost.
ADK_SERVER_URL = "http://localhost:8000"

st.title("🤖 Agente de Scraping con Apify")
st.caption("Pega la URL del sitio web que quieres analizar y presiona Enter.")

# --- GESTIÓN DE SESIÓN ---
if "session_id" not in st.session_state:
    try:
        # El app_name debe coincidir con el nombre del directorio donde está el agent.py, en este caso 'src'
        response = requests.post(f"{ADK_SERVER_URL}/apps/src/users/user/sessions")
        response.raise_for_status()
        st.session_state.session_id = response.json()["id"]
        st.session_state.messages = []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ No se pudo conectar con el servidor del ADK. Asegúrate de que el comando `adk web` esté en ejecución. Error: {e}")
        st.stop()

# Mostrar historial del chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT DEL USUARIO Y LLAMADA AL AGENTE ---
if prompt := st.chat_input("Pega aquí la URL (ej: https://www.google.com)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # --- CAMBIO AQUÍ para reflejar el proceso ---
        with st.spinner("🤖 Analizando... (Paso 1: Scraping, Paso 2: Análisis). Esto puede tardar un momento..."):
            try:
                payload = {
                    "app_name": "src",
                    "user_id": "user",
                    "session_id": st.session_state.session_id,
                    "newMessage": {"role": "user", "parts": [{"text": prompt}]},
                }

                response = requests.post(
                    f"{ADK_SERVER_URL}/run_sse", json=payload, stream=True
                )
                response.raise_for_status()

                response_placeholder = st.empty()
                full_response = ""
                for line in response.iter_lines():
                    if line and line.decode("utf-8").startswith("data:"):
                        event = json.loads(line.decode("utf-8")[5:])
                        if isinstance(content := event.get("content"), dict):
                            if text := content.get("parts", [{}])[0].get("text"):
                                full_response += text
                                response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)

            except requests.exceptions.RequestException as e:
                st.error(f"Error al comunicarse con el agente: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})