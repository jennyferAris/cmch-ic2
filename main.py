import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
from generador_qr import generar_qrs  # ← Nueva importación
import json

st.set_page_config(page_title="Sistema de Inventario - IC", layout="wide")

# Función para cargar roles desde secrets
@st.cache_data
def cargar_roles():
    try:
        roles_data = json.loads(st.secrets["roles_autorizados"]["data"])
        return roles_data
    except Exception as e:
        st.error(f"Error al cargar roles: {e}")
        return {}

# Función para obtener información del rol
def obtener_info_rol(email, roles_data):
    if email in roles_data:
        return {
            "nombre": roles_data[email][0],
            "nivel": roles_data[email][1],
            "funciones": roles_data[email][2] if len(roles_data[email]) > 2 else []
        }
    return None

# Función para obtener menús según el rol
def obtener_menus_por_rol(nivel):
    menus_base = ["Inicio", "Base de Datos"]
    
    if nivel == 0:  # Pasante 0
        return menus_base + ["Fichas Técnicas", "Mis Reportes"]
    elif nivel == 1:  # Pasante 1
        return menus_base + ["Mantenimientos", "Inventario"]
    elif nivel == 2:  # Pasante 2
        return menus_base + ["Mantenimientos", "Gestión Pasantes", "Inventario"]
    elif nivel == 3:  # Practicante Preprofesional
        return menus_base + ["Supervisión", "Mantenimientos", "Pasantes"]
    elif nivel == 4:  # Ingeniero Junior
        return menus_base + ["Mantenimientos", "Supervisión", "Reportes"]
    elif nivel == 5:  # Ingeniero Clínico (Jefe)
        return menus_base + ["Dashboard KPIs", "Generador QR", "Asignación Tareas", "Gestión Usuarios", "Reportes", "Rendimiento Equipo", "Cronograma"]
    elif nivel == 6:  # Personal de Salud
        return ["Escáner QR", "Reportar Evento", "Mis Reportes"]
    else:
        return menus_base

# Función para obtener iconos de menú
def obtener_iconos_menu(menus):
    iconos = {
        "Inicio": "house",
        "Base de Datos": "database",
        "Dashboard KPIs": "graph-up",
        "Generador QR": "qr-code",
        "Asignación Tareas": "clipboard-check",
        "Gestión Usuarios": "people",
        "Reportes": "file-earmark-text",
        "Rendimiento Equipo": "award",
        "Cronograma": "calendar3",
        "Escáner QR": "camera",
        "Reportar Evento": "exclamation-triangle",
        "Fichas Técnicas": "file-medical",
        "Mantenimientos": "tools",
        "Inventario": "box-seam",
        "Gestión Pasantes": "person-badge",
        "Supervisión": "eye",
        "Pasantes": "person-workspace",
        "Mis Reportes": "file-person"
    }
    return [iconos.get(menu, "circle") for menu in menus]

# Función para mostrar la pantalla de login
def mostrar_login():
    # Crear espacio superior
    st.write("")
    st.write("")
    
    # Centrar todo el contenido
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; max-width: 800px; margin: 0 auto;">
        <h1 style="color: #DC143C; margin-bottom: 10px;">
            🏥 PLATAFORMA DEL DEPARTAMENTO DE INGENIERÍA CLÍNICA
        </h1>
        <h3 style="color: #666; margin-bottom: 30px;">
            Sistema de Gestión de Equipos Médicos
        </h3>
        <p style="font-size: 18px; color: #555; line-height: 1.6; margin-bottom: 20px;">
            Sistema integral para mantenimiento preventivo, inventario y gestión técnica.
        </p>
        <p style="font-size: 16px; color: #777;">
            Para continuar, inicia sesión con tu cuenta autorizada.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Espacio antes del botón
    st.write("")
    
    # Centrar el botón de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔑 Ingresar con Google", 
                    type="primary", 
                    use_container_width=True,
                    help="Haz clic para iniciar sesión con tu cuenta de Google"):
            st.login("google")

