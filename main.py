import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
import json

st.set_page_config(page_title="Sistema de Inventario", layout="wide")

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
            "nivel": roles_data[email][1]
        }
    return None

# Función para mostrar la pantalla de login
def mostrar_login():
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>🏥 PLATAFORMA DEL DEPARTAMENTO DE INGENIERÍA CLÍNICA</h1>
        <h2>Clínica Médica Cayetano Heredia</h2>
        <br>
        <h3>Sistema de Inventario de Equipos Médicos</h3>
        <br>
        <p style="font-size: 18px; color: #666;">
            Bienvenido al sistema de gestión de inventario médico.<br>
            Para continuar, inicia sesión con tu cuenta autorizada.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Crear columnas para centrar el botón
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔑 Ingresar con Google", 
                    type="primary", 
                    use_container_width=True,
                    help="Haz clic para iniciar sesión con tu cuenta de Google"):
            st.login("google")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px; 
                background-color: #f0f2f6; border-radius: 10px;">
        <h4>ℹ️ Información importante</h4>
        <p>• Solo las cuentas autorizadas pueden acceder al sistema</p>
        <p>• Contacta al administrador si necesitas acceso</p>
        <p>• Asegúrate de usar tu cuenta institucional</p>
    </div>
    """, unsafe_allow_html=True)

# Verificar si el usuario está logueado
if not st.user.is_logged_in:
    mostrar_login()
    st.stop()

# Cargar roles desde secrets
roles_data = cargar_roles()

# El resto del código se ejecuta solo si el usuario está logueado
st.title("PLATAFORMA DEL DEPARTAMENTO DE INGENIERÍA CLÍNICA")

email = st.user.email
name = st.user.name
rol_info = obtener_info_rol(email, roles_data)

# Acceso denegado si el correo no está en la lista
if rol_info is None:
    st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
    st.info(f"📧 Cuenta utilizada: {email}")
    st.warning("Si crees que esto es un error, contacta al administrador del sistema.")
    
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

# Sidebar con menú
with st.sidebar:
    st.markdown(f"""
    👤 **{name}**  
    📧 {email}  
    🛡️ Rol: `{rol_nombre}`  
    🏆 Nivel: `{rol_nivel}`
    """)
    
    # Separador visual
    st.markdown("---")
    
    menu = option_menu(
        menu_title="Menú Principal",
        options=["Inicio", "Ver Base de Datos", "Perfil", "Configuración"],
        icons=["house", "database", "person", "gear"],
        default_index=0
    )

# Sección de inicio
if menu == "Inicio":
    st.title("🏥 Bienvenido al Sistema de Inventario")
    
    # Mensaje personalizado según el nivel del usuario
    if rol_nivel >= 4:
        st.success(f"👨‍💼 Bienvenido {rol_nombre}. Tienes acceso completo al sistema.")
    elif rol_nivel >= 2:
        st.info(f"👨‍🔧 Bienvenido {rol_nombre}. Tienes acceso de consulta y edición.")
    else:
        st.info(f"👨‍🎓 Bienvenido {rol_nombre}. Tienes acceso de consulta.")
    
    st.write("Navega usando el menú lateral para ver y gestionar los equipos médicos.")
    
    # Mostrar permisos según el nivel
    with st.expander("Ver permisos de tu rol"):
        if rol_nivel >= 5:
            st.write("✅ Administración completa del sistema")
            st.write("✅ Gestión de usuarios y roles")
            st.write("✅ Acceso a todas las funcionalidades")
        elif rol_nivel >= 4:
            st.write("✅ Gestión completa de inventario")
            st.write("✅ Generar reportes avanzados")
            st.write("✅ Configuración del sistema")
        elif rol_nivel >= 3:
            st.write("✅ Editar información de equipos")
            st.write("✅ Generar reportes básicos")
            st.write("✅ Consultar base de datos")
        else:
            st.write("✅ Consultar base de datos")
            st.write("❌ Edición limitada")

# Sección de base de datos
elif menu == "Ver Base de Datos":
    mostrar_base_datos()

# Perfil
elif menu == "Perfil":
    st.title("👤 Perfil del Usuario")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.user.picture:
            st.image(st.user.picture, width=150)
        else:
            st.info("Sin foto de perfil")
    
    with col2:
        st.markdown(f"""
        **Información Personal:**
        - **Nombre:** {name}
        - **Correo:** {email}
        - **Rol:** {rol_nombre}
        - **Nivel de acceso:** {rol_nivel}
        """)
    
    # Información adicional del token
    with st.expander("Ver información técnica completa"):
        st.json({
            "user_info": st.user.to_dict(),
            "role_info": rol_info
        })

# Configuración
elif menu == "Configuración":
    st.title("⚙️ Configuración")
    
    if rol_nivel >= 4:
        st.success("Tienes permisos para modificar la configuración del sistema.")
        st.write("Aquí irán las opciones de configuración personalizadas.")
        
        # Ejemplo de configuraciones según el nivel
        if rol_nivel >= 5:
            st.subheader("Configuración de Administrador")
            st.write("- Gestión de usuarios")
            st.write("- Configuración de la base de datos")
            st.write("- Respaldos del sistema")
        
        st.subheader("Configuración Personal")
        st.write("- Preferencias de visualización")
        st.write("- Notificaciones")
        st.write("- Idioma")
    else:
        st.warning("No tienes permisos suficientes para acceder a la configuración.")
        st.info("Contacta a un administrador si necesitas cambiar alguna configuración.")

# Logout
if st.sidebar.button("Cerrar sesión"):
    st.logout()