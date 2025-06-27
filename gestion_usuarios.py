import streamlit as st
import json
from datetime import datetime

def cargar_roles_actuales():
    """Carga los roles actuales desde secrets"""
    try:
        roles_data = json.loads(st.secrets["roles_autorizados"]["data"])
        return roles_data
    except Exception as e:
        st.error(f"Error al cargar roles: {e}")
        return {}

def guardar_roles_en_session(nuevos_roles):
    """Guarda temporalmente los roles en session_state para mostrar cambios"""
    st.session_state['roles_temp'] = nuevos_roles

def mostrar_instrucciones_secrets():
    """Muestra las instrucciones para actualizar secrets"""
    st.markdown("""
    ### 📋 Instrucciones para actualizar Secrets:
    
    1. **Ve a la configuración de tu app en Streamlit Cloud**
    2. **Busca la sección "Secrets"**
    3. **Reemplaza la sección `[roles_autorizados]` con:**
    
    ```toml
    [roles_autorizados]
    data = '''AQUÍ_VA_EL_JSON'''
    ```
    
    4. **Guarda los cambios y reinicia la app**
    """)

def validar_email(email):
    """Valida formato básico de email"""
    import re
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def obtener_siguiente_nivel_sugerido(roles_actuales):
    """Sugiere el siguiente nivel basado en los existentes"""
    if not roles_actuales:
        return 0
    
    niveles_usados = [info[1] for info in roles_actuales.values()]
    for nivel in range(0, 6):
        if nivel not in niveles_usados:
            return nivel
    return 0