# Verificar si el usuario está logueado
if not st.user.is_logged_in:
    mostrar_login()
    st.stop()

# Cargar roles desde secrets
roles_data = cargar_roles()
email = st.user.email
name = st.user.name
rol_info = obtener_info_rol(email, roles_data)

# Acceso denegado si el correo no está en la lista
if rol_info is None:
    st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
    st.info(f"📧 Cuenta utilizada: {email}")
    st.warning("Contacta al Ingeniero Clínico para solicitar acceso al sistema.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Intentar con otra cuenta"):
            st.logout()
    with col2:
        if st.button("📞 Contactar Administrador"):
            st.info("Contacta a: daang0406@gmail.com")
    st.stop()

# Extraer información del rol
rol_nombre = rol_info["nombre"]
rol_nivel = rol_info["nivel"]
funciones = rol_info["funciones"]

# Obtener menús según el rol
menus_usuario = obtener_menus_por_rol(rol_nivel)
iconos_menu = obtener_iconos_menu(menus_usuario)

# Título principal
st.title("🏥 PLATAFORMA DE INGENIERÍA CLÍNICA")

# Sidebar con información del usuario y menú
with st.sidebar:
    # Información del usuario
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h4 style="margin: 0; color: #1f77b4;">👤 {name}</h4>
        <p style="margin: 5px 0; font-size: 14px;">📧 {email}</p>
        <p style="margin: 5px 0; font-size: 14px;">🛡️ <strong>{rol_nombre}</strong></p>
        <p style="margin: 5px 0; font-size: 14px;">🏆 Nivel: {rol_nivel}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Funciones del rol
    with st.expander("🎯 Mis Funciones"):
        for funcion in funciones:
            st.write(f"• {funcion}")
    
    st.markdown("---")
    
    # Menú principal
    menu = option_menu(
        menu_title="Menú Principal",
        options=menus_usuario,
        icons=iconos_menu,
        default_index=0,
        styles={
            "container": {"padding": "0!important"},
            "icon": {"color": "#DC143C", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#DC143C"},
        }
    )

# Contenido principal según la selección del menú
if menu == "Inicio":
    st.markdown(f"## 🎯 Bienvenido, {rol_nombre}")
    
    # Mensaje personalizado según el rol
    if rol_nivel == 5:  # Ingeniero Clínico
        st.success("👨‍💼 Acceso completo al sistema como Jefe del Departamento de Ingeniería Clínica.")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 KPIs", "Dashboard", "Activo")
        with col2:
            st.metric("👥 Equipo", "6 miembros", "+1")
        with col3:
            st.metric("⚙️ Equipos", "150", "3 nuevos")
        with col4:
            st.metric("🔧 Mantenimientos", "12 programados", "Esta semana")
            
    elif rol_nivel == 4:  # Ingeniero Junior
        st.info("👨‍🔧 Gestiona mantenimientos y supervisa las operaciones técnicas del departamento.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔧 Mantenimientos", "8 programados", "Hoy")
        with col2:
            st.metric("📋 Reportes", "3 pendientes", "Revisión")
        with col3:
            st.metric("👥 Supervisión", "4 áreas", "Activas")
            
    elif rol_nivel in [1, 2, 3]:  # Pasantes y Practicante
        st.info(f"👨‍🎓 {rol_nombre} - Acceso a funciones de mantenimiento e inventario.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📋 Mis Tareas", "5 pendientes", "Hoy")
        with col2:
            st.metric("🔧 Mantenimientos", "Asignados", "3 equipos")
            
    elif rol_nivel == 6:  # Personal de Salud
        st.info("👩‍⚕️ Reporta eventos y utiliza el escáner QR para equipos médicos.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📱 Escáner QR", type="primary", use_container_width=True):
                st.info("Módulo de escáner QR en desarrollo")
        with col2:
            if st.button("📝 Reportar Evento", type="secondary", use_container_width=True):
                st.info("Módulo de reportes en desarrollo")
    
    # Actividad reciente
    st.markdown("### 📋 Actividad Reciente")
    st.info("🔄 Sistema de Ingeniería Clínica inicializado correctamente")
    if rol_nivel >= 3:
        st.success("✅ Permisos de supervisión activos")
    if rol_nivel >= 5:
        st.success("🎛️ Panel de administración disponible")

elif menu == "Base de Datos":
    mostrar_base_datos()

elif menu == "Dashboard KPIs" and rol_nivel >= 5:
    st.title("📊 Dashboard de KPIs")
    st.info("📈 Módulo en desarrollo - Métricas y indicadores del departamento")

# ← AQUÍ ESTÁ LA INTEGRACIÓN DEL GENERADOR QR
elif menu == "Generador QR" and rol_nivel >= 5:
    generar_qrs()  # ← Llama a tu función del generador QR

elif menu == "Asignación Tareas" and rol_nivel >= 5:
    st.title("📋 Asignación de Tareas")
    st.info("📝 Módulo en desarrollo - Sistema de asignación de tareas")
    
elif menu == "Gestión Usuarios" and rol_nivel >= 5:
    st.title("👥 Gestión de Usuarios")
    st.info("👤 Módulo en desarrollo - Administración de usuarios y roles")

elif menu == "Cronograma" and rol_nivel >= 5:
    st.title("📅 Cronograma de Mantenimientos")
    st.info("📋 Módulo en desarrollo - Programación de mantenimientos preventivos")

elif menu == "Mantenimientos":
    st.title("🔧 Gestión de Mantenimientos")
    st.info("⚙️ Módulo en desarrollo - Sistema de mantenimientos preventivos y correctivos")

elif menu == "Inventario":
    st.title("📦 Control de Inventario")
    st.info("📋 Módulo en desarrollo - Gestión de inventario de equipos médicos")

elif menu == "Escáner QR" and rol_nivel == 6:
    st.title("📱 Escáner de Códigos QR")
    st.info("📷 Módulo en desarrollo - Escáner para identificación de equipos")

elif menu == "Reportar Evento" and rol_nivel == 6:
    st.title("📝 Reportar Evento")
    st.info("🚨 Módulo en desarrollo - Sistema de reportes de eventos técnicos")

elif menu == "Fichas Técnicas":
    st.title("📋 Fichas Técnicas")
    st.info("📄 Módulo en desarrollo - Fichas técnicas de equipos")

elif menu == "Mis Reportes":
    st.title("📊 Mis Reportes")
    st.info("📈 Módulo en desarrollo - Reportes personalizados")

elif menu == "Gestión Pasantes":
    st.title("👥 Gestión de Pasantes")
    st.info("🎓 Módulo en desarrollo - Administración de pasantes")

elif menu == "Supervisión":
    st.title("👁️ Supervisión")
    st.info("🔍 Módulo en desarrollo - Panel de supervisión")

elif menu == "Pasantes":
    st.title("👨‍🎓 Gestión de Pasantes")
    st.info("📚 Módulo en desarrollo - Administración de pasantes")

elif menu == "Reportes":
    st.title("📄 Reportes del Sistema")
    st.info("📊 Módulo en desarrollo - Generación de reportes")

elif menu == "Rendimiento Equipo":
    st.title("🏆 Rendimiento del Equipo")
    st.info("📈 Módulo en desarrollo - Métricas de rendimiento")

else:
    st.title(f"🔧 {menu}")
    st.info(f"⚙️ Módulo en desarrollo - {menu}")

# Logout en sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
    st.logout()

# Footer limpio
st.markdown("---")
st.markdown("🏥 **Sistema de Ingeniería Clínica v1.0** | Enfocado en mantenimiento preventivo y gestión técnica")