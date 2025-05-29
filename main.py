import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import os
import json
import urllib.parse

# Configuración
client_id = st.secrets["auth"]["google"]["client_id"]
client_secret = st.secrets["auth"]["google"]["client_secret"]
redirect_uri = st.secrets["auth"]["redirect_uri"]
server_metadata_url = st.secrets["auth"]["google"]["server_metadata_url"]
cookie_secret = st.secrets["auth"]["cookie_secret"]

# Diccionario de roles autorizados
roles_autorizados = json.loads(st.secrets["roles_autorizados"]["data"])

# Sesión OAuth
oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)

# Intentar cargar metadata desde Google o fallback manual
try:
    oauth.fetch_server_metadata(server_metadata_url)
except Exception as e:
    st.warning("Fallo al obtener metadata de Google. Usando configuración manual.")
    oauth.register_client_metadata({
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
    })

# Obtener parámetros del callback
query_params = st.experimental_get_query_params()

if "code" in query_params:
    # Intercambiar código por token
    code = query_params["code"][0]
    token = oauth.fetch_token(code=code)
    user_info = oauth.get("userinfo").json()
    correo = user_info["email"]

    if correo in roles_autorizados:
        rol, nivel = roles_autorizados[correo]
        st.success(f"Bienvenida/o {rol}")
        st.write(f"Tu correo es: {correo}")
        st.write(f"Tu nivel de acceso es: {nivel}")
    else:
        st.error("No estás autorizado para acceder a esta aplicación.")
else:
    # Si no hay código, mostrar botón de login
    auth_url, state = oauth.create_authorization_url(oauth.server_metadata["authorization_endpoint"], access_type="offline", prompt="consent")
    st.markdown(f"[Iniciar sesión con Google]({auth_url})")
