import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos


# Diccionario de roles autorizados
ROLES = {
    "daang0406@gmail.com": "Ingeniero Clínico",
    "jear142003@gmail.com": "Practicante"
}

st.set_page_config(page_title="Sistema de Inventario", layout="wide")
st.title("PLATAFORMA DE INGENIERÍA CLÍNICA")

# Autenticación
if not st.user.is_logged_in:
    st.login("google")
    st.stop()

email = st.user.email
name = st.user.name
role = ROLES.get(email)

# Acceso denegado si el correo no está en la lista
if role is None:
    st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
    st.stop()

# Sidebar con menú
with st.sidebar:
    st.markdown(f"👤 **{name}**\n📧 {email}\n🛡️ Rol: `{role}`")
    menu = option_menu(
        menu_title="Menú Principal",
        options=["Inicio", "Ver Base de Datos", "Perfil", "Configuración"],
        icons=["house", "database", "person", "gear"],
        default_index=0
    )

# Sección de inicio
if menu == "Inicio":
    st.title("🏥 Bienvenido al Sistema de Inventario")
    st.write("Navega usando el menú lateral para ver y gestionar los equipos médicos.")

# Sección de base de datos
elif menu == "Ver Base de Datos":
    mostrar_base_datos()

# Perfil
elif menu == "Perfil":
    st.title("👤 Perfil del Usuario")
    st.image(st.user.picture)
    st.write(f"Nombre: {name}")
    st.write(f"Correo: {email}")
    st.write(f"Rol: {role}")
    with st.expander("Ver token completo"):
        st.json(st.user.to_dict())

# Configuración
elif menu == "Configuración":
    st.title("⚙️ Configuración")
    st.write("Aquí irán las opciones de configuración personalizadas.")

# Logout
if st.sidebar.button("Cerrar sesión"):
    st.logout()
