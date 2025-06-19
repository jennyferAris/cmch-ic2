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
    # CSS con efectos de partículas
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
    
    /* Fondo con gradiente suave */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
        overflow: hidden;
    }
    
    /* Partículas flotantes */
    .stApp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(255, 195, 49, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(180, 38, 65, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-30px) rotate(120deg); }
        66% { transform: translateY(20px) rotate(240deg); }
    }
    
    .block-container {
        padding-top: 3rem !important;
        position: relative;
        z-index: 1;
    }
    
    /* Contenedor principal con efecto de cristal */
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 70px 60px;
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.25),
            0 0 0 1px rgba(255, 255, 255, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        margin: 40px auto;
        max-width: 500px;
        text-align: center;
        position: relative;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Efectos de hover suaves */
    .login-container:hover {
        transform: translateY(-15px);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 35px 70px -12px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }
    
    /* Botón con gradiente médico */
    .stButton > button {
        background: linear-gradient(45deg, #b42641, #d63384, #ffc331);
        border: none;
        border-radius: 25px;
        padding: 20px 45px;
        font-weight: 600;
        font-size: 17px;
        transition: all 0.4s ease;
        color: white;
        width: 100%;
        margin-top: 35px;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 10px 30px rgba(180, 38, 65, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(180, 38, 65, 0.4);
        background: linear-gradient(45deg, #a0213a, #c42a69, #e6b02e);
    }
    
    /* Logo container con animación */
    .logo-container {
        margin-bottom: 50px;
        padding: 25px;
        position: relative;
        animation: logoFloat 6s ease-in-out infinite;
    }
    
    @keyframes logoFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .logo-container::after {
        content: '';
        position: absolute;
        bottom: 15px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 5px;
        background: linear-gradient(90deg, 
            rgba(180, 38, 65, 0.8), 
            rgba(255, 195, 49, 0.8), 
            rgba(180, 38, 65, 0.8));
        border-radius: 3px;
        box-shadow: 0 2px 10px rgba(180, 38, 65, 0.3);
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
        <div style="text-align: center; margin: 30px 0;">
            <h1 style="color: #b42641; margin-bottom: 30px; font-weight: 800; font-size: 38px; letter-spacing: -1px;">
                ¡Bienvenido a MEDIFLOW!
            </h1>
            <p style="font-size: 19px; color: #4a5568; line-height: 1.8; margin-bottom: 25px; font-weight: 400;">
                Tu plataforma integral para la gestión profesional de equipos médicos
            </p>
            <p style="font-size: 16px; color: #718096; font-weight: 500;">
                Inicia sesión para acceder al sistema
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