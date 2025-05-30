import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import json

# Configuración de credenciales
info = st.secrets["google_service_account"]
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
cliente = gspread.authorize(credenciales)

# IDs de las hojas de cálculo desde secrets
ASIGNACION_SHEET_ID = st.secrets["google_sheets"]["asignacion_tareas_id"]
BASE_DATOS_SHEET_ID = st.secrets["google_sheets"]["base_datos_id"]

def cargar_roles():
    """Carga los roles desde secrets"""
    try:
        roles_data = json.loads(st.secrets["roles_autorizados"]["data"])
        return roles_data
    except Exception as e:
        st.error(f"Error al cargar roles: {e}")
        return {}
    
def obtener_pasantes_disponibles(nivel_asignador):
    """Obtiene la lista de pasantes que pueden recibir tareas según el nivel del asignador"""
    roles_data = cargar_roles()
    pasantes_disponibles = []
    
    for email, info in roles_data.items():
        nombre, nivel, funciones = info[0], info[1], info[2]
        
        # Lógica de asignación según niveles
        if nivel_asignador >= 4:  # Ingeniero Junior y Jefe
            if nivel >= 2:  # Pueden asignar a Pasante 2 para arriba
                pasantes_disponibles.append({
                    'email': email,
                    'nombre': nombre,
                    'nivel': nivel,
                    'rol': nombre
                })
        elif nivel_asignador == 2:  # Pasante 2
            if nivel in [0, 1]:  # Solo pueden asignar a Pasante 0 y 1
                pasantes_disponibles.append({
                    'email': email,
                    'nombre': nombre,
                    'nivel': nivel,
                    'rol': nombre
                })
    
    # Ordenar por nivel
    pasantes_disponibles.sort(key=lambda x: x['nivel'])
    return pasantes_disponibles

@st.cache_data(ttl=300)  # Cache por 5 minutos
def cargar_equipos_base_datos():
    """Carga los equipos desde la hoja de base de datos con las columnas exactas de tu Excel"""
    try:
        # Abrir la hoja de base de datos
        hoja_base = cliente.open_by_key(BASE_DATOS_SHEET_ID).sheet1
        datos = hoja_base.get_all_records()
        
        # Debug: mostrar las primeras columnas para verificar nombres
        if datos:
            st.info(f"🔍 Columnas encontradas: {list(datos[0].keys())}")
        
        equipos = []
        for fila in datos:
            # Usar las columnas EXACTAS de tu base de datos según tu imagen
            equipo_info = {
                'numero_equipo': str(fila.get('Codigo nuevo', '')).strip(),  # Mantengo según tu código
                'numero_serie': str(fila.get('SERIE', '')).strip(),         # Mantengo según tu código
                'nombre_equipo': str(fila.get('EQUIPO', '')).strip(),       # Correcto
                'area': str(fila.get('UPSS/UPS', '')).strip(),              # Mantengo según tu código
                'ubicacion': str(fila.get('AMBIENTE', '')).strip(),             # Mantengo según tu código
                'marca': str(fila.get('MARCA', '')).strip(),                # Correcto
                'modelo': str(fila.get('MODELO', '')).strip()               # Correcto
            }
            
            # Solo agregar si tiene número de equipo válido
            if (equipo_info['numero_equipo'] and 
                equipo_info['numero_equipo'] != 'nan' and 
                equipo_info['numero_equipo'] != ''):
                equipos.append(equipo_info)
        
        return equipos
    
    except Exception as e:
        st.error(f"Error al cargar equipos: {e}")
        st.error("Verifique que la cuenta de servicio tenga acceso a la hoja de base de datos.")
        return []

def cargar_tareas_asignadas():
    """Carga las tareas ya asignadas"""
    try:
        hoja_tareas = cliente.open_by_key(ASIGNACION_SHEET_ID).sheet1
        datos = hoja_tareas.get_all_records()
        return datos
    except Exception as e:
        st.error(f"Error al cargar tareas: {e}")
        return []

