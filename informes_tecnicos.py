import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io
from datetime import datetime

# Configuración de credenciales
info = st.secrets["google_service_account"]
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
cliente = gspread.authorize(credenciales)
drive_service = build('drive', 'v3', credentials=credenciales)
folder2 = st.secrets["google_drive"]["qr_folder_id2"]

def subir_archivo_drive(pdf_buffer, nombre_archivo):
    """Sube el informe PDF a Google Drive"""
    try:
        file_metadata = {
            'name': nombre_archivo,
            'parents': [folder2],
            'mimeType': 'application/pdf'
        }

        pdf_buffer.seek(0)
        media = MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')

    except Exception as e:
        st.error(f"Error subiendo archivo a Drive: {e}")
        return None

def generar_pdf_informe(datos_informe):
    """Genera un PDF del informe técnico"""
    buffer = io.BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Crear contenido
    story = []
    
    # Título
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkred
    )
    
    story.append(Paragraph("INFORME TÉCNICO", titulo_style))
    story.append(Spacer(1, 12))
    
    # Información del header
    header_data = [
        ['Técnico:', datos_informe['tecnico']],
        ['Fecha:', datos_informe['fecha']],
        ['Equipo:', datos_informe['equipo']],
        ['Área:', datos_informe['area']],
        ['Tipo de Informe:', datos_informe['tipo']]
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 12))
    
    # Descripción del problema
    story.append(Paragraph("<b>Descripción del Problema:</b>", styles['Heading2']))
    story.append(Paragraph(datos_informe['descripcion'], styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Diagnóstico
    story.append(Paragraph("<b>Diagnóstico:</b>", styles['Heading2']))
    story.append(Paragraph(datos_informe['diagnostico'], styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Acciones realizadas
    story.append(Paragraph("<b>Acciones Realizadas:</b>", styles['Heading2']))
    story.append(Paragraph(datos_informe['acciones'], styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Recomendaciones
    if datos_informe.get('recomendaciones'):
        story.append(Paragraph("<b>Recomendaciones:</b>", styles['Heading2']))
        story.append(Paragraph(datos_informe['recomendaciones'], styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Firma
    story.append(Spacer(1, 24))
    firma_data = [
        ['_' * 30, '_' * 30],
        ['Técnico Responsable', 'Supervisor']
    ]
    
    firma_table = Table(firma_data, colWidths=[3*inch, 3*inch])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 12),
    ]))
    
    story.append(firma_table)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def subir_informe_drive():
    """Función principal para mostrar la interfaz de informes técnicos"""
    st.title("📄 Informes Técnicos")
    
    # Obtener información del usuario desde session_state
    tecnico = st.session_state.get('name', 'Usuario')
    rol_nombre = st.session_state.get('rol_nombre', 'Sin rol')
    email = st.session_state.get('email', 'Sin email')
    
    # Mostrar información del técnico
    st.info(f"👤 **Técnico:** {tecnico} ({rol_nombre})")
    
    # Formulario para crear informe
    with st.form("formulario_informe"):
        st.subheader("📝 Crear Nuevo Informe")
        
        col1, col2 = st.columns(2)
        
        with col1:
            equipo = st.text_input("🏥 Equipo Médico", placeholder="Ej: Ventilador Puritan Bennett")
            area = st.selectbox("📍 Área", [
                "UCI", "Emergencia", "Quirófano", "Hospitalización", 
                "Laboratorio", "Rayos X", "Farmacia", "Otro"
            ])
            tipo_informe = st.selectbox("📋 Tipo de Informe", [
                "Mantenimiento Preventivo",
                "Mantenimiento Correctivo", 
                "Calibración",
                "Inspección",
                "Reparación",
                "Otro"
            ])
        
        with col2:
            fecha = st.date_input("📅 Fecha del Informe", datetime.now().date())
            prioridad = st.selectbox("⚠️ Prioridad", ["Baja", "Media", "Alta", "Crítica"])
            estado = st.selectbox("📊 Estado", ["Completado", "En Proceso", "Pendiente"])
        
        # Campos de texto
        descripcion = st.text_area("📝 Descripción del Problema", 
                                 placeholder="Describe detalladamente el problema encontrado...",
                                 height=100)
        
        diagnostico = st.text_area("🔍 Diagnóstico", 
                                 placeholder="Análisis técnico del problema...",
                                 height=100)
        
        acciones = st.text_area("🔧 Acciones Realizadas", 
                              placeholder="Detalla las acciones tomadas para resolver el problema...",
                              height=100)
        
        recomendaciones = st.text_area("💡 Recomendaciones", 
                                     placeholder="Recomendaciones para prevenir futuros problemas...",
                                     height=80)
        
        # Botón para generar informe
        submitted = st.form_submit_button("📤 Generar y Subir Informe", type="primary")
        
        if submitted:
            # Validar campos obligatorios
            if not all([equipo, area, descripcion, diagnostico, acciones]):
                st.error("❌ Por favor completa todos los campos obligatorios (Equipo, Área, Descripción, Diagnóstico, Acciones)")
                return
            
            # Preparar datos del informe
            datos_informe = {
                'tecnico': tecnico,
                'email': email,
                'fecha': fecha.strftime('%d/%m/%Y'),
                'equipo': equipo,
                'area': area,
                'tipo': tipo_informe,
                'prioridad': prioridad,
                'estado': estado,
                'descripcion': descripcion,
                'diagnostico': diagnostico,
                'acciones': acciones,
                'recomendaciones': recomendaciones
            }
            
            try:
                # Generar PDF
                with st.spinner('📄 Generando informe PDF...'):
                    pdf_buffer = generar_pdf_informe(datos_informe)
                
                # Crear nombre del archivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"Informe_{equipo.replace(' ', '_')}_{timestamp}.pdf"
                
                # Subir a Google Drive
                with st.spinner('☁️ Subiendo a Google Drive...'):
                    file_id = subir_archivo_drive(pdf_buffer, nombre_archivo)
                
                if file_id:
                    st.success("✅ ¡Informe generado y subido exitosamente!")
                    st.info(f"📎 **Archivo:** {nombre_archivo}")
                    st.info(f"🆔 **ID en Drive:** {file_id}")
                    
                    # Mostrar preview del PDF
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=nombre_archivo,
                        mime="application/pdf"
                    )
                else:
                    st.error("❌ Error al subir el archivo a Google Drive")
                    
            except Exception as e:
                st.error(f"❌ Error al procesar el informe: {str(e)}")
    
    # Sección de informes recientes (placeholder)
    st.markdown("---")
    st.subheader("📚 Mis Informes Recientes")
    st.info("🔄 Funcionalidad en desarrollo - Aquí se mostrarán tus informes anteriores")

# Esta es la función que se llama desde main.py
def mostrar_informes_tecnicos():
    """Función de compatibilidad para main.py"""
    subir_informe_drive()