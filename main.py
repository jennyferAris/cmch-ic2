import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import requests
import json

# --- Configuración desde secrets.toml ---
CLIENT_ID = st.secrets["auth.google"]["client_id"]
CLIENT_SECRET = st.secrets["auth.google"]["client_secret"]
REDIRECT_URI = st.secrets["auth"]["redirect_uri"]
DISCOVERY_URL = st.secrets["auth.google"]["server_metadata_url"]
ROLES = json.loads(st.secrets["roles_autorizados"]["data"])

# Obtener endpoints de Google
@st.cache_data(show_spinner=False)
def get_google_provider_cfg():
    return requests.get(DISCOVERY_URL).json()

provider_cfg = get_google_provider_cfg()
authorization_endpoint = provider_cfg["authorization_endpoint"]
token_endpoint = provider_cfg["token_endpoint"]
userinfo_endpoint = provider_cfg["userinfo_endpoint"]

def login():
    oauth = OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=REDIRECT_URI,
    )
    authorization_url, state = oauth.create_authorization_url(authorization_endpoint)
    st.session_state["oauth_state"] = state
    st.experimental_set_query_params()  # limpiar params
    st.markdown(f"""
        <a href="{authorization_url}" style="text-decoration:none;">
        <button style="
            padding:10px 20px; font-size:16px; background-color:#4285F4; color:white;
            border:none; border-radius:5px; cursor:pointer;">
            Ingresar con Google
        </button>
        </a>
    """, unsafe_allow_html=True)

def fetch_token(code):
    oauth = OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        state=st.session_state.get("oauth_state"),
    )
    token = oauth.fetch_token(token_endpoint, code=code)
    return token

def get_userinfo(token):
    oauth = OAuth2Session(CLIENT_ID, CLIENT_SECRET, token=token)
    resp = oauth.get(userinfo_endpoint)
    resp.raise_for_status()
    return resp.json()

def main():
    st.title("Sistema de Login Google - CMCH IC2")

    # Si ya autenticado, mostrar info y rol
    if "user" in st.session_state:
        user = st.session_state["user"]
        email = user.get("email")
        st.success(f"¡Bienvenido {email}!")
        # Mostrar rol si autorizado
        if email in ROLES:
            rol_name, rol_id = ROLES[email]
            st.info(f"Tu rol es: **{rol_name}** (ID: {rol_id})")
        else:
            st.warning("No tienes un rol asignado en el sistema.")

        if st.button("Cerrar sesión"):
            st.session_state.pop("user")
            st.experimental_rerun()

        # Aquí iría el resto de tu app con acceso autorizado
        st.write("Contenido protegido para usuarios autenticados...")

    else:
        # Revisar si viene el código OAuth en la URL
        query_params = st.experimental_get_query_params()
        if "code" in query_params:
            code = query_params["code"][0]
            try:
                token = fetch_token(code)
                userinfo = get_userinfo(token)
                st.session_state["user"] = userinfo
                st.experimental_set_query_params()  # limpiar URL
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error en autenticación: {e}")
        else:
            login()

if __name__ == "__main__":
    if "oauth_state" not in st.session_state:
        st.session_state["oauth_state"] = None
    main()