def verificar_columnas_hoja():
    """Verifica y crea las columnas necesarias en la hoja de asignación"""
    try:
        hoja_tareas = cliente.open_by_key(ASIGNACION_SHEET_ID).sheet1
        
        # Columnas requeridas
        columnas_requeridas = [
            "Emisor", "Encargado", "Tarea", "Fecha", "Hora", "Estado",
            "Numero_Equipo", "Numero_Serie", "Nombre_Equipo", "Area_Equipo"
        ]
        
        # Verificar si la primera fila tiene headers
        try:
            primera_fila = hoja_tareas.row_values(1)
        except:
            primera_fila = []
        
        if not primera_fila or len(primera_fila) < len(columnas_requeridas):
            # Actualizar headers
            hoja_tareas.update('A1:J1', [columnas_requeridas])
            st.success("✅ Headers de la hoja actualizados correctamente")
        
        return True
        
    except Exception as e:
        st.error(f"Error al verificar columnas: {e}")
        return False

def asignar_nueva_tarea(datos_tarea):
    """Asigna una nueva tarea en la hoja de cálculo"""
    try:
        hoja_tareas = cliente.open_by_key(ASIGNACION_SHEET_ID).sheet1
        
        # Agregar nueva fila con timestamp
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        nueva_fila = [
            datos_tarea['emisor'],
            datos_tarea['encargado'],
            datos_tarea['tarea'],
            datos_tarea['fecha'],
            datos_tarea['hora'],
            datos_tarea['estado'],
            datos_tarea.get('numero_equipo', ''),
            datos_tarea.get('numero_serie', ''),
            datos_tarea.get('nombre_equipo', ''),
            datos_tarea.get('area_equipo', '')
        ]
        
        hoja_tareas.append_row(nueva_fila)
        
        cargar_equipos_base_datos.clear()
        
        return True
        
    except Exception as e:
        st.error(f"Error al asignar tarea: {e}")
        return False

def actualizar_estado_tarea(tarea_original, nuevo_estado):
    """Actualiza el estado de una tarea específica buscando por contenido"""
    try:
        hoja_tareas = cliente.open_by_key(ASIGNACION_SHEET_ID).sheet1
        todas_las_filas = hoja_tareas.get_all_values()
        
        # Buscar la fila que coincida con la tarea
        for i, fila in enumerate(todas_las_filas[1:], start=2):  # Empezar desde fila 2
            if (len(fila) >= 6 and 
                fila[0] == tarea_original.get('Emisor', '') and
                fila[1] == tarea_original.get('Encargado', '') and
                fila[2] == tarea_original.get('Tarea', '')):
                
                # Actualizar la columna de estado (columna F, índice 6)
                hoja_tareas.update_cell(i, 6, nuevo_estado)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error al actualizar estado: {e}")
        return False

