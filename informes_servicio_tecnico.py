import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, time
import openpyxl
from openpyxl.styles import Font
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Configurar Google Drive API
@st.cache_resource
def configurar_drive_api():
    """Configura la API de Google Drive"""
    info = st.secrets["google_service_account"]
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    drive_service = build('drive', 'v3', credentials=credenciales)
    return drive_service

# Descargar plantilla desde Google Sheets
def descargar_plantilla_drive(drive_service, plantilla_id):
    """Descarga la plantilla desde Google Sheets como Excel"""
    try:
        request = drive_service.files().export_media(
            fileId=plantilla_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_io.seek(0)
        return file_io
        
    except Exception as e:
        st.error(f"Error descargando plantilla: {e}")
        return None

# Subir archivo a Google Drive
def subir_a_drive(drive_service, archivo_buffer, nombre_archivo, carpeta_id):
    """Sube un archivo a Google Drive"""
    try:
        archivo_buffer.seek(0)
        
        file_metadata = {
            'name': nombre_archivo,
            'parents': [carpeta_id]
        }
        
        media = MediaIoBaseUpload(
            archivo_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,webViewLink'
        ).execute()
        
        return file
        
    except Exception as e:
        st.error(f"Error subiendo archivo: {e}")
        return None

# Cargar datos desde Google Sheets
@st.cache_data
def cargar_datos():
    info = st.secrets["google_service_account"]
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
    credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    cliente = gspread.authorize(credenciales)
    hoja = cliente.open("Base de datos").sheet1
    datos = hoja.get_all_records()
    return pd.DataFrame(datos)

# FUNCIÓN PRINCIPAL QUE SE LLAMA DESDE MAIN.PY
def mostrar_informes_servicio_tecnico():
    """Función principal del módulo de informes de servicio técnico"""
    
    # IDs de Google Drive
    PLANTILLA_ID = "1QsSeISaWS_mTnMGsfhlWcTEuE948X8I7"
    CARPETA_INFORMES_ID = "1W5K0aOUOrr5qabn-mFzi5GrlAZ1xgY3i"

    # Título del módulo
    st.title("🩺 Registro de Servicio Técnico - Equipos Médicos")
    
    # Información del usuario
    if hasattr(st.session_state, 'name') and hasattr(st.session_state, 'rol_nombre'):
        st.info(f"👨‍🔧 **Técnico:** {st.session_state.name} | **Rol:** {st.session_state.rol_nombre}")

    # Configurar Google Drive
    drive_service = configurar_drive_api()

    # Cargar base de datos
    df = cargar_datos()

    # ============== SELECTOR DE EQUIPOS MEJORADO ==============
    st.markdown("### 🔍 Selección de Equipo")
    
    # Convertir DataFrame a lista de diccionarios para facilitar el manejo
    equipos = []
    for _, row in df.iterrows():
        equipo = {
            'codigo_nuevo': row.get('Codigo nuevo', ''),
            'equipo': row.get('EQUIPO', ''),
            'marca': row.get('MARCA', ''),
            'modelo': row.get('MODELO', ''),
            'serie': row.get('SERIE', ''),
            'area': row.get('AREA', ''),  # Asume que tienes esta columna
            'ubicacion': row.get('UBICACION', ''),  # Asume que tienes esta columna
        }
        equipos.append(equipo)

    # Método de selección de equipo
    metodo_seleccion = st.radio(
        "¿Cómo deseas seleccionar el equipo?",
        ["🔍 Selector inteligente", "⌨️ Código manual"],
        horizontal=True
    )

    # Variables para almacenar datos del equipo
    marca = modelo = equipo_nombre = serie = codigo_equipo = ""
    area_equipo = ubicacion_equipo = ""

    if metodo_seleccion == "🔍 Selector inteligente":
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
                opcion = f"{eq['codigo_nuevo']} - {eq['equipo']}"
                if eq['area']:
                    opcion += f" ({eq['area']})"
                if eq['ubicacion']:
                    opcion += f" - {eq['ubicacion']}"
                opciones_equipos.append(opcion)
            
            equipo_seleccionado = st.selectbox("🔧 Seleccionar Equipo", opciones_equipos)
            indice_equipo = opciones_equipos.index(equipo_seleccionado)
            equipo_data = equipos_filtrados[indice_equipo]
            
            # Extraer datos del equipo seleccionado
            codigo_equipo = equipo_data['codigo_nuevo']
            equipo_nombre = equipo_data['equipo']
            marca = equipo_data['marca']
            modelo = equipo_data['modelo']
            serie = equipo_data['serie']
            area_equipo = equipo_data['area']
            ubicacion_equipo = equipo_data['ubicacion']
            
            # Mostrar detalles del equipo seleccionado
            with st.expander("🔍 Detalles del Equipo Seleccionado", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**🏷️ Código:** {codigo_equipo}")
                    st.write(f"**⚙️ Equipo:** {equipo_nombre}")
                    st.write(f"**🏭 Marca:** {marca}")
                with col2:
                    st.write(f"**📱 Modelo:** {modelo}")
                    st.write(f"**🔢 Serie:** {serie}")
                    st.write(f"**📍 Área:** {area_equipo}")
                    st.write(f"**📍 Ubicación:** {ubicacion_equipo}")
        else:
            st.warning("⚠️ No se encontraron equipos para el área seleccionada")
    
    else:  # Código manual
        codigo_input = st.text_input("🔍 Ingrese el código del equipo (Ej: EQU-0000001)")
        equipo_info = df[df["Codigo nuevo"] == codigo_input]
        
        if not equipo_info.empty:
            equipo_row = equipo_info.iloc[0]
            codigo_equipo = codigo_input
            marca = equipo_row["MARCA"]
            modelo = equipo_row["MODELO"]
            equipo_nombre = equipo_row["EQUIPO"]
            serie = equipo_row["SERIE"]
            area_equipo = equipo_row.get("AREA", "")
            ubicacion_equipo = equipo_row.get("UBICACION", "")
            
            st.success(f"✅ **Equipo encontrado:** {equipo_nombre}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Marca", value=marca, disabled=True)
                st.text_input("Equipo", value=equipo_nombre, disabled=True)
            with col2:
                st.text_input("Modelo", value=modelo, disabled=True)
                st.text_input("Serie", value=serie, disabled=True)
        else:
            if codigo_input:
                st.warning("⚠️ Código no encontrado. Verifica el código del equipo.")

    # ============== FORMULARIO DE SERVICIO ==============
    st.markdown("### 🏥 Información del Servicio")
    col1, col2 = st.columns(2)
    with col1:
        sede = st.selectbox("🏥 Sede", [
            "Clínica Médica Cayetano Heredia",
            "Policlínico Lince",
            "Centro de diagnóstico por imágenes",
            "Anexo de Logística"
        ])
        
        tipo_servicio = st.selectbox("🔧 Tipo de servicio", [
            "Mantenimiento Preventivo", 
            "Mantenimiento Correctivo", 
            "Inspección", 
            "Otro"
        ])

    with col2:
        upss = st.selectbox("🏢 UPSS", [
            "Diagnóstico por imágenes",
            "Emergencias",
            "Unidad de Cuidados Intensivos",
            "Centro Quirúrgico",
            "Centro Obstétrico",
            "Consulta Externa",
            "Laboratorio",
            "Anatomía Patológica"
        ])
        
        estado = st.selectbox("📊 Estado", ["Operativo", "Inoperativo", "Regular"])

    # ============== FECHAS Y HORAS ==============
    st.markdown("### 📅 Fechas y Horarios")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("📅 Fecha de inicio", datetime.now())
        hora_inicio = st.time_input("🕒 Hora de inicio", time(8, 0))
    with col2:
        fecha_fin = st.date_input("📅 Fecha de fin", datetime.now())
        hora_fin = st.time_input("🕒 Hora de fin", time(17, 0))

    inicio_servicio = datetime.combine(fecha_inicio, hora_inicio)
    fin_servicio = datetime.combine(fecha_fin, hora_fin)

    # Validación de fechas
    if fin_servicio <= inicio_servicio:
        st.warning("⚠️ La fecha de fin debe ser posterior a la fecha de inicio")

    # ============== CAMPOS DE TEXTO LIBRES ==============
    st.markdown("### 📝 Detalles del Servicio")
    inconveniente = st.text_area("🛠 Inconveniente reportado / Motivo de servicio", 
                                height=100, 
                                placeholder="Describe el problema reportado o el motivo del servicio técnico...")
    
    actividades = st.text_area("✅ Actividades realizadas", 
                              height=150,
                              placeholder="Detalla paso a paso las actividades realizadas durante el servicio...")
    
    resultado = st.text_area("📋 Resultado final y observaciones", 
                            height=100,
                            placeholder="Indica el resultado del servicio y cualquier observación importante...")

    # ============== CAMPOS ADICIONALES ==============
    st.markdown("### 📋 Información Adicional")
    col1, col2 = st.columns(2)
    with col1:
        tecnico_responsable = st.text_input("👨‍🔧 Técnico responsable", 
                                          value=st.session_state.get('name', ''))
        repuestos_utilizados = st.text_area("🔧 Repuestos/Materiales utilizados", 
                                          height=80,
                                          placeholder="Lista los repuestos o materiales utilizados...")
    with col2:
        costo_servicio = st.number_input("💰 Costo del servicio (S/)", min_value=0.0, step=0.01)
        tiempo_estimado = st.number_input("⏱️ Tiempo de servicio (horas)", min_value=0.0, step=0.5)

    # ============== CÓDIGO DEL INFORME ==============
    siglas_dict = {
        "Mantenimiento Preventivo": "MP",
        "Mantenimiento Correctivo": "MC",
        "Inspección": "I",
        "Otro": "O"
    }

    if equipo_nombre and modelo and serie:
        fecha_str = fecha_inicio.strftime("%Y%m%d")
        sigla_servicio = siglas_dict.get(tipo_servicio, "O")
        codigo_informe = f"{fecha_str}-{sigla_servicio}-{modelo}-{serie}"
        st.text_input("📄 Código del informe generado", value=codigo_informe, disabled=True)
    else:
        codigo_informe = ""

    # ============== GENERAR INFORME ==============
    st.markdown("### 📤 Generar Informe")

    if st.button("🚀 Generar y Guardar Informe Técnico", type="primary", use_container_width=True):
        if not codigo_informe:
            st.error("❌ Por favor selecciona un equipo válido primero")
            st.stop()
        
        if not inconveniente.strip() or not actividades.strip():
            st.warning("⚠️ Por favor completa los campos obligatorios: inconveniente y actividades realizadas")
            st.stop()
        
        # Indicadores de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. Descargar plantilla
            status_text.text("📥 Descargando plantilla desde Google Drive...")
            progress_bar.progress(20)
            
            plantilla_buffer = descargar_plantilla_drive(drive_service, PLANTILLA_ID)
            
            if not plantilla_buffer:
                st.error("❌ Error al descargar la plantilla")
                st.stop()
            
            # 2. Procesar Excel
            status_text.text("📝 Completando datos en el informe...")
            progress_bar.progress(40)
            
            wb = openpyxl.load_workbook(plantilla_buffer)
            ws = wb.active
            fuente = Font(name="Albert Sans", size=8)

            # Llenar TODOS los datos en las celdas correspondientes
            ws["J6"] = codigo_informe
            ws["J6"].font = fuente
            ws["C5"] = sede
            ws["C5"].font = fuente
            ws["C6"] = upss
            ws["C6"].font = fuente
            ws["C7"] = tipo_servicio
            ws["C7"].font = fuente
            ws["F10"] = equipo_nombre
            ws["F10"].font = fuente
            ws["I10"] = marca
            ws["I10"].font = fuente
            ws["K10"] = modelo
            ws["K10"].font = fuente
            ws["M10"] = serie
            ws["M10"].font = fuente
            ws["B12"] = inicio_servicio.strftime("%d/%m/%Y %H:%M")
            ws["B12"].font = fuente
            ws["D12"] = fin_servicio.strftime("%d/%m/%Y %H:%M")
            ws["D12"].font = fuente
            ws["F12"] = estado
            ws["F12"].font = fuente
            ws["B15"] = inconveniente
            ws["B15"].font = fuente
            ws["B20"] = actividades
            ws["B20"].font = fuente
            ws["B29"] = resultado
            ws["B29"].font = fuente
            
            # Campos adicionales (ajusta las celdas según tu plantilla)
            if tecnico_responsable:
                ws["B35"] = f"Técnico: {tecnico_responsable}"  # Ajusta la celda
                ws["B35"].font = fuente
            
            if repuestos_utilizados:
                ws["B37"] = f"Repuestos: {repuestos_utilizados}"  # Ajusta la celda
                ws["B37"].font = fuente
                
            if costo_servicio > 0:
                ws["B39"] = f"Costo: S/ {costo_servicio:.2f}"  # Ajusta la celda
                ws["B39"].font = fuente
            
            # 3. Guardar en buffer
            progress_bar.progress(60)
            archivo_final = io.BytesIO()
            wb.save(archivo_final)
            archivo_final.seek(0)
            
            # 4. Subir a Google Drive
            status_text.text("☁️ Guardando en Google Drive...")
            progress_bar.progress(80)
            
            nombre_archivo = f"informe_servicio_{codigo_informe}.xlsx"
            resultado_subida = subir_a_drive(drive_service, archivo_final, nombre_archivo, CARPETA_INFORMES_ID)
            
            if resultado_subida:
                progress_bar.progress(100)
                status_text.text("✅ ¡Informe generado exitosamente!")
                
                st.success(f"🎉 **¡Informe de servicio técnico generado y guardado exitosamente!**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📁 **Archivo:** `{nombre_archivo}`")
                    st.info(f"🆔 **ID Drive:** `{resultado_subida['id']}`")
                
                with col2:
                    # Enlaces útiles
                    if 'webViewLink' in resultado_subida:
                        st.markdown(f"🔗 [Ver en Google Drive]({resultado_subida['webViewLink']})")
                    
                    # Descarga local
                    archivo_final.seek(0)
                    st.download_button(
                        label="⬇️ Descargar copia local",
                        data=archivo_final,
                        file_name=nombre_archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                # Botón para crear nuevo informe
                if st.button("🔄 Crear Nuevo Informe", type="secondary"):
                    st.rerun()
                    
            else:
                st.error("❌ Error al guardar en Google Drive")
                
        except Exception as e:
            st.error(f"❌ Error procesando el informe: {e}")
            progress_bar.empty()
            status_text.empty()

    # Footer informativo
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px;'>
        🏥 <strong>Sistema de Informes de Servicio Técnico - MEDIFLOW</strong><br>
        Todos los informes se guardan automáticamente en Google Drive con respaldo completo
    </div>
    """, unsafe_allow_html=True)

# Función standalone para testing (opcional)
if __name__ == "__main__":
    mostrar_informes_servicio_tecnico()