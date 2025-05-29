import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
import json
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

# Configuración desde secrets
roles_json = st.secrets["roles_autorizados"]["data"]
ROLES = json.loads(roles_json)

auth_config = st.secrets["auth"]
google_config = st.secrets["auth.google"]

# Parámetros OAuth
client_id = google_config["client_id"]
client_secret = google_config["client_secret"]
redirect_uri = auth_config["redirect_uri"]
server_metadata_url = google_config["server_metadata_url"]

# Obtener metadata de Google (endpoints)
import requests

metadata = requests.get(server_metadata_url).json()
authorization_endpoint = metadata["authorization_endpoint"]
token_endpoint = metadata["token_endpoint"]
userinfo_endpoint = metadata["userinfo_endpoint"]

def get_authorization_url(state):
    oauth = OAuth2Session(client_id, client_secret, scope="openid email profile", redirect_uri=redirect_uri)
    uri, _ = oauth.create_authorization_url(authorization_endpoint, state=state, prompt="select_account")
    return uri

def get_token(code):
    oauth = OAuth2Session(client_id, client_secret, scope="openid email profile", redirect_uri=redirect_uri)
    token = oauth.fetch_token(token_endpoint, code=code)
    return token

def get_userinfo(token):
    oauth = OAuth2Session(client_id, client_secret, token=token)
    resp = oauth.get(userinfo_endpoint)
    return resp.json()

st.set_page_config(page_title="Sistema de Inventario", layout="wide")

# Paso 1: Leer query params para detectar código OAuth2
query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]
    # Intercambiar código por token
    token = get_token(code)
    # Obtener info usuario
    userinfo = get_userinfo(token)
    email = userinfo.get("email")
    if email in ROLES:
        st.session_state["user"] = userinfo
        # Limpiar URL para que no repita el código
        st.experimental_set_query_params()
        st.experimental_rerun()
    else:
        st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
        st.stop()

if "user" not in st.session_state:
    st.title("🔐 Login")
    if st.button("Iniciar sesión con Google"):
        # Generar URL autorización y redirigir (abrir en nueva ventana)
        import uuid
        state = str(uuid.uuid4())
        auth_url = get_authorization_url(state)
        st.markdown(f"[Haz clic aquí para iniciar sesión]({auth_url})", unsafe_allow_html=True)
else:
    user = st.session_state["user"]
    email = user["email"]
    name = user.get("name", "Usuario")
    picture = user.get("picture")
    role = ROLES.get(email, ["Invitado", 0])[0]

    st.title("PLATAFORMA DE INGENIERÍA CLÍNICA")

    with st.sidebar:
        st.markdown(f"👤 **{name}**\n📧 {email}\n🛡️ Rol: `{role}`")
        menu = option_menu(
            menu_title="Menú Principal",
            options=["Inicio", "Ver Base de Datos", "Perfil", "Configuración"],
            icons=["house", "database", "person", "gear"],
            default_index=0
        )
        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.experimental_rerun()

    if menu == "Inicio":
        st.title("🏥 Bienvenido al Sistema de Inventario")
        st.write("Navega usando el menú lateral para ver y gestionar los equipos médicos.")

    elif menu == "Ver Base de Datos":
        mostrar_base_datos()

    elif menu == "Perfil":
        st.title("👤 Perfil del Usuario")
        if picture:
            st.image(picture)
        st.write(f"Nombre: {name}")
        st.write(f"Correo: {email}")
        st.write(f"Rol: {role}")
        st.json(user)

    elif menu == "Configuración":
        st.title("⚙️ Configuración")
        st.write("Aquí irán las opciones de configuración personalizadas.")
