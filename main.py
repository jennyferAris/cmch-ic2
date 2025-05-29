import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse
import json
from base_datos import mostrar_base_datos

# Cargar configuración desde secrets
redirect_uri = st.secrets["auth"]["redirect_uri"]
client_id = st.secrets["auth"]["google"]["client_id"]
client_secret = st.secrets["auth"]["google"]["client_secret"]
server_metadata_url = st.secrets["auth"]["google"]["server_metadata_url"]

# Roles autorizados
roles_autorizados = json.loads(st.secrets["roles_autorizados"]["data"])

# Inicializar sesión OAuth2
oauth = OAuth2Session(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="openid email profile"
)

# Obtener configuración del servidor de autenticación
oauth.fetch_server_metadata(server_metadata_url)

# URL para redirigir a Google Login
auth_url, state = oauth.create_authorization_url(oauth.server_metadata["authorization_endpoint"])

# Guardar estado en session_state
if "state" not in st.session_state:
    st.session_state["state"] = state

# Mostrar botón de login si aún no hay token
if "token" not in st.session_state:

    query_params = st.query_params
    if "code" not in query_params:
        st.title("Inicio de sesión")
        st.markdown("Inicia sesión con tu cuenta de Google institucional")
        st.link_button("🔐 Iniciar sesión con Google", auth_url)

    else:
        # Intercambiar 'code' por token
        token = oauth.fetch_token(
            oauth.server_metadata["token_endpoint"],
            authorization_response=st.request.url,
            code=query_params["code"],
        )
        st.session_state["token"] = token

        # Obtener datos del usuario
        user_info = oauth.get(oauth.server_metadata["userinfo_endpoint"]).json()
        st.session_state["user_info"] = user_info

        st.rerun()

# Si ya hay token, mostrar contenido
if "token" in st.session_state:
    user_info = st.session_state["user_info"]
    user_email = user_info["email"]

    st.success(f"Has iniciado sesión como {user_email}")

    if user_email in roles_autorizados:
        nombre_rol, nivel = roles_autorizados[user_email]
        st.info(f"Tu rol es: **{nombre_rol}** (nivel {nivel})")

        # Mostrar la base de datos o interfaz principal aquí
        mostrar_base_datos()

    else:
        st.error("Tu correo no está autorizado para acceder a esta aplicación.")

