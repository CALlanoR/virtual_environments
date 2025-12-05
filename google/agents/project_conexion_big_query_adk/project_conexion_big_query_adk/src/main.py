import streamlit as st
import requests
import json

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Agente SQL de CitiBike",
    page_icon="🧠",
    layout="wide"
)

# --- BARRA LATERAL FIJA ---
# Aquí puedes poner el logo de tu empresa y cualquier otro contenido fijo
st.sidebar.image("./images/datapath-logo.png", use_container_width=True)
st.sidebar.markdown("## Sistema de Consulta a una base de datos - Desarrollado por Nombre Apellido")
st.sidebar.markdown("---")

# La URL donde está corriendo su servidor ADK.
ADK_SERVER_URL = "http://localhost:8000"

st.title("🤖 Agente Analista de Datos de CitiBike")
st.caption("Hecho con ADK (Backend) y Streamlit (Frontend)")

# --- GESTIÓN DEL HISTORIAL DE LA CONVERSACIÓN ---
if "session_id" not in st.session_state:
    try:
        response = requests.post(f"{ADK_SERVER_URL}/apps/src/users/user/sessions")
        response.raise_for_status()
        session_id = response.json()["id"]
        st.session_state.session_id = session_id
        st.session_state.messages = []
    except requests.exceptions.RequestException as e:
        st.error(f"No se pudo conectar con el servidor del ADK. ¿Está `adk web --host 0.0.0.0` en ejecución? Error: {e}")
        st.stop()

# Mostramos el historial (chat mostrado en body)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ENTRADA Y COMUNICACIÓN CON EL AGENTE ---
if prompt := st.chat_input("¿En qué te puedo ayudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Contactando al agente..."):
            try:
                payload = {
                    "app_name": "src",
                    "user_id": "user",
                    "session_id": st.session_state.session_id,
                    "newMessage": {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    },
                }

                response = requests.post(
                    f"{ADK_SERVER_URL}/run_sse",
                    json=payload,
                    stream=True
                )
                response.raise_for_status()

                response_placeholder = st.empty()
                full_response = ""

                for line in response.iter_lines():
                    if not line:
                        continue
                    decoded = line.decode("utf-8")
                    if not decoded.startswith("data:"):
                        continue
                    event = json.loads(decoded[5:])
                    content = event.get("content")
                    if isinstance(content, dict):
                        for part in content.get("parts", []):
                            text = part.get("text")
                            if text:
                                full_response += text
                                response_placeholder.markdown(full_response)

                if not full_response:
                    response_placeholder.markdown("El agente no produjo una respuesta final.")

            except requests.exceptions.RequestException as e:
                if e.response is not None and e.response.status_code == 422:
                    st.error(f"Error 422: El servidor ADK rechazó el formato de los datos. Detalles: {e.response.text}")
                else:
                    st.error(f"Error al comunicarse con el agente: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