def mostrar_gestion_usuarios():
    """Función principal para gestión de usuarios"""
    
    # Verificar permisos
    nivel_usuario = st.session_state.get('rol_nivel', 0)
    nombre_usuario = st.session_state.get('name', '')
    
    if nivel_usuario < 1:
        st.error("🚫 **Acceso Denegado**")
        st.warning("Solo el Ingeniero Clínico (Nivel 5) puede gestionar usuarios.")
        return
    
    st.title("👥 Gestión de Usuarios")
    st.info(f"👤 **{nombre_usuario}** | Ingeniero Clínico - Gestión completa de usuarios")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Agregar Usuario", 
        "👥 Usuarios Actuales", 
        "✏️ Editar Usuario",
        "📋 Exportar Config"
    ])
    
    # Cargar roles actuales
    roles_actuales = cargar_roles_actuales()
    
    # Usar roles temporales si existen (para mostrar cambios)
    if 'roles_temp' in st.session_state:
        roles_mostrar = st.session_state['roles_temp']
        st.success("⚠️ **Cambios pendientes** - Se muestran los cambios realizados (aún no guardados en secrets)")
    else:
        roles_mostrar = roles_actuales
    
    with tab1:
        st.subheader("➕ Agregar Nuevo Usuario")
        
        with st.form("form_nuevo_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Datos básicos
                nombre_completo = st.text_input(
                    "👤 Nombre Completo",
                    placeholder="Ej: María García López",
                    help="Nombre y apellidos completos"
                )
                
                email_nuevo = st.text_input(
                    "📧 Correo Electrónico",
                    placeholder="ejemplo@empresa.com",
                    help="Email institucional del usuario"
                )
                
                # Validación de email en tiempo real
                if email_nuevo and not validar_email(email_nuevo):
                    st.error("❌ Formato de email inválido")
                
                if email_nuevo and email_nuevo in roles_mostrar:
                    st.error("❌ Este email ya está registrado")
            
            with col2:
                # Configuración de rol
                nivel_usuario_nuevo = st.selectbox(
                    "🎯 Nivel de Usuario",
                    options=[0, 1, 2, 3, 4, 5],
                    index=obtener_siguiente_nivel_sugerido(roles_mostrar),
                    help="Nivel de autorización del usuario"
                )
                
                # Descripción automática del nivel
                niveles_descripcion = {
                    0: "👶 Pasante Nivel 0 - Acceso básico",
                    1: "🌱 Pasante Nivel 1 - Funciones limitadas", 
                    2: "📈 Pasante Nivel 2 - Puede asignar tareas a niveles 0-1",
                    3: "🎓 Practicante - Funciones avanzadas",
                    4: "👨‍🔧 Ingeniero Junior - Gestión de equipos",
                    5: "👨‍💼 Ingeniero Clínico - Acceso completo"
                }
                
                st.info(niveles_descripcion.get(nivel_usuario_nuevo, ""))
                
                # Funciones específicas
                funciones_disponibles = [
                    "Consultar equipos",
                    "Generar QR",
                    "Escanear QR", 
                    "Crear informes",
                    "Asignar tareas",
                    "Gestionar usuarios",
                    "Ver dashboard KPIs",
                    "Gestionar cronogramas",
                    "Análisis de rendimiento"
                ]
                
                funciones_seleccionadas = st.multiselect(
                    "⚙️ Funciones Específicas",
                    funciones_disponibles,
                    default=funciones_disponibles[:min(3, nivel_usuario_nuevo + 2)],
                    help="Selecciona las funciones que tendrá este usuario"
                )
            
            # Información adicional
            st.markdown("### 📝 Información Adicional")
            col3, col4 = st.columns(2)
            
            with col3:
                areas_asignadas = st.multiselect(
                    "🏢 Área de Trabajo",
                    ["UCI", "Quirófanos", "Emergencia", "Hospitalización", "Imagenología", "Laboratorio", "Mantenimiento", "Administración"],
                    help="Selecciona una o más áreas donde trabajará el usuario"
                )
                
                turno = st.selectbox(
                    "🕐 Turno de Trabajo", 
                    ["Mañana", "Tarde", "Noche", "Rotativo"],
                    help="Horario de trabajo habitual"
                )
            
            with col4:
                telefono = st.text_input(
                    "📱 Teléfono (Opcional)",
                    placeholder="+51 999 999 999"
                )
                
                fecha_inicio = st.date_input(
                    "📅 Fecha de Inicio",
                    value=datetime.now().date(),
                    help="Fecha de incorporación"
                )
            
            comentarios = st.text_area(
                "💬 Comentarios Adicionales",
                placeholder="Observaciones especiales, restricciones, etc.",
                height=80
            )
            
            # Botón submit
            submitted = st.form_submit_button("➕ Agregar Usuario", type="primary", use_container_width=True)
            
            if submitted:
                # Validaciones
                errores = []
                
                if not nombre_completo.strip():
                    errores.append("❌ El nombre completo es obligatorio")
                
                if not email_nuevo.strip():
                    errores.append("❌ El email es obligatorio")
                elif not validar_email(email_nuevo):
                    errores.append("❌ Formato de email inválido")
                elif email_nuevo in roles_mostrar:
                    errores.append("❌ Este email ya está registrado")
                
                if not funciones_seleccionadas:
                    errores.append("❌ Debe seleccionar al menos una función")
                
                # Mostrar errores o procesar
                if errores:
                    for error in errores:
                        st.error(error)
                else:
                    # Crear nuevo usuario
                    nuevo_usuario = [
                        nombre_completo.strip(),
                        nivel_usuario_nuevo,
                        funciones_seleccionadas,
                        {
                            "area": areas_asignadas,
                            "turno": turno,
                            "telefono": telefono,
                            "fecha_inicio": fecha_inicio.strftime('%d/%m/%Y'),
                            "comentarios": comentarios,
                            "creado_por": nombre_usuario,
                            "fecha_creacion": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        }
                    ]
                    
                    # Agregar a roles temporales
                    roles_nuevos = roles_mostrar.copy()
                    roles_nuevos[email_nuevo] = nuevo_usuario
                    guardar_roles_en_session(roles_nuevos)
                    
                    st.success(f"✅ Usuario **{nombre_completo}** agregado exitosamente!")
                    st.balloons()
                    st.rerun()
    
    with tab2:
        st.subheader("👥 Usuarios Actuales")
        
        if not roles_mostrar:
            st.info("👤 No hay usuarios registrados aún.")
            return
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_nivel = st.selectbox(
                "🎯 Filtrar por Nivel",
                ["Todos"] + [f"Nivel {i}" for i in range(6)]
            )
        
        with col2:
            # Obtener áreas únicas
            areas_usuarios = set()
            for info in roles_mostrar.values():
                if len(info) > 3 and isinstance(info[3], dict):
                    areas_usuario = info[3].get('areas', info[3].get('area', []))
                    if isinstance(areas_usuario, list):
                        areas_usuarios.update(areas_usuario)
                    else:
                        areas_usuarios.add(areas_usuario)   
            
            filtro_area = st.selectbox(
                "🏢 Filtrar por Área",
                ["Todas"] + sorted(list(areas_usuarios))
            )

        with col3:
            buscar_texto = st.text_input("🔍 Buscar usuario", placeholder="Nombre o email...")
        
        # Mostrar usuarios
        usuarios_filtrados = []
        
        for email, info in roles_mostrar.items():
            nombre = info[0]
            nivel = info[1]
            funciones = info[2] if len(info) > 2 else []
            extra_info = info[3] if len(info) > 3 and isinstance(info[3], dict) else {}
            
            # Aplicar filtros
            if filtro_nivel != "Todos" and f"Nivel {nivel}" != filtro_nivel:
                continue
                
            if filtro_area != "Todas":
                areas_usuario = extra_info.get('areas', extra_info.get('area', []))
                if isinstance(areas_usuario, list):
                    if filtro_area not in areas_usuario:
                        continue
                else:
                    if areas_usuario != filtro_area:
                        continue
            
            if buscar_texto:
                if (buscar_texto.lower() not in nombre.lower() and 
                    buscar_texto.lower() not in email.lower()):
                    continue
            
            usuarios_filtrados.append((email, info))
        
        # Mostrar resultados
        st.info(f"📊 Mostrando {len(usuarios_filtrados)} de {len(roles_mostrar)} usuarios")
        
        for email, info in usuarios_filtrados:
            nombre = info[0]
            nivel = info[1] 
            funciones = info[2] if len(info) > 2 else []
            extra_info = info[3] if len(info) > 3 else {}
            
            # Color por nivel
            color_nivel = {
                0: "🟢", 1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🟣"
            }.get(nivel, "⚪")
            
            with st.expander(f"{color_nivel} **{nombre}** (Nivel {nivel}) - {email}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📧 Email:** {email}")
                    st.write(f"**🎯 Nivel:** {nivel} - {niveles_descripcion.get(nivel, '')}")
                    st.write(f"**⚙️ Funciones:** {', '.join(funciones)}")
                
                with col2:
                    if isinstance(extra_info, dict):
                        areas_usuario = extra_info.get('areas', extra_info.get('area', []))
                        if isinstance(areas_usuario, list):
                            areas_texto = ', '.join(areas_usuario) if areas_usuario else 'N/A'
                        else:
                            areas_texto = areas_usuario if areas_usuario else 'N/A'
                        
                        st.write(f"**🏢 Áreas:** {areas_texto}")
                        st.write(f"**🕐 Turno:** {extra_info.get('turno', 'N/A')}")
                        st.write(f"**📱 Teléfono:** {extra_info.get('telefono', 'N/A')}")
                        st.write(f"**📅 Inicio:** {extra_info.get('fecha_inicio', 'N/A')}")
                
                # Botones de acción
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button(f"✏️ Editar", key=f"edit_{email}", type="secondary"):
                        st.session_state['usuario_editar'] = email
                        st.session_state['tab_activo'] = 2
                        st.rerun()
                
                with col_btn2:
                    if email != st.session_state.get('email'):  # No puede eliminarse a sí mismo
                        if st.button(f"🗑️ Eliminar", key=f"del_{email}", type="secondary"):
                            # Confirmar eliminación
                            st.session_state[f'confirmar_eliminar_{email}'] = True
                            st.rerun()
                    else:
                        st.info("👤 No puedes eliminarte a ti mismo")
                
                # Confirmar eliminación
                if st.session_state.get(f'confirmar_eliminar_{email}', False):
                    st.warning(f"⚠️ **¿Estás seguro de eliminar a {nombre}?**")
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        if st.button("✅ Sí, eliminar", key=f"conf_del_{email}", type="primary"):
                            roles_nuevos = roles_mostrar.copy()
                            del roles_nuevos[email]
                            guardar_roles_en_session(roles_nuevos)
                            del st.session_state[f'confirmar_eliminar_{email}']
                            st.success(f"🗑️ Usuario {nombre} eliminado")
                            st.rerun()
                    
                    with col_conf2:
                        if st.button("❌ Cancelar", key=f"canc_del_{email}"):
                            del st.session_state[f'confirmar_eliminar_{email}']
                            st.rerun()
    
    with tab3:
        st.subheader("✏️ Editar Usuario")
        
        usuario_editar = st.session_state.get('usuario_editar')
        
        if not usuario_editar:
            st.info("👈 Selecciona un usuario de la pestaña 'Usuarios Actuales' para editarlo")
        elif usuario_editar not in roles_mostrar:
            st.error("❌ Usuario no encontrado")
            st.button("🔄 Volver", on_click=lambda: st.session_state.pop('usuario_editar', None))
        else:
            # Cargar datos del usuario
            info_actual = roles_mostrar[usuario_editar]
            nombre_actual = info_actual[0]
            nivel_actual = info_actual[1]
            funciones_actuales = info_actual[2] if len(info_actual) > 2 else []
            extra_actual = info_actual[3] if len(info_actual) > 3 and isinstance(info_actual[3], dict) else {}
            
            st.info(f"✏️ Editando: **{nombre_actual}** ({usuario_editar})")
            
            with st.form("form_editar_usuario"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre_edit = st.text_input("👤 Nombre Completo", value=nombre_actual)
                    nivel_edit = st.selectbox("🎯 Nivel", options=[0,1,2,3,4,5], index=nivel_actual)
                    
                    funciones_edit = st.multiselect(
                        "⚙️ Funciones",
                        funciones_disponibles,
                        default=funciones_actuales
                    )                

                with col2:

                    # Obtener áreas actuales (con compatibilidad hacia atrás)
                    areas_actuales = extra_actual.get('areas', [])
                    if not areas_actuales and extra_actual.get('area'):
                        areas_actuales = [extra_actual.get('area')]

                    areas_edit = st.multiselect(
                        "🏢 Áreas",
                        ["UCI", "Quirófanos", "Emergencia", "Hospitalización", "Imagenología", "Laboratorio", "Mantenimiento", "Administración"],
                        default=areas_actuales,
                        help="Selecciona una o más áreas donde trabajará el usuario"
                    )
                    
                    turno_edit = st.selectbox(
                        "🕐 Turno",
                        ["Mañana", "Tarde", "Noche", "Rotativo"],
                        index=["Mañana", "Tarde", "Noche", "Rotativo"].index(extra_actual.get('turno', 'Mañana'))
                    )
                    
                    telefono_edit = st.text_input("📱 Teléfono", value=extra_actual.get('telefono', ''))
                
                comentarios_edit = st.text_area(
                    "💬 Comentarios",
                    value=extra_actual.get('comentarios', ''),
                    height=80
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                        # Actualizar usuario
                        usuario_actualizado = [
                            nombre_edit.strip(),
                            nivel_edit,
                            funciones_edit,
                            {
                                "area": areas_edit,
                                "turno": turno_edit,
                                "telefono": telefono_edit,
                                "fecha_inicio": extra_actual.get('fecha_inicio', datetime.now().strftime('%d/%m/%Y')),
                                "comentarios": comentarios_edit,
                                "creado_por": extra_actual.get('creado_por', 'Sistema'),
                                "fecha_creacion": extra_actual.get('fecha_creacion', datetime.now().strftime('%d/%m/%Y %H:%M:%S')),
                                "editado_por": nombre_usuario,
                                "fecha_edicion": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                            }
                        ]
                        
                        roles_nuevos = roles_mostrar.copy()
                        roles_nuevos[usuario_editar] = usuario_actualizado
                        guardar_roles_en_session(roles_nuevos)
                        
                        st.success(f"💾 Usuario **{nombre_edit}** actualizado exitosamente!")
                        st.session_state.pop('usuario_editar', None)
                        st.rerun()
                
                with col_btn2:
                    if st.form_submit_button("❌ Cancelar"):
                        st.session_state.pop('usuario_editar', None)
                        st.rerun()
    
    with tab4:
        st.subheader("📋 Exportar Configuración")
        
        if 'roles_temp' in st.session_state:
            st.success("✨ **Configuración actualizada lista para exportar**")
            roles_exportar = st.session_state['roles_temp']
        else:
            st.info("📋 Configuración actual (sin cambios pendientes)")
            roles_exportar = roles_actuales
        
        # Mostrar resumen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Total Usuarios", len(roles_exportar))
        
        with col2:
            niveles_count = {}
            for info in roles_exportar.values():
                nivel = info[1]
                niveles_count[nivel] = niveles_count.get(nivel, 0) + 1
            nivel_mas_comun = max(niveles_count, key=niveles_count.get) if niveles_count else 0
            st.metric("📊 Nivel Más Común", f"Nivel {nivel_mas_comun}")
        
        with col3:
            if 'roles_temp' in st.session_state:
                cambios = len(st.session_state['roles_temp']) - len(roles_actuales)
                st.metric("🔄 Cambios Pendientes", f"+{cambios}" if cambios > 0 else cambios)
        
        # JSON para secrets
        st.markdown("### 🔧 Configuración para Secrets:")
        
        json_output = json.dumps(roles_exportar, ensure_ascii=False, indent=2)
        
        st.code(json_output, language="json")
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📥 Descargar JSON",
                json_output,
                file_name=f"roles_usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                type="primary"
            )
        
        with col2:
            if st.button("📋 Copiar al Portapapeles", type="secondary"):
                st.code(f'[roles_autorizados]\ndata = \'\'\'{json_output}\'\'\'', language="toml")
                st.success("📋 Copiado! Pégalo en la configuración de Secrets")
        
        with col3:
            if 'roles_temp' in st.session_state:
                if st.button("🗑️ Descartar Cambios", type="secondary"):
                    st.session_state.pop('roles_temp', None)
                    st.success("🗑️ Cambios descartados")
                    st.rerun()
        
        # Instrucciones detalladas
        mostrar_instrucciones_secrets()

# Función de compatibilidad para main.py
def mostrar_modulo_gestion_usuarios():
    """Función de compatibilidad para main.py"""
    mostrar_gestion_usuarios()