def mostrar_asignacion_tareas():
    """Función principal para mostrar la interfaz de asignación de tareas"""
    
    # Obtener información del usuario
    email_usuario = st.session_state.get('email', '')
    nombre_usuario = st.session_state.get('name', '')
    nivel_usuario = st.session_state.get('rol_nivel', 0)
    
    st.title("📋 Asignación de Tareas")
    
    # Verificar permisos
    if nivel_usuario < 2:
        st.error("🚫 No tienes permisos para asignar tareas.")
        st.info("Solo Pasantes nivel 2 o superior pueden asignar tareas.")
        return
    
    # Verificar columnas de la hoja
    verificar_columnas_hoja()
    
    # Mostrar información del asignador
    nivel_info = {
        2: "Pasante 2 - Puede asignar a Pasantes 0 y 1",
        3: "Practicante - Puede asignar a Pasantes 2+",
        4: "Ingeniero Junior - Puede asignar a Pasantes 2+", 
        5: "Ingeniero Clínico - Puede asignar a todos"
    }
    
    st.info(f"👤 **{nombre_usuario}** | {nivel_info.get(nivel_usuario, f'Nivel {nivel_usuario}')}")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["➕ Nueva Tarea", "📊 Tareas Asignadas", "📈 Estadísticas"])
    
    with tab1:
        st.subheader("🆕 Asignar Nueva Tarea")
        
        # Obtener pasantes disponibles
        pasantes_disponibles = obtener_pasantes_disponibles(nivel_usuario)
        
        if not pasantes_disponibles:
            st.warning("⚠️ No hay pasantes disponibles para asignar tareas según tu nivel de autorización.")
            st.info("💡 Recuerda: Pasantes nivel 2 solo pueden asignar a niveles 0 y 1.")
            return
        
        # Cargar equipos
        with st.spinner("🔄 Cargando equipos de la base de datos..."):
            equipos = cargar_equipos_base_datos()
        
        if equipos:
            st.success(f"✅ Se cargaron {len(equipos)} equipos de la base de datos")
        else:
            st.warning("⚠️ No se pudieron cargar equipos o la base de datos está vacía")
        
        with st.form("form_nueva_tarea"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleccionar encargado
                opciones_encargados = [f"{p['nombre']} (Nivel {p['nivel']} - {p['rol']})" for p in pasantes_disponibles]
                encargado_seleccionado = st.selectbox(
                    "👤 Encargado de la Tarea",
                    opciones_encargados,
                    help="Selecciona quien realizará la tarea"
                )
                
                # Obtener datos del encargado seleccionado
                indice_encargado = opciones_encargados.index(encargado_seleccionado)
                encargado_data = pasantes_disponibles[indice_encargado]
                
                # Fecha y hora
                fecha_tarea = st.date_input("📅 Fecha Límite", min_value=date.today())
                hora_tarea = st.time_input("🕐 Hora Límite", value=datetime.now().time())
                
                # Estado inicial
                estado = st.selectbox("📊 Estado Inicial", ["Pendiente", "En Proceso"])
                
                # Tipo de tarea
                tipo_tarea = st.selectbox("🔧 Tipo de Tarea", [
                    "Mantenimiento Preventivo",
                    "Mantenimiento Correctivo",
                    "Inspección",
                    "Calibración",
                    "Reparación",
                    "Inventario",
                    "Documentación",
                    "Capacitación",
                    "Limpieza y Desinfección",
                    "Verificación de Funcionamiento",
                    "Otro"
                ])
            
            with col2:
                # Prioridad
                prioridad = st.selectbox("⚠️ Prioridad", ["Baja", "Media", "Alta", "Crítica"])
                
                # Selección de equipo (opcional)
                usar_equipo = st.checkbox("🏥 Asignar a equipo específico")
                
                numero_equipo = ""
                numero_serie = ""
                nombre_equipo = ""
                area_equipo = ""
                
                if usar_equipo:
                    if equipos:
                        # Filtros para equipos
                        areas_disponibles = sorted(list(set([eq['area'] for eq in equipos if eq['area']])))
                        area_filtro = st.selectbox("🏢 Filtrar por Área", ["Todas"] + areas_disponibles)
                        
                        equipos_filtrados = equipos
                        if area_filtro != "Todas":
                            equipos_filtrados = [eq for eq in equipos if eq['area'] == area_filtro]
                        
                        if equipos_filtrados:
                            # Crear opciones más descriptivas
                            opciones_equipos = []
                            for eq in equipos_filtrados:
                                opcion = f"{eq['numero_equipo']} - {eq['nombre_equipo']}"
                                if eq['area']:
                                    opcion += f" ({eq['area']})"
                                if eq['ubicacion']:
                                    opcion += f" - {eq['ubicacion']}"
                                opciones_equipos.append(opcion)
                            
                            equipo_seleccionado = st.selectbox("🔧 Seleccionar Equipo", opciones_equipos)
                            indice_equipo = opciones_equipos.index(equipo_seleccionado)
                            equipo_data = equipos_filtrados[indice_equipo]
                            
                            numero_equipo = equipo_data['numero_equipo']
                            numero_serie = equipo_data['numero_serie']
                            nombre_equipo = equipo_data['nombre_equipo']
                            area_equipo = equipo_data['area']
                            
                            # ✅ CORRECCIÓN: Mostrar detalles del equipo (SIN ERRORES DE COLUMNAS)
                            with st.expander("🔍 Detalles del Equipo Seleccionado"):
                                st.write(f"**📍 Área:** {equipo_data.get('area', 'N/A')}")
                                st.write(f"**📍 Ubicación:** {equipo_data.get('ubicacion', 'N/A')}")
                                st.write(f"**🏷️ N° Serie:** {equipo_data.get('numero_serie', 'N/A')}")
                                st.write(f"**🏭 Marca:** {equipo_data.get('marca', 'N/A')}")
                                st.write(f"**📱 Modelo:** {equipo_data.get('modelo', 'N/A')}")
                        else:
                            st.warning(f"⚠️ No se encontraron equipos en el área '{area_filtro}'.")
                    else:
                        st.error("❌ No se pudo cargar la base de datos de equipos.")
                        st.info("Verifica que la cuenta de servicio tenga acceso a la hoja de base de datos.")
            
            # Descripción de la tarea
            tarea_descripcion = st.text_area(
                "📝 Descripción Detallada de la Tarea",
                placeholder="Describe paso a paso lo que debe realizar el encargado...",
                height=120
            )
            
            # Comentarios adicionales
            comentarios = st.text_area(
                "💬 Instrucciones Especiales",
                placeholder="Materiales necesarios, precauciones, horarios específicos, etc.",
                height=80
            )
            
            # Botón para enviar
            submitted = st.form_submit_button("📤 Asignar Tarea", type="primary", use_container_width=True)
            
            if submitted:
                if not tarea_descripcion.strip():
                    st.error("❌ La descripción de la tarea es obligatoria.")
                else:
                    # Preparar descripción completa de la tarea
                    tarea_completa = f"[{prioridad}] {tipo_tarea}: {tarea_descripcion}"
                    if comentarios.strip():
                        tarea_completa += f" | Instrucciones: {comentarios}"
                    
                    datos_tarea = {
                        'emisor': nombre_usuario,
                        'encargado': encargado_data['nombre'],
                        'tarea': tarea_completa,
                        'fecha': fecha_tarea.strftime('%d/%m/%Y'),
                        'hora': hora_tarea.strftime('%H:%M'),
                        'estado': estado,
                        'numero_equipo': numero_equipo,
                        'numero_serie': numero_serie,
                        'nombre_equipo': nombre_equipo,
                        'area_equipo': area_equipo
                    }
                    
                    # Asignar la tarea
                    with st.spinner("📤 Asignando tarea..."):
                        if asignar_nueva_tarea(datos_tarea):
                            st.success("✅ ¡Tarea asignada exitosamente!")
                            st.balloons()
                            # Limpiar cache
                            cargar_equipos_base_datos.clear()
                            st.rerun()
                        else:
                            st.error("❌ Error al asignar la tarea. Intenta nuevamente.")
    
    with tab2:
        st.subheader("📊 Tareas Asignadas")
        
        # Cargar tareas
        with st.spinner("🔄 Cargando tareas..."):
            tareas = cargar_tareas_asignadas()
        
        if not tareas:
            st.info("📝 No hay tareas asignadas aún.")
            st.info("💡 Usa la pestaña 'Nueva Tarea' para crear la primera asignación.")
            return
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filtro_estado = st.selectbox("🔍 Estado", 
                                       ["Todos", "Pendiente", "En Proceso", "Completada", "Cancelada"])
        
        with col2:
            # Solo mostrar tareas asignadas por el usuario actual si no es jefe
            if nivel_usuario < 5:
                mostrar_solo_mias = st.checkbox("Solo mis asignaciones", value=True)
            else:
                mostrar_solo_mias = st.checkbox("Solo mis asignaciones", value=False)
        
        with col3:
            encargados_unicos = list(set([t.get('Encargado', '') for t in tareas if t.get('Encargado', '')]))
            filtro_encargado = st.selectbox("👤 Encargado", ["Todos"] + sorted(encargados_unicos))
        
        with col4:
            ordenar_por = st.selectbox("📊 Ordenar", ["Fecha ↓", "Fecha ↑", "Estado", "Prioridad"])
        
        # Filtrar tareas
        tareas_filtradas = tareas.copy()
        
        if filtro_estado != "Todos":
            tareas_filtradas = [t for t in tareas_filtradas if t.get('Estado', '') == filtro_estado]
        
        if filtro_encargado != "Todos":
            tareas_filtradas = [t for t in tareas_filtradas if t.get('Encargado', '') == filtro_encargado]
        
        if mostrar_solo_mias:
            tareas_filtradas = [t for t in tareas_filtradas if t.get('Emisor', '') == nombre_usuario]
        
        # Mostrar contador
        st.info(f"📊 Mostrando {len(tareas_filtradas)} de {len(tareas)} tareas")
        
        # Mostrar tareas en cards
        if tareas_filtradas:
            for i, tarea in enumerate(tareas_filtradas):
                estado_color = {
                    'Pendiente': '🟡',
                    'En Proceso': '🔵', 
                    'Completada': '🟢',
                    'Cancelada': '🔴'
                }.get(tarea.get('Estado', ''), '⚪')
                
                # Determinar prioridad
                tarea_texto = tarea.get('Tarea', '')
                prioridad_emoji = '🔴' if '[Crítica]' in tarea_texto else '🟠' if '[Alta]' in tarea_texto else '🟡' if '[Media]' in tarea_texto else '🟢'
                
                with st.expander(f"{estado_color} {prioridad_emoji} {tarea_texto[:60]}... | Encargado: {tarea.get('Encargado', '')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**👤 Emisor:** {tarea.get('Emisor', '')}")
                        st.write(f"**🎯 Encargado:** {tarea.get('Encargado', '')}")
                        st.write(f"**📅 Fecha Límite:** {tarea.get('Fecha', '')}")
                        st.write(f"**🕐 Hora Límite:** {tarea.get('Hora', '')}")
                    
                    with col2:
                        st.write(f"**📊 Estado:** {estado_color} {tarea.get('Estado', '')}")
                        if tarea.get('Numero_Equipo'):
                            st.write(f"**🔧 Equipo:** {tarea.get('Numero_Equipo', '')} - {tarea.get('Nombre_Equipo', '')}")
                            if tarea.get('Numero_Serie'):
                                st.write(f"**🏷️ Serie:** {tarea.get('Numero_Serie', '')}")
                            if tarea.get('Area_Equipo'):
                                st.write(f"**📍 Área:** {tarea.get('Area_Equipo', '')}")
                    
                    st.markdown("**📝 Descripción de la Tarea:**")
                    st.markdown(f"_{tarea.get('Tarea', '')}_")
                    
                    # Botón para cambiar estado (solo para emisor o jefe)
                    if tarea.get('Emisor', '') == nombre_usuario or nivel_usuario >= 5:
                        col_estado1, col_estado2 = st.columns(2)
                        
                        with col_estado1:
                            nuevo_estado = st.selectbox(
                                "Cambiar Estado:",
                                ["Pendiente", "En Proceso", "Completada", "Cancelada"],
                                index=["Pendiente", "En Proceso", "Completada", "Cancelada"].index(tarea.get('Estado', 'Pendiente')),
                                key=f"estado_{i}"
                            )
                        
                        with col_estado2:
                            if st.button(f"✅ Actualizar", key=f"btn_{i}", type="secondary"):
                                if actualizar_estado_tarea(tarea, nuevo_estado):
                                    st.success("✅ Estado actualizado exitosamente")
                                    cargar_equipos_base_datos.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ Error al actualizar el estado")
        else:
            st.info("🔍 No se encontraron tareas con los filtros seleccionados.")
            st.info("💡 Ajusta los filtros o crea nuevas tareas.")
    
    with tab3:
        st.subheader("📈 Estadísticas y Reportes")
        
        # Cargar tareas para estadísticas
        tareas = cargar_tareas_asignadas()
        
        if tareas:
            # Métricas generales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_tareas = len(tareas)
                st.metric("📊 Total Tareas", total_tareas)
            
            with col2:
                pendientes = len([t for t in tareas if t.get('Estado', '') == 'Pendiente'])
                st.metric("⏳ Pendientes", pendientes)
            
            with col3:
                completadas = len([t for t in tareas if t.get('Estado', '') == 'Completada'])
                st.metric("✅ Completadas", completadas)
            
            with col4:
                if total_tareas > 0:
                    porcentaje_completadas = (completadas / total_tareas) * 100
                    st.metric("📊 % Completadas", f"{porcentaje_completadas:.1f}%")
            
            # Gráficos
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                # Gráfico de distribución por estado
                estados = {}
                for tarea in tareas:
                    estado = tarea.get('Estado', 'Sin Estado')
                    estados[estado] = estados.get(estado, 0) + 1
                
                if estados:
                    st.subheader("📊 Por Estado")
                    df_estados = pd.DataFrame(list(estados.items()), columns=['Estado', 'Cantidad'])
                    st.bar_chart(df_estados.set_index('Estado'))
            
            with col_graf2:
                # Estadísticas por encargado
                encargados = {}
                for tarea in tareas:
                    encargado = tarea.get('Encargado', 'Sin Encargado')
                    encargados[encargado] = encargados.get(encargado, 0) + 1
                
                if encargados:
                    st.subheader("👥 Por Encargado")
                    df_encargados = pd.DataFrame(list(encargados.items()), columns=['Encargado', 'Tareas'])
                    st.bar_chart(df_encargados.set_index('Encargado'))
            
            # Resumen de equipos más asignados
            if any(t.get('Nombre_Equipo') for t in tareas):
                st.subheader("🔧 Equipos Más Asignados")
                equipos_tareas = {}
                for tarea in tareas:
                    if tarea.get('Nombre_Equipo'):
                        equipo = f"{tarea.get('Numero_Equipo', '')} - {tarea.get('Nombre_Equipo', '')}"
                        equipos_tareas[equipo] = equipos_tareas.get(equipo, 0) + 1
                
                df_equipos = pd.DataFrame(list(equipos_tareas.items()), columns=['Equipo', 'Tareas Asignadas'])
                df_equipos = df_equipos.sort_values('Tareas Asignadas', ascending=False).head(10)
                st.dataframe(df_equipos, use_container_width=True)
            
            # Estadísticas por área
            if any(t.get('Area_Equipo') for t in tareas):
                st.subheader("🏢 Tareas por Área")
                areas_tareas = {}
                for tarea in tareas:
                    if tarea.get('Area_Equipo'):
                        area = tarea.get('Area_Equipo', '')
                        areas_tareas[area] = areas_tareas.get(area, 0) + 1
                
                df_areas = pd.DataFrame(list(areas_tareas.items()), columns=['Área', 'Tareas'])
                st.bar_chart(df_areas.set_index('Área'))
        
        else:
            st.info("📊 No hay datos suficientes para mostrar estadísticas.")
            st.info("💡 Asigna algunas tareas para ver métricas y reportes.")

# Función de compatibilidad para main.py
def mostrar_modulo_asignacion():
    """Función de compatibilidad para main.py"""
    mostrar_asignacion_tareas()