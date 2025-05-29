import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
from asignar_tareas import mostrar_tareas_asignadas, mostrar_todas_las_tareas, asignar_tarea_form

# Diccionario de roles autorizados con niveles
ROLES = {
    "pasante0@gmail.com": ("Pasante 0", 0),
    "pasante1@gmail.com": ("Pasante 1", 1),
    "pasante2@gmail.com": ("Pasante 2", 2),
    "prepro@gmail.com": ("Ingeniero Preprofesional", 3),
    "profesional@gmail.com": ("Ingeniero Profesional", 4),
    "jear142003@gmail.com": ("Jefe del Departamento", 5)
}

st.set_page_config(page_title="Sistema de Inventario", layout="wide")
st.title("PLATAFORMA DE INGENIERÍA CLÍNICA")

# Autenticación
if not st.user.is_logged_in:
    st.login("google")
    st.stop()

email = st.user.email
name = st.user.name
rol_info = ROLES.get(email)

# Acceso denegado si el correo no está en la lista
if rol_info is None:
    st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
    st.stop()

role, rol_nivel = rol_info

# Sidebar con menú
with st.sidebar:
    st.markdown(f"👤 **{name}**\n📧 {email}\n🛡️ Rol: `{role}`")
    menu = option_menu(
        menu_title="Menú Principal",
        options=["Inicio", "Ver Base de Datos", "Asignación de Tareas", "Perfil", "Configuración"],
        icons=["house", "database", "clipboard-check", "person", "gear"],
        default_index=0
    )
    if st.button("Cerrar sesión"):
        st.logout()

# Sección de inicio
if menu == "Inicio":
    st.title("🏥 Bienvenido al Sistema de Inventario")
    st.write("Navega usando el menú lateral para ver y gestionar los equipos médicos.")

# Sección de base de datos
elif menu == "Ver Base de Datos":
    mostrar_base_datos()

# Asignación de Tareas
elif menu == "Asignación de Tareas":
    st.title("🗂️ Asignación de Tareas")
    if rol_nivel in [1, 2]:
        mostrar_tareas_asignadas(email)
    elif rol_nivel >= 3:
        mostrar_todas_las_tareas()
        asignar_tarea_form()
    else:
        st.warning("🔒 Tu rol actual no tiene acceso a tareas asignadas.")

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
