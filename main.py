import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
from generar_qr import generar_qrs
import json
from escanear_qr import mostrar_escaner_qr
from informes_tecnicos import mostrar_informes_tecnicos 
from asignacion_tareas import mostrar_modulo_asignacion 
from gestion_usuarios import mostrar_modulo_gestion_usuarios
from dashboard_kpis import mostrar_modulo_dashboard
from reportes import mostrar_modulo_reportes
from rendimiento_equipo import mostrar_rendimiento_equipo


#st.set_page_config(page_title="Sistema de Inventario - IC", layout="wide")

# Al inicio del archivo, agregar configuración de página
st.set_page_config(
    page_title="MEDIFLOW",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS global para eliminar elementos
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .reportview-container .main {
        color: black;
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

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
        return menus_base + ["Informes Técnicos", "Fichas Técnicas", "Mis Reportes"]
    elif nivel == 1:  # Pasante 1
        return menus_base + ["Mantenimientos", "Informes Técnicos", "Inventario"]
    elif nivel == 2:  # Pasante 2
        return menus_base + ["Mantenimientos", "Informes Técnicos", "Asignación Tareas", "Gestión Pasantes", "Inventario"]
    elif nivel == 3:  # Practicante Preprofesional
        return menus_base + ["Supervisión", "Mantenimientos", "Informes Técnicos", "Asignación Tareas", "Pasantes"]
    elif nivel == 4:  # Ingeniero Junior
        return menus_base + ["Mantenimientos", "Supervisión", "Informes Técnicos", "Asignación Tareas", "Reportes", "Escáner QR"]
    elif nivel == 5:  # Ingeniero Clínico (Jefe)
        return menus_base + ["Dashboard KPIs", "Generador QR", "Escáner QR", "Informes Técnicos", "Asignación Tareas", "Gestión Usuarios", "Reportes", "Rendimiento Equipo"]
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
        #"Cronograma": "calendar3",
        "Escáner QR": "camera",
        "Reportar Evento": "exclamation-triangle",
        "Fichas Técnicas": "file-medical",
        "Informes Técnicos": "file-earmark-pdf",  # ← NUEVO ICONO
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
    # CSS para diseño moderno
    st.markdown("""
    <style>
    /* Eliminar elementos de Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .stDeployButton {
        display: none !important;
    }
    
    footer {
        display: none !important;
    }
    
    /* Fondo elegante */
    .stApp {
        background: #ffffff;
        min-height: 100vh;
    }
    
    .block-container {
        padding-top: 3rem !important;
    }
    
    /* Contenedor con diseño de tarjeta */
    .login-container {
        background: white;
        border-radius: 20px;
        padding: 60px 50px;
        box-shadow: 
            0 0 0 1px rgba(0, 0, 0, 0.05),
            0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin: 50px auto;
        max-width: 450px;
        text-align: center;
        position: relative;
    }
    
    /* Efecto de brillo sutil */
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(180, 38, 65, 0.4), transparent);
    }
    
    /* Hover effect */
    .login-container:hover {
        transform: translateY(-8px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 0 0 1px rgba(0, 0, 0, 0.05),
            0 32px 40px -12px rgba(0, 0, 0, 0.15),
            0 16px 16px -8px rgba(0, 0, 0, 0.08);
    }
    
    /* Botón elegante */
    .stButton > button {
        background: linear-gradient(135deg, #b42641 0%, #d63384 50%, #ffc331 100%);
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: white;
        width: 100%;
        margin-top: 25px;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(180, 38, 65, 0.4);
        background: linear-gradient(135deg, #a0213a 0%, #c42a69 50%, #e6b02e 100%);
    }
    
    /* Logo container con efecto */
    .logo-container {
        margin-bottom: 40px;
        padding: 10px;
        position: relative;
    }
    
    .logo-container::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #b42641, #ffc331);
        border-radius: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Espacio superior
    st.write("")
    st.write("")
    
    # Centrar contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Logo con tu código específico para centrar
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try:
            # Usar columnas internas para centrar la imagen
            img_col1, img_col2, img_col3 = st.columns([1.5, 2, 1.5])
            with img_col2:
                st.image("static/MEDIFLOW LOGO.png", width=220)
        except:
            st.error("No se pudo cargar el logo")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contenido elegante
        st.markdown("""
        <div style="text-align: center; margin: 25px 0;">
            <h1 style="color: #b42641; margin-bottom: 25px; font-weight: 700; font-size: 32px; letter-spacing: -0.5px;">
                Bienvenido
            </h1>
            <p style="font-size: 17px; color: #64748b; line-height: 1.7; margin-bottom: 20px; font-weight: 400;">
                Accede al sistema integral de gestión para equipos médicos
            </p>
            <p style="font-size: 15px; color: #94a3b8; font-weight: 500;">
                Usa tu cuenta autorizada para continuar
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔑 Ingresar con Google",
                     type="primary",
                     use_container_width=True,
                     help="Haz clic para iniciar sesión con tu cuenta de Google"):
            st.login("google")
        
        st.markdown('</div>', unsafe_allow_html=True)

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
    # Información del usuario con estilo Cayetano
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #B71C1C 0%, #DC143C 100%);
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.3);
        text-align: center;
        color: white;
    ">
        <div style="
            background-color: rgba(255, 255, 255, 0.2);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            margin: 0 auto 15px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        ">
            👤
        </div>
        <h3 style="margin: 0 0 8px 0; color: white; font-size: 18px; font-weight: bold;">
            {name}
        </h3>
        <p style="margin: 0 0 12px 0; font-size: 14px; opacity: 0.9;">
            {email}
        </p>
        <div style="
            background-color: rgba(255, 255, 255, 0.2);
            padding: 8px 12px;
            border-radius: 20px;
            margin: 10px 0;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        ">
            <span style="font-size: 16px;">🛡️</span>
            <span style="font-weight: bold; font-size: 14px;">{rol_nombre}</span>
        </div>
        <p style="margin: 8px 0 0 0; font-size: 16px; font-weight: bold;">
            Nivel: {rol_nivel}
        </p>
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
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📊 KPIs", "Dashboard", "Activo")
        with col2:
            st.metric("👥 Equipo", "6 miembros", "+1")
        with col3:
            st.metric("⚙️ Equipos", "150", "3 nuevos")
        with col4:
            st.metric("🔧 Mantenimientos", "12 programados", "Esta semana")
        with col5:
            if st.button("📱 Escáner QR", type="primary", use_container_width=True):
                st.info("Redirigiendo al escáner QR...")
        
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
                st.info("Redirigiendo al escáner QR...")
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

elif menu == "Dashboard KPIs":
    mostrar_modulo_dashboard()

# Generador QR
elif menu == "Generador QR" and rol_nivel >= 5:
    generar_qrs()

# ← NUEVO MÓDULO DE INFORMES TÉCNICOS
elif menu == "Informes Técnicos":
    # Pasar información del rol al módulo de informes
    if 'name' not in st.session_state:
        st.session_state.name = name
    if 'rol_nombre' not in st.session_state:
        st.session_state.rol_nombre = rol_nombre
    if 'email' not in st.session_state:
        st.session_state.email = email
    mostrar_informes_tecnicos()

elif menu == "Asignación Tareas" and rol_nivel >= 2:
    # Pasar información del rol al módulo
    if 'email' not in st.session_state:
        st.session_state.email = email
    if 'name' not in st.session_state:
        st.session_state.name = name
    if 'rol_nivel' not in st.session_state:
        st.session_state.rol_nivel = rol_nivel
    
    mostrar_modulo_asignacion()


elif menu == "Gestión Usuarios":
    mostrar_modulo_gestion_usuarios()

#elif menu == "Cronograma" and rol_nivel >= 5:
    #st.title("📅 Cronograma de Mantenimientos")
    #st.info("📋 Módulo en desarrollo - Programación de mantenimientos preventivos")

elif menu == "Mantenimientos":
    st.title("🔧 Gestión de Mantenimientos")
    st.info("⚙️ Módulo en desarrollo - Sistema de mantenimientos preventivos y correctivos")

elif menu == "Inventario":
    st.title("📦 Control de Inventario")
    st.info("📋 Módulo en desarrollo - Gestión de inventario de equipos médicos")

elif menu == "Escáner QR" and rol_nivel in [4, 5, 6]:
    # Pasar información del rol al escáner
    if 'rol_nivel' not in st.session_state:
        st.session_state.rol_nivel = rol_nivel
    if 'rol_nombre' not in st.session_state:
        st.session_state.rol_nombre = rol_nombre
    
    mostrar_escaner_qr()

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
    mostrar_modulo_reportes()

elif menu == "Rendimiento Equipo":
    mostrar_rendimiento_equipo()

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