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

# CONFIGURACIÓN CRÍTICA - AL INICIO DEL ARCHIVO
st.set_page_config(
    page_title="MEDIFLOW",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS GLOBAL CRÍTICO - JUSTO DESPUÉS
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        background: transparent !important;
    }
    
    .reportview-container .main {
        background: transparent !important;
    }
    
    .main > div:first-child {
        display: none !important;
    }
    
    /* CSS actualizado para Sidebar más ancho */
    [data-testid="stSidebar"] {
        width: 400px !important;
        min-width: 400px !important;
    }

    [data-testid="stSidebar"] > div {
        width: 400px !important;
        min-width: 400px !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Ajustar el contenido principal */
    .main .block-container {
        padding-left: 2rem !important;
        max-width: none !important;
    }

    /* Mejorar el option_menu específicamente */
    .nav-pills {
        --bs-nav-pills-border-radius: 10px;
    }

    .nav-pills .nav-link {
        padding: 15px 20px !important;
        margin-bottom: 10px !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        transition: all 0.3s ease !important;
    }

    .nav-pills .nav-link.active {
        background-color: #DC143C !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 20px rgba(220, 20, 60, 0.4) !important;
        transform: translateX(8px) !important;
    }

    .nav-pills .nav-link:not(.active) {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .nav-pills .nav-link:not(.active):hover {
        background-color: rgba(220, 20, 60, 0.1) !important;
        color: #DC143C !important;
        transform: translateX(5px) !important;
        border-color: rgba(220, 20, 60, 0.3) !important;
    }

    /* Mejorar los iconos del menú */
    .nav-link svg {
        margin-right: 15px !important;
        font-size: 20px !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Título del menú */
    .nav-pills-header {
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        margin-bottom: 20px !important;
        padding: 0 10px !important;
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
    # CSS corregido - eliminar contenedores de imagen
    st.markdown("""
    <style>
    /* Eliminar elementos específicos de Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .stDeployButton {
        display: none !important;
    }
    
    footer {
        display: none !important;
    }
    
    /* Eliminar contenedores y fondos de imagen */
    .stImage {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stImage > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Eliminar cualquier contenedor que rodee la imagen */
    div[data-testid="stImage"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Asegurar que las columnas también sean transparentes */
    .stColumn {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stColumn > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stApp {
        background: 
            radial-gradient(ellipse 800px 600px at 15% 85%, 
                rgba(180, 38, 65, 0.25) 0%, 
                rgba(180, 38, 65, 0.1) 30%,
                transparent 60%),
            radial-gradient(ellipse 900px 500px at 85% 15%, 
                rgba(255, 195, 49, 0.3) 0%, 
                rgba(255, 195, 49, 0.15) 30%,
                transparent 60%),
            radial-gradient(ellipse 600px 800px at 70% 60%, 
                rgba(180, 38, 65, 0.15) 0%, 
                transparent 50%),
            radial-gradient(ellipse 700px 400px at 30% 40%, 
                rgba(255, 195, 49, 0.2) 0%, 
                transparent 50%),
            linear-gradient(135deg, 
                #ffffff 0%, 
                rgba(255, 195, 49, 0.08) 50%, 
                #ffffff 100%),
            #ffffff !important;
        background-size: 120% 120%, 130% 130%, 110% 110%, 115% 115%, 100% 100%, 100% 100% !important;
        animation: waveFlow 20s ease-in-out infinite !important;
        min-height: 100vh !important;
    }
     
    @keyframes waveFlow {
        0%, 100% { 
            background-position: 0% 0%, 100% 0%, 70% 60%, 30% 40%, 0% 0%, 0% 0%; 
        }
        33% { 
            background-position: 10% 15%, 90% 10%, 60% 50%, 40% 30%, 0% 0%, 0% 0%; 
        }
        66% { 
            background-position: 5% 25%, 95% 5%, 80% 70%, 20% 50%, 0% 0%, 0% 0%; 
        }
    }
                      
    /* Efecto de brillo */
    .login-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
        z-index: 1;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        50% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        100% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    }
    
    /* Hover effect */
    .login-container:hover {
        transform: translateY(-10px) scale(1.02) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 20px 60px 0 rgba(31, 38, 135, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Botón con gradiente y efectos */
    .stButton > button {
        background: linear-gradient(135deg, #b42641 0%, #ff6b6b 50%, #ffc331 100%) !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 18px 40px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: white !important;
        width: 100% !important;
        margin-top: 30px !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        box-shadow: 0 8px 25px rgba(180, 38, 65, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
        z-index: 10 !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(180, 38, 65, 0.4) !important;
        background: linear-gradient(135deg, #a0213a 0%, #ff5252 50%, #e6b02e 100%) !important;
    }
    
    /* Logo container con efectos - asegurar que esté por encima */
    .logo-container {
        margin-bottom: 40px !important;
        padding: 20px !important;
        position: relative !important;
        z-index: 5 !important;
        background: transparent !important;
    }
    
    .logo-container::after {
        content: '';
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #b42641, #ffc331, #b42641);
        border-radius: 2px;
        animation: pulse 2s ease-in-out infinite;
        z-index: 6;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; transform: translateX(-50%) scaleX(1); }
        50% { opacity: 1; transform: translateX(-50%) scaleX(1.2); }
    }
    
    /* Texto con sombras suaves */
    .content-text {
        z-index: 5 !important;
        position: relative !important;
    }
    
    .content-text h1 {
        color: rgba(44, 62, 80, 1) !important;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 25px !important;
        font-weight: 700 !important;
        font-size: 36px !important;
        letter-spacing: -0.5px !important;
    }
    
    .content-text p {
        color: rgba(52, 73, 94, 1) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Asegurar que todos los contenidos estén por encima del efecto de brillo */
    .logo-container *, 
    .content-text *, 
    .stButton *,
    .stImage *,
    .stColumn * {
        position: relative !important;
        z-index: 10 !important;
    }
    </style>
    """, unsafe_allow_html=True)
         
    # Espacio superior
    st.write("")
    st.write("")
         
    # Centrar contenido
    col1, col2, col3 = st.columns([1, 2, 1])
         
    with col2:
        # Logo con tu código específico para centrar
        try:
            # Usar columnas internas para centrar la imagen
            img_col1, img_col2, img_col3 = st.columns([1.3, 2, 1.5])
            with img_col2:
                st.image("static/MEDIFLOW LOGO.png", width=260)
        except:
            st.error("No se pudo cargar el logo")
                 
        # Contenido elegante
        st.markdown("""
        <div class="content-text" style="text-align: center; margin: 25px 0;">
            <h1>¡Bienvenido!</h1>
            <p style="font-size: 18px; line-height: 1.7; margin-bottom: 20px; font-weight: 400;">
                Accede al sistema integral de gestión para equipos médicos
            </p>
            <p style="font-size: 16px; font-weight: 500;">
                Usa tu cuenta autorizada para continuar
            </p>
        </div>
        """, unsafe_allow_html=True)
                 
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
    # Información del usuario con estilo Cayetano (SIN COLUMNAS)
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #B71C1C 0%, #DC143C 100%);
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.3);
        text-align: center;
        color: white;
        width: 100%;
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
    
    # Menú principal (SIN COLUMNAS)
    menu = option_menu(
        menu_title="Menú Principal",
        options=menus_usuario,
        icons=iconos_menu,
        default_index=0,
        styles={
            "container": {"padding": "0!important", "width": "100%"},
            "icon": {"color": "#DC143C", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "0px",
                "padding": "15px 20px",
                "width": "100%"
            },
            "nav-link-selected": {"background-color": "#DC143C"},
        }
    )

# Contenido principal según la selección del menú
if menu == "Inicio":
    st.markdown(f"## 👋 Hola, {name}")
    
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
st.markdown("🏥 **MEDIFLOW v1.0** | Enfocado en mantenimiento preventivo y gestión técnica")