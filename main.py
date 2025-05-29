import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
import json
from authlib.integrations.streamlit_client import StreamlitOAuth2App
import requests

# Cargar roles autorizados desde secrets
roles_json = st.secrets["roles_autorizados"]["data"]
ROLES = json.loads(roles_json)

# Config OAuth desde secrets
auth_config = st.secrets["auth"]
google_config = st.secrets["auth.google"]

# Inicializamos cliente OAuth2 con la configuración de Google
oauth_app = StreamlitOAuth2App(
    client_id=google_config["client_id"],
    client_secret=google_config["client_secret"],
    server_metadata_url=google_config["server_metadata_url"],
    redirect_uri=auth_config["redirect_uri"],
    scope="openid email profile",
)

st.set_page_config(page_title="Sistema de Inventario", layout="wide")

def login():
    st.title("🔐 Login")
    if st.button("Iniciar sesión con Google"):
        oauth_app.authorize_redirect()

def logout():
    st.session_state.clear()
    st.experimental_rerun()

if "user" not in st.session_state:
    # Intentamos obtener token e info si el usuario viene de autorización
    token = oauth_app.authorize_access_token()
    if token:
        user_info = oauth_app.parse_id_token(token)
        if user_info:
            email = user_info["email"]
            if email in ROLES:
                st.session_state["user"] = user_info
                st.experimental_rerun()
            else:
                st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
                st.stop()
        else:
            st.error("No se pudo obtener información del usuario.")
            st.stop()
    else:
        login()
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
            logout()

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
