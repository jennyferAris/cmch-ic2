import streamlit as st
import os
import qrcode
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime
import pandas as pd

# Configuración de servicios
info = st.secrets["google_service_account"]
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
cliente = gspread.authorize(credenciales)

# Cliente de Drive
drive_service = build('drive', 'v3', credentials=credenciales)

QR_FOLDER_ID = st.secrets["google_drive"]["qr_folder_id"]

def obtener_siguiente_codigo():
    """Obtener el siguiente código secuencial"""
    try:
        query = f"'{QR_FOLDER_ID}' in parents and mimeType='image/png'"
        results = drive_service.files().list(q=query, pageSize=1000).execute()
        archivos = results.get('files', [])
        
        codigos = [f['name'].replace(".png", "") for f in archivos if f['name'].startswith("EQU-")]
        if codigos:
            ultimo = max(codigos)
            siguiente_numero = int(ultimo.split("-")[1]) + 1
        else:
            siguiente_numero = 1
            
        return f"EQU-{siguiente_numero:07d}"
    except Exception as e:
        st.error(f"Error obteniendo siguiente código: {e}")
        return f"EQU-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def crear_qr_simple(codigo):
    """Crear QR simple con solo el código"""
    img = qrcode.make(codigo)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def crear_qr_avanzado(codigo, datos_adicionales=None):
    """Crear QR con información adicional"""
    # Datos básicos
    qr_data = f"CÓDIGO: {codigo}"
    
    # Agregar datos adicionales si existen
    if datos_adicionales:
        if datos_adicionales.get('nombre'):
            qr_data += f"\nEQUIPO: {datos_adicionales['nombre']}"
        if datos_adicionales.get('ubicacion'):
            qr_data += f"\nUBICACIÓN: {datos_adicionales['ubicacion']}"
        if datos_adicionales.get('url'):
            qr_data += f"\nURL: {datos_adicionales['url']}"
    
    # Crear QR con configuración personalizada
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def subir_qr_a_drive(buffer, codigo):
    """Subir QR generado a Google Drive"""
    try:
        file_metadata = {
            'name': f"{codigo}.png",
            'parents': [QR_FOLDER_ID],
            'mimeType': 'image/png'
        }
        media = MediaIoBaseUpload(buffer, mimetype='image/png')
        archivo = drive_service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id,webViewLink'
        ).execute()
        
        return archivo.get('id'), archivo.get('webViewLink')
    except Exception as e:
        st.error(f"Error subiendo QR: {e}")
        return None, None

