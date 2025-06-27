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
        # Exportar Google Sheets como Excel
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

# IDs de Google Drive (usando tus enlaces)
PLANTILLA_ID = "1QsSeISaWS_mTnMGsfhlWcTEuE948X8I7"
CARPETA_INFORMES_ID = "1W5K0aOUOrr5qabn-mFzi5GrlAZ1xgY3i"

st.set_page_config(page_title="Formulario Técnico", layout="wide")
st.title("🩺 Registro de Servicio Técnico - Equipos Médicos")

# Configurar Google Drive
drive_service = configurar_drive_api()

# Cargar base de datos
df = cargar_datos()

# Tu formulario original...
codigo_input = st.text_input("🔍 Ingrese el código del equipo (Ej: EQU-0000001)")
equipo_info = df[df["Codigo nuevo"] == codigo_input]

if not equipo_info.empty:
    equipo_row = equipo_info.iloc[0]
    marca = equipo_row["MARCA"]
    modelo = equipo_row["MODELO"]
    equipo = equipo_row["EQUIPO"]
    serie = equipo_row["SERIE"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Marca", value=marca, disabled=True)
        st.text_input("Equipo", value=equipo, disabled=True)
    with col2:
        st.text_input("Modelo", value=modelo, disabled=True)
        st.text_input("Serie", value=serie, disabled=True)
else:
    st.warning("Introduce un código válido para mostrar los datos del equipo.")
    marca = modelo = equipo = serie = ""

# Resto del formulario
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

# Fechas y horas
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

# Campos de texto
st.markdown("### 📝 Detalles del Servicio")
inconveniente = st.text_area("🛠 Inconveniente reportado / Motivo de servicio", height=100)
actividades = st.text_area("✅ Actividades realizadas", height=150)
resultado = st.text_area("📋 Resultado final y observaciones", height=100)

# Código del informe
siglas_dict = {
    "Mantenimiento Preventivo": "MP",
    "Mantenimiento Correctivo": "MC",
    "Inspección": "I",
    "Otro": "O"
}

if equipo and modelo and serie:
    fecha_str = fecha_inicio.strftime("%Y%m%d")
    sigla_servicio = siglas_dict.get(tipo_servicio, "O")
    codigo_informe = f"{fecha_str}-{sigla_servicio}-{modelo}-{serie}"
    st.text_input("📄 Código del informe generado", value=codigo_informe, disabled=True)
else:
    codigo_informe = ""

# BOTÓN PARA GENERAR INFORME
st.markdown("### 📤 Generar Informe")

if st.button("🚀 Generar y Guardar Informe Técnico", type="primary", use_container_width=True):
    if not codigo_informe:
        st.error("❌ Por favor ingresa un código de equipo válido primero")
        st.stop()
    
    if not inconveniente.strip() or not actividades.strip():
        st.warning("⚠️ Por favor completa los campos de inconveniente y actividades realizadas")
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

        # Llenar datos en las celdas correspondientes
        ws["J6"] = codigo_informe
        ws["J6"].font = fuente
        ws["C5"] = sede
        ws["C5"].font = fuente
        ws["C6"] = upss
        ws["C6"].font = fuente
        ws["C7"] = tipo_servicio
        ws["C7"].font = fuente
        ws["F10"] = equipo
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
        
        # 3. Guardar en buffer
        progress_bar.progress(60)
        archivo_final = io.BytesIO()
        wb.save(archivo_final)
        archivo_final.seek(0)
        
        # 4. Subir a Google Drive
        status_text.text("☁️ Guardando en Google Drive...")
        progress_bar.progress(80)
        
        nombre_archivo = f"informe_{codigo_informe}.xlsx"
        resultado_subida = subir_a_drive(drive_service, archivo_final, nombre_archivo, CARPETA_INFORMES_ID)
        
        if resultado_subida:
            progress_bar.progress(100)
            status_text.text("✅ ¡Informe generado exitosamente!")
            
            st.success(f"🎉 **¡Informe generado y guardado exitosamente!**")
            
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
    🏥 <strong>Sistema de Informes Técnicos - MEDIFLOW</strong><br>
    Los informes se guardan automáticamente en Google Drive para respaldo y acceso compartido
</div>
""", unsafe_allow_html=True)