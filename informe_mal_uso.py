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
from PIL import Image
import base64

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

# Función para escribir en celdas de forma segura
def escribir_celda_segura(ws, celda, valor, fuente=None):
    """Escribe en una celda manejando celdas fusionadas"""
    try:
        # Verificar si la celda está fusionada
        cell = ws[celda]
        if hasattr(cell, 'coordinate'):
            # Buscar si esta celda es parte de un rango fusionado
            for merged_range in ws.merged_cells.ranges:
                if cell.coordinate in merged_range:
                    # Es una celda fusionada, usar la celda superior izquierda
                    top_left = merged_range.start_cell
                    top_left.value = valor
                    if fuente:
                        top_left.font = fuente
                    return
        
        # No está fusionada, escribir normalmente
        cell.value = valor
        if fuente:
            cell.font = fuente
            
    except Exception as e:
        st.warning(f"No se pudo escribir en la celda {celda}: {e}")

# Función para crear informe de mal uso
def crear_informe_mal_uso_completo(drive_service, plantilla_id, carpeta_destino_id, datos_formulario):
    """Crea copia de plantilla de mal uso, llena datos y sube archivo final a Drive"""
    try:
        # 1. Crear copia de la plantilla
        nombre_copia = f"Informe_MalUso_{datos_formulario['codigo_informe']}"
        copy_metadata = {
            'name': nombre_copia,
            'parents': [carpeta_destino_id]
        }
        
        copia = drive_service.files().copy(
            fileId=plantilla_id,
            body=copy_metadata,
            fields='id,name,webViewLink'
        ).execute()
        
        copia_id = copia['id']
        
        # 2. Descargar la copia para editar
        file_metadata = drive_service.files().get(fileId=copia_id, fields='mimeType').execute()
        mime_type = file_metadata.get('mimeType')
        
        if mime_type == 'application/vnd.google-apps.spreadsheet':
            request = drive_service.files().export_media(
                fileId=copia_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            request = drive_service.files().get_media(fileId=copia_id)
        
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_io.seek(0)
        
        # 3. Editar el archivo Excel con los datos
        wb = openpyxl.load_workbook(file_io)
        ws = wb.active
        fuente = Font(name="Albert Sans", size=8)

        # Llenar datos usando la función segura - AJUSTAR CELDAS SEGÚN TU TEMPLATE
        escribir_celda_segura(ws, "J6", datos_formulario['codigo_informe'], fuente)  # Código de informe
        escribir_celda_segura(ws, "C5", datos_formulario['sede'], fuente)            # Sede
        escribir_celda_segura(ws, "C6", datos_formulario['upss'], fuente)            # UPSS
        escribir_celda_segura(ws, "C7", datos_formulario['servicio'], fuente)        # Servicio
        
        # Información del equipo y personal
        escribir_celda_segura(ws, "B10", datos_formulario['personal_asignado'], fuente)  # Personal asignado
        escribir_celda_segura(ws, "F10", datos_formulario['equipo_nombre'], fuente)     # Nombre del equipo
        escribir_celda_segura(ws, "I10", datos_formulario['marca'], fuente)            # Marca
        escribir_celda_segura(ws, "K10", datos_formulario['modelo'], fuente)           # Modelo
        escribir_celda_segura(ws, "M10", datos_formulario['serie'], fuente)            # Serie
        
        # Inconveniente reportado
        escribir_celda_segura(ws, "B13", datos_formulario['inconveniente'], fuente)
        
        # Información de imágenes en la celda B19
        if datos_formulario.get('num_imagenes', 0) > 0:
            texto_imagenes = f"Se adjuntan {datos_formulario['num_imagenes']} imagen(es) como evidencia del incidente."
            escribir_celda_segura(ws, "B19", texto_imagenes, fuente)
        
        # 4. Guardar archivo editado
        archivo_editado = io.BytesIO()
        wb.save(archivo_editado)
        archivo_editado.seek(0)
        
        # 5. Actualizar archivo en Drive
        media = MediaIoBaseUpload(
            archivo_editado,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        resultado_final = drive_service.files().update(
            fileId=copia_id,
            media_body=media,
            fields='id,name,webViewLink'
        ).execute()
        
        return resultado_final, archivo_editado
        
    except Exception as e:
        st.error(f"Error creando informe de mal uso: {e}")
        import traceback
        st.error(f"Detalles del error: {traceback.format_exc()}")
        return None, None

# Función alternativa para debugging - inspeccionar celdas fusionadas
def inspeccionar_plantilla(drive_service, plantilla_id):
    """Función para inspeccionar qué celdas están fusionadas en la plantilla"""
    try:
        # Crear copia temporal
        copy_metadata = {'name': 'temp_inspection'}
        copia = drive_service.files().copy(fileId=plantilla_id, body=copy_metadata).execute()
        copia_id = copia['id']
        
        # Descargar
        request = drive_service.files().get_media(fileId=copia_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        file_io.seek(0)
        
        # Inspeccionar
        wb = openpyxl.load_workbook(file_io)
        ws = wb.active
        
        st.write("### 🔍 Celdas fusionadas encontradas:")
        for merged_range in ws.merged_cells.ranges:
            st.write(f"- Rango fusionado: {merged_range}")
            
        # Eliminar copia temporal
        drive_service.files().delete(fileId=copia_id).execute()
        
    except Exception as e:
        st.error(f"Error inspeccionando plantilla: {e}")

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

# Función para gestionar imágenes (nueva funcionalidad)
def gestionar_imagenes():
    """Maneja la captura y subida de imágenes"""
    st.markdown("### 📷 Imágenes Referenciales")
    
    # Inicializar session state para imágenes si no existe
    if 'imagenes_capturadas' not in st.session_state:
        st.session_state.imagenes_capturadas = []
    
    # Pestañas para diferentes métodos de captura
    tab1, tab2, tab3 = st.tabs(["📷 Tomar Foto", "📁 Subir Archivo", "🖼️ Imágenes Capturadas"])
    
    with tab1:
        st.markdown("#### 📸 Capturar con Cámara")
        
        # Widget de cámara
        foto_capturada = st.camera_input("Toma una foto del incidente")
        
        if foto_capturada is not None:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Mostrar vista previa
                imagen = Image.open(foto_capturada)
                st.image(imagen, caption="Vista previa de la foto capturada", width=300)
            
            with col2:
                # Botón para guardar la foto
                if st.button("💾 Guardar Foto", key="guardar_camera"):
                    # Convertir imagen a bytes
                    img_bytes = foto_capturada.getvalue()
                    
                    # Generar nombre único
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_imagen = f"foto_camara_{timestamp}.jpg"
                    
                    # Guardar en session state
                    st.session_state.imagenes_capturadas.append({
                        'nombre': nombre_imagen,
                        'bytes': img_bytes,
                        'tipo': 'camera',
                        'timestamp': timestamp
                    })
                    
                    st.success(f"✅ Foto guardada: {nombre_imagen}")
                    st.rerun()
    
    with tab2:
        st.markdown("#### 📁 Subir desde Dispositivo")
        
        # File uploader tradicional
        archivos_subidos = st.file_uploader(
            "Selecciona imágenes desde tu dispositivo",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Puedes seleccionar múltiples imágenes a la vez"
        )
        
        if archivos_subidos:
            for archivo in archivos_subidos:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Mostrar vista previa
                    imagen = Image.open(archivo)
                    st.image(imagen, caption=archivo.name, width=300)
                
                with col2:
                    # Botón para agregar a la colección
                    if st.button(f"➕ Agregar", key=f"add_{archivo.name}"):
                        # Verificar si ya existe
                        existe = any(img['nombre'] == archivo.name for img in st.session_state.imagenes_capturadas)
                        
                        if not existe:
                            st.session_state.imagenes_capturadas.append({
                                'nombre': archivo.name,
                                'bytes': archivo.getvalue(),
                                'tipo': 'upload',
                                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
                            })
                            st.success(f"✅ Agregada: {archivo.name}")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Ya existe: {archivo.name}")
    
    with tab3:
        st.markdown("#### 🖼️ Imágenes Guardadas")
        
        if st.session_state.imagenes_capturadas:
            st.success(f"📊 **Total de imágenes:** {len(st.session_state.imagenes_capturadas)}")
            
            # Mostrar todas las imágenes guardadas
            cols = st.columns(3)
            
            for i, img_data in enumerate(st.session_state.imagenes_capturadas):
                with cols[i % 3]:
                    # Mostrar imagen
                    imagen = Image.open(io.BytesIO(img_data['bytes']))
                    st.image(imagen, caption=img_data['nombre'], width=200)
                    
                    # Información adicional
                    st.caption(f"🕒 {img_data['timestamp']}")
                    st.caption(f"📱 Fuente: {'Cámara' if img_data['tipo'] == 'camera' else 'Archivo'}")
                    
                    # Botón para eliminar
                    if st.button(f"🗑️ Eliminar", key=f"del_{i}"):
                        st.session_state.imagenes_capturadas.pop(i)
                        st.rerun()
            
            # Botones de gestión
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ **Limpiar Todas**", use_container_width=True):
                    st.session_state.imagenes_capturadas = []
                    st.success("✅ Todas las imágenes eliminadas")
                    st.rerun()
            
            with col2:
                if st.button("💾 **Descargar ZIP**", use_container_width=True):
                    import zipfile
                    
                    # Crear ZIP con todas las imágenes
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for img_data in st.session_state.imagenes_capturadas:
                            zip_file.writestr(img_data['nombre'], img_data['bytes'])
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ Descargar ZIP",
                        data=zip_buffer,
                        file_name=f"imagenes_incidente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )
        else:
            st.info("📝 No hay imágenes guardadas aún. Usa las pestañas anteriores para capturar o subir imágenes.")
    
    return st.session_state.imagenes_capturadas

# FUNCIÓN PRINCIPAL PARA INFORMES DE MAL USO
def mostrar_informes_mal_uso():
    """Función principal del módulo de informes de mal uso"""
    
    # IDs de Google Drive - CAMBIAR POR TUS IDs REALES
    PLANTILLA_MAL_USO_ID = "1mW0gzxNAtyd02FSN15Ru39IUZZAwWe-o"  
    CARPETA_MAL_USO_ID = "1wD8J5xy8cXCLStOAvx7MxOFGHluVVolf"     

    st.title("📋 Informe de Mal Uso - MEDIFLOW")

    # Información del usuario
    if hasattr(st.session_state, 'name') and hasattr(st.session_state, 'rol_nombre'):
        st.info(f"👨‍💼 **Personal:** {st.session_state.name} | **Rol:** {st.session_state.rol_nombre}")

    # Configurar Google Drive
    drive_service = configurar_drive_api()

    # Botón para debugging (opcional)
    if st.checkbox("🔧 Modo Debug - Inspeccionar Plantilla"):
        if st.button("Inspeccionar celdas fusionadas"):
            inspeccionar_plantilla(drive_service, PLANTILLA_MAL_USO_ID)

    # Cargar base de datos
    df = cargar_datos()

    # ============== SELECTOR DE EQUIPOS ==============
    st.markdown("### 🔍 Selección de Equipo/Accesorio/Repuesto")
    
    equipos = []
    for _, row in df.iterrows():
        equipo = {
            'codigo_nuevo': row.get('Codigo nuevo', ''),
            'equipo': row.get('EQUIPO', ''),
            'marca': row.get('MARCA', ''),
            'modelo': row.get('MODELO', ''),
            'serie': row.get('SERIE', ''),
            'area': row.get('AREA', ''),
            'ubicacion': row.get('UBICACION', ''),
        }
        equipos.append(equipo)

    metodo_seleccion = st.radio(
        "¿Cómo deseas seleccionar el equipo?",
        ["🔍 Selector inteligente", "⌨️ Código manual"],
        horizontal=True
    )

    marca = modelo = equipo_nombre = serie = codigo_equipo = ""
    area_equipo = ubicacion_equipo = ""

    if metodo_seleccion == "🔍 Selector inteligente":
        areas_disponibles = sorted(list(set([eq['area'] for eq in equipos if eq['area']])))
        area_filtro = st.selectbox("🏢 Filtrar por Área", ["Todas"] + areas_disponibles)
        
        equipos_filtrados = equipos
        if area_filtro != "Todas":
            equipos_filtrados = [eq for eq in equipos if eq['area'] == area_filtro]
        
        if equipos_filtrados:
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
            
            codigo_equipo = equipo_data['codigo_nuevo']
            equipo_nombre = equipo_data['equipo']
            marca = equipo_data['marca']
            modelo = equipo_data['modelo']
            serie = equipo_data['serie']
            area_equipo = equipo_data['area']
            ubicacion_equipo = equipo_data['ubicacion']
            
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

    # ============== INFORMACIÓN DEL INFORME ==============
    st.markdown("### 🏥 Información del Informe")
    
    col1, col2 = st.columns(2)
    with col1:
        sede = st.selectbox("🏥 Sede", [
            "Clínica Médica Cayetano Heredia",
            "Policlínico Lince", 
            "Centro de diagnóstico por imágenes",
            "Anexo de Logística"
        ])
        
        servicio = st.selectbox("🔧 Servicio", [
            "Informe de Mal Uso",
            "Reporte de Incidente",
            "Evaluación de Daños",
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
        
        personal_asignado = st.text_input("👨‍💼 Nombre del personal asignado", 
                                        value=st.session_state.get('name', ''))

    # ============== DETALLES DEL MAL USO ==============
    st.markdown("### 📝 Detalles del Mal Uso")
    
    inconveniente = st.text_area(
        "🚨 Inconveniente reportado / Motivo del servicio", 
        height=150,
        placeholder="Describe detalladamente el mal uso, incidente o daño reportado..."
    )

    # ============== IMÁGENES REFERENCIALES (NUEVA FUNCIONALIDAD) ==============
    imagenes_guardadas = gestionar_imagenes()

    # ============== CÓDIGO DEL INFORME ==============
    fecha_actual = datetime.now()
    if equipo_nombre and modelo and serie:
        fecha_str = fecha_actual.strftime("%Y%m%d")
        codigo_informe = f"{fecha_str}-MU-{modelo}-{serie}"  # MU = Mal Uso
        st.text_input("📄 Código del informe", value=codigo_informe, disabled=True)
    else:
        codigo_informe = ""

    # ============== BOTÓN PARA GENERAR INFORME ==============
    st.markdown("---")
    
    if st.button("📤 **SUBIR INFORME DE MAL USO A DRIVE**", type="primary", use_container_width=True):
        if not codigo_informe:
            st.error("❌ Por favor selecciona un equipo válido")
            st.stop()
        
        if not inconveniente.strip():
            st.warning("⚠️ Completa el campo obligatorio: inconveniente reportado")
            st.stop()
        
        # Preparar datos del formulario
        datos_formulario = {
            'codigo_informe': codigo_informe,
            'sede': sede,
            'upss': upss,
            'servicio': servicio,
            'personal_asignado': personal_asignado,
            'equipo_nombre': equipo_nombre,
            'marca': marca,
            'modelo': modelo,
            'serie': serie,
            'inconveniente': inconveniente,
            'fecha_generacion': fecha_actual.strftime("%d/%m/%Y"),
            'num_imagenes': len(imagenes_guardadas)
        }
        
        # Proceso con barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Procesando informe de mal uso...")
            progress_bar.progress(25)
            
            status_text.text("📋 Creando copia y llenando datos...")
            progress_bar.progress(50)
            
            status_text.text("☁️ Subiendo a Google Drive...")
            progress_bar.progress(75)
            
            # Crear informe completo
            resultado_final, archivo_editado = crear_informe_mal_uso_completo(
                drive_service, 
                PLANTILLA_MAL_USO_ID, 
                CARPETA_MAL_USO_ID, 
                datos_formulario
            )
            
            if resultado_final:
                progress_bar.progress(100)
                status_text.text("✅ ¡Informe de mal uso subido exitosamente!")
                
                st.success("🎉 **¡Informe de mal uso subido a Drive!**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📁 **Archivo:** {resultado_final['name']}")
                    st.info(f"🆔 **ID:** {resultado_final['id']}")
                    st.info(f"📷 **Imágenes adjuntas:** {len(imagenes_guardadas)}")
                
                with col2:
                    if 'webViewLink' in resultado_final:
                        st.markdown(f"🔗 [Ver en Google Drive]({resultado_final['webViewLink']})")
                    
                    # Descarga local opcional
                    if archivo_editado:
                        archivo_editado.seek(0)
                        st.download_button(
                            label="⬇️ Descargar copia",
                            data=archivo_editado,
                            file_name=f"{resultado_final['name']}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                # Limpiar imágenes después de subir exitosamente
                if st.button("🧹 Limpiar imágenes para nuevo informe"):
                    st.session_state.imagenes_capturadas = []
                    st.rerun()
                        
            else:
                st.error("❌ Error al crear el informe")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
            progress_bar.empty()
            status_text.empty()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px;'>
        🚨 <strong>Sistema de Informes de Mal Uso - MEDIFLOW</strong><br>
        Documentación de incidentes y mal uso de equipos médicos
    </div>
    """, unsafe_allow_html=True)