def obtener_qrs_existentes():
    """Obtener lista de QRs ya generados"""
    try:
        query = f"'{QR_FOLDER_ID}' in parents and mimeType='image/png'"
        results = drive_service.files().list(
            q=query, 
            pageSize=100,
            fields="files(id,name,createdTime,webViewLink)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        st.error(f"Error obteniendo QRs existentes: {e}")
        return []

def generar_qrs():
    st.title("📲 Generador de Códigos QR")
    st.write("Genera códigos QR para equipos médicos")
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["🆕 Generar Nuevo", "📋 QRs Existentes", "⚙️ Configuración"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Generar QR Secuencial")
            
            # Obtener siguiente código
            siguiente_codigo = obtener_siguiente_codigo()
            st.info(f"**Próximo código:** {siguiente_codigo}")
            
            # Opción de QR simple o avanzado
            tipo_qr = st.radio(
                "Tipo de QR:",
                ["Simple (solo código)", "Avanzado (con información adicional)"]
            )
            
            datos_adicionales = {}
            if tipo_qr == "Avanzado (con información adicional)":
                st.write("**Información adicional:**")
                datos_adicionales['nombre'] = st.text_input(
                    "Nombre del equipo:", 
                    placeholder="Monitor de Signos Vitales"
                )
                datos_adicionales['ubicacion'] = st.text_input(
                    "Ubicación:", 
                    placeholder="UCI - Cama 1"
                )
                datos_adicionales['url'] = st.text_input(
                    "URL del sistema:", 
                    value=f"https://cmch-ic2.streamlit.app/scanner?equipo={siguiente_codigo}",
                    help="URL que se abrirá al escanear el QR"
                )
            
            if st.button("🔧 GENERAR QR", type="primary", use_container_width=True):
                with st.spinner("Generando QR..."):
                    # Crear QR según el tipo seleccionado
                    if tipo_qr == "Simple (solo código)":
                        qr_buffer = crear_qr_simple(siguiente_codigo)
                    else:
                        qr_buffer = crear_qr_avanzado(siguiente_codigo, datos_adicionales)
                    
                    # Subir a Drive
                    file_id, web_link = subir_qr_a_drive(qr_buffer, siguiente_codigo)
                    
                    if file_id:
                        st.success(f"✅ QR generado y subido: **{siguiente_codigo}**")
                        
                        # Guardar en session state para mostrar
                        st.session_state.ultimo_qr = qr_buffer.getvalue()
                        st.session_state.ultimo_codigo = siguiente_codigo
                        st.session_state.ultimo_link = web_link
                    else:
                        st.error("❌ Error al subir el QR a Google Drive")
        
        with col2:
            st.subheader("QR Generado")
            
            # Mostrar último QR generado
            if 'ultimo_qr' in st.session_state:
                st.image(
                    st.session_state.ultimo_qr, 
                    caption=f"Código: {st.session_state.ultimo_codigo}",
                    width=300
                )
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar QR",
                    data=st.session_state.ultimo_qr,
                    file_name=f"{st.session_state.ultimo_codigo}.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                # Link de Drive
                if 'ultimo_link' in st.session_state and st.session_state.ultimo_link:
                    st.markdown(f"🔗 [Ver en Google Drive]({st.session_state.ultimo_link})")
            else:
                st.info("👆 Genera un QR para verlo aquí")
    
    with tab2:
        st.subheader("📋 QRs Existentes")
        
        # Obtener QRs existentes
        qrs_existentes = obtener_qrs_existentes()
        
        if qrs_existentes:
            st.write(f"**Total de QRs generados:** {len(qrs_existentes)}")
            
            # Convertir a DataFrame para mejor visualización
            df_qrs = pd.DataFrame(qrs_existentes)
            df_qrs['codigo'] = df_qrs['name'].str.replace('.png', '')
            df_qrs['fecha'] = pd.to_datetime(df_qrs['createdTime']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Mostrar tabla
            st.dataframe(
                df_qrs[['codigo', 'fecha']].rename(columns={
                    'codigo': 'Código',
                    'fecha': 'Fecha de Creación'
                }),
                use_container_width=True
            )
            
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total QRs", len(qrs_existentes))
            with col2:
                hoy = datetime.now().date()
                qrs_hoy = sum(1 for qr in qrs_existentes 
                             if pd.to_datetime(qr['createdTime']).date() == hoy)
                st.metric("📅 Generados Hoy", qrs_hoy)
            with col3:
                if qrs_existentes:
                    ultimo_numero = max([
                        int(qr['name'].replace('.png', '').split('-')[1]) 
                        for qr in qrs_existentes 
                        if qr['name'].startswith('EQU-')
                    ])
                    st.metric("🔢 Último Número", ultimo_numero)
        else:
            st.info("📝 No hay QRs generados aún")
    
    with tab3:
        st.subheader("⚙️ Configuración del Generador")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuración Actual:**")
            st.code(f"""
Carpeta de QRs: {QR_FOLDER_ID}
Formato: EQU-XXXXXXX
Tipo de archivo: PNG
Calidad: Alta
            """)
        
        with col2:
            st.write("**Próximas funciones:**")
            st.info("""
            • Códigos personalizados
            • QR con logos
            • Exportación masiva
            • Integración con inventario
            """)
        
        # Botón para limpiar cache
        if st.button("🔄 Actualizar Lista de QRs"):
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    generar_qrs()
