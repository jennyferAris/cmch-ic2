# informes_tecnicos.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
import base64

def conectar_google_sheets():
    """Conecta con Google Sheets usando las credenciales de Streamlit secrets"""
    try:
        # Configurar credenciales desde secrets
        credentials_dict = {
            "type": st.secrets["google_drive"]["type"],
            "project_id": st.secrets["google_drive"]["project_id"],
            "private_key_id": st.secrets["google_drive"]["private_key_id"],
            "private_key": st.secrets["google_drive"]["private_key"],
            "client_email": st.secrets["google_drive"]["client_email"],
            "client_id": st.secrets["google_drive"]["client_id"],
            "auth_uri": st.secrets["google_drive"]["auth_uri"],
            "token_uri": st.secrets["google_drive"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_drive"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google_drive"]["client_x509_cert_url"]
        }
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        gc = gspread.authorize(credentials)
        
        return gc
    except Exception as e:
        st.error(f"Error conectando con Google Sheets: {e}")
        return None

def cargar_base_datos():
    """Carga la base de datos desde Google Sheets"""
    try:
        gc = conectar_google_sheets()
        if gc is None:
            return None
            
        # ID de tu hoja de cálculo de base de datos
        spreadsheet_id = st.secrets["google_drive"]["spreadsheet_id"]
        sheet = gc.open_by_key(spreadsheet_id).sheet1
        
        # Obtener todos los datos
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        st.error(f"Error cargando base de datos: {e}")
        return None

def buscar_equipo(df, criterio_busqueda, tipo_busqueda):
    """Busca un equipo en la base de datos"""
    if df is None or df.empty:
        return None
        
    try:
        if tipo_busqueda == "Serie":
            resultado = df[df['Serie'].astype(str).str.contains(criterio_busqueda, case=False, na=False)]
        elif tipo_busqueda == "Código de Barras":
            resultado = df[df['Código de barras'].astype(str).str.contains(criterio_busqueda, case=False, na=False)]
        elif tipo_busqueda == "Nombre del Equipo":
            resultado = df[df['Nombre del equipo'].astype(str).str.contains(criterio_busqueda, case=False, na=False)]
        else:
            return None
            
        if not resultado.empty:
            return resultado.iloc[0]  # Retorna el primer resultado
        else:
            return None
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return None

def generar_pdf_informe(datos_equipo, datos_informe, técnico_info):
    """Genera el PDF del informe técnico siguiendo el formato oficial"""
    buffer = io.BytesIO()
    
    # Crear documento PDF con márgenes ajustados
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=2*cm, leftMargin=2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo para el encabezado principal
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.black
    )
    
    # Estilo para títulos de sección
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=6,
        textColor=colors.black,
        backColor=colors.lightgrey,
        leftIndent=6,
        rightIndent=6,
        spaceBefore=12
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=3
    )
    
    # Estilo para texto en negrita
    bold_style = ParagraphStyle(
        'BoldCustom',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=3
    )
    
    # Contenido del PDF
    story = []
    
    # ENCABEZADO PRINCIPAL
    story.append(Paragraph("HOSPITAL NACIONAL CAYETANO HEREDIA", header_style))
    story.append(Paragraph("DEPARTAMENTO DE INGENIERÍA CLÍNICA", header_style))
    story.append(Paragraph("INFORME TÉCNICO", header_style))
    story.append(Spacer(1, 20))
    
    # INFORMACIÓN GENERAL - Tabla superior
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    numero_informe = f"IC-{datetime.now().strftime('%Y%m%d')}-{datos_equipo.get('Serie', 'SN')}"
    
    info_general_data = [
        ['INFORME Nº:', numero_informe, 'FECHA:', fecha_actual],
        ['TÉCNICO:', técnico_info['nombre'], 'SERVICIO:', datos_informe.get('servicio', 'INGENIERÍA CLÍNICA')],
    ]
    
    tabla_info_general = Table(info_general_data, colWidths=[2.5*cm, 5*cm, 2.5*cm, 5*cm])
    tabla_info_general.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(tabla_info_general)
    story.append(Spacer(1, 15))
    
    # I. DATOS DEL EQUIPO
    story.append(Paragraph("I. DATOS DEL EQUIPO", section_title_style))
    
    equipo_data = [
        ['EQUIPO:', str(datos_equipo.get('Nombre del equipo', '')), 'MARCA:', str(datos_equipo.get('Marca', ''))],
        ['MODELO:', str(datos_equipo.get('Modelo', '')), 'SERIE:', str(datos_equipo.get('Serie', ''))],
        ['CÓDIGO PATRIMONIAL:', str(datos_equipo.get('Código de barras', '')), 'UBICACIÓN:', str(datos_equipo.get('Ubicación', ''))],
        ['ESTADO:', str(datos_equipo.get('Estado', '')), 'FECHA ADQUISICIÓN:', str(datos_equipo.get('Fecha de adquisición', ''))],
    ]
    
    tabla_equipo = Table(equipo_data, colWidths=[3*cm, 4.5*cm, 3*cm, 4.5*cm])
    tabla_equipo.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(tabla_equipo)
    story.append(Spacer(1, 15))
    
    # II. TIPO DE SERVICIO
    story.append(Paragraph("II. TIPO DE SERVICIO", section_title_style))
    
    # Crear checkboxes para tipo de servicio
    servicios = ['MANTENIMIENTO PREVENTIVO', 'MANTENIMIENTO CORRECTIVO', 'INSTALACIÓN', 'CALIBRACIÓN', 'OTROS']
    servicio_seleccionado = datos_informe.get('tipo_servicio', '').upper()
    
    servicio_data = []
    for i in range(0, len(servicios), 2):
        fila = []
        for j in range(2):
            if i + j < len(servicios):
                servicio = servicios[i + j]
                checkbox = "☑" if servicio == servicio_seleccionado else "☐"
                fila.extend([checkbox, servicio])
            else:
                fila.extend(["", ""])
        servicio_data.append(fila)
    
    tabla_servicio = Table(servicio_data, colWidths=[0.5*cm, 4*cm, 0.5*cm, 4*cm])
    tabla_servicio.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(tabla_servicio)
    story.append(Spacer(1, 15))
    
    # III. DESCRIPCIÓN DEL TRABAJO
    story.append(Paragraph("III. DESCRIPCIÓN DEL TRABAJO", section_title_style))
    
    # Motivo del servicio
    story.append(Paragraph("MOTIVO DEL SERVICIO:", bold_style))
    motivo_texto = datos_informe.get('motivo', 'No especificado')
    story.append(Paragraph(motivo_texto, normal_style))
    story.append(Spacer(1, 10))
    
    # Trabajos realizados
    story.append(Paragraph("TRABAJOS REALIZADOS:", bold_style))
    trabajos_texto = datos_informe.get('trabajos_realizados', 'No especificado')
    story.append(Paragraph(trabajos_texto, normal_style))
    story.append(Spacer(1, 10))
    
    # Repuestos utilizados
    story.append(Paragraph("REPUESTOS Y/O MATERIALES UTILIZADOS:", bold_style))
    repuestos_texto = datos_informe.get('repuestos', 'Ninguno')
    story.append(Paragraph(repuestos_texto, normal_style))
    story.append(Spacer(1, 15))
    
    # IV. DIAGNÓSTICO Y OBSERVACIONES
    story.append(Paragraph("IV. DIAGNÓSTICO Y OBSERVACIONES", section_title_style))
    
    diagnostico_texto = datos_informe.get('diagnostico', 'No especificado')
    story.append(Paragraph(diagnostico_texto, normal_style))
    story.append(Spacer(1, 10))
    
    # Observaciones
    if datos_informe.get('observaciones'):
        story.append(Paragraph("OBSERVACIONES ADICIONALES:", bold_style))
        observaciones_texto = datos_informe.get('observaciones', '')
        story.append(Paragraph(observaciones_texto, normal_style))
        story.append(Spacer(1, 15))
    
    # V. RECOMENDACIONES
    story.append(Paragraph("V. RECOMENDACIONES", section_title_style))
    
    recomendaciones_texto = datos_informe.get('recomendaciones', 'Continuar con mantenimientos programados.')
    story.append(Paragraph(recomendaciones_texto, normal_style))
    story.append(Spacer(1, 20))
    
    # VI. ESTADO FINAL DEL EQUIPO
    story.append(Paragraph("VI. ESTADO FINAL DEL EQUIPO", section_title_style))
    
    estados = ['OPERATIVO', 'INOPERATIVO', 'EN OBSERVACIÓN', 'BAJA DEFINITIVA']
    estado_seleccionado = datos_informe.get('estado_final', 'OPERATIVO').upper()
    
    estado_data = []
    for i in range(0, len(estados), 2):
        fila = []
        for j in range(2):
            if i + j < len(estados):
                estado = estados[i + j]
                checkbox = "☑" if estado == estado_seleccionado else "☐"
                fila.extend([checkbox, estado])
            else:
                fila.extend(["", ""])
        estado_data.append(fila)
    
    tabla_estado = Table(estado_data, colWidths=[0.5*cm, 4*cm, 0.5*cm, 4*cm])
    tabla_estado.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(tabla_estado)
    story.append(Spacer(1, 30))
    
    # FIRMAS
    firma_data = [
        ['', '', ''],
        ['_________________________', '', '_________________________'],
        [técnico_info['nombre'], '', 'JEFE DE INGENIERÍA CLÍNICA'],
        ['TÉCNICO RESPONSABLE', '', ''],
        ['', '', ''],
        ['FECHA: ___/___/______', '', 'FECHA: ___/___/______'],
    ]
    
    tabla_firmas = Table(firma_data, colWidths=[6*cm, 3*cm, 6*cm])
    tabla_firmas.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
        ('FONTNAME', (2, 2), (2, 2), 'Helvetica-Bold'),
    ]))
    
    story.append(tabla_firmas)
    
    # Construir PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer

def subir_informe_drive(pdf_buffer, nombre_archivo, técnico_info):
    """Sube el informe PDF a Google Drive"""
    try:
        gc = conectar_google_sheets()
        if gc is None:
            return False
            
        # ID de la carpeta de informes técnicos
        folder_id = "1rPsYh4MABv7VD524ub60BB2HZcpCApQb"
        
        # Crear archivo en Drive
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        
        # Usar las mismas credenciales
        credentials_dict = {
            "type": st.secrets["google_drive"]["type"],
            "project_id": st.secrets["google_drive"]["project_id"],
            "private_key_id": st.secrets["google_drive"]["private_key_id"],
            "private_key": st.secrets["google_drive"]["private_key"],
            "client_email": st.secrets["google_drive"]["client_email"],
            "client_id": st.secrets["google_drive"]["client_id"],
            "auth_uri": st.secrets["google_drive"]["auth_uri"],
            "token_uri": st.secrets["google_drive"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_drive"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google_drive"]["client_x509_cert_url"]
        }
        
        scopes = ["https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Metadata del archivo
        file_metadata = {
            'name': nombre_archivo,
            'parents': [folder_id]
        }
        
        # Crear media upload
        pdf_buffer.seek(0)
        media = MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf')
        
        # Subir archivo
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
        
    except Exception as e:
        st.error(f"Error subiendo archivo a Drive: {e}")
        return None

def mostrar_informes_tecnicos():
    """Función principal para mostrar la interfaz de informes técnicos"""
    st.title("📋 Generador de Informes Técnicos")
    st.markdown("*Genera informes técnicos siguiendo el formato oficial del Hospital Nacional Cayetano Heredia*")
    
    # Obtener información del técnico desde session_state
    técnico_info = {
        'nombre': st.session_state.get('name', 'Técnico'),
        'rol_nombre': st.session_state.get('rol_nombre', 'Técnico'),
        'email': st.session_state.get('email', 'no-email')
    }
    
    # Cargar base de datos
    with st.spinner("Cargando base de datos..."):
        df = cargar_base_datos()
    
    if df is None:
        st.error("❌ No se pudo cargar la base de datos")
        return
    
    st.success(f"✅ Base de datos cargada: {len(df)} equipos disponibles")
    
    # Sección de búsqueda
    st.markdown("### 🔍 Buscar Equipo")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        criterio_busqueda = st.text_input(
            "Ingrese criterio de búsqueda:",
            placeholder="Ej: 12345, MINDRAY, Monitor..."
        )
    
    with col2:
        tipo_busqueda = st.selectbox(
            "Buscar por:",
            ["Serie", "Código de Barras", "Nombre del Equipo"]
        )
    
    equipo_encontrado = None
    
    if criterio_busqueda:
        equipo_encontrado = buscar_equipo(df, criterio_busqueda, tipo_busqueda)
        
        if equipo_encontrado is not None:
            st.success("✅ Equipo encontrado")
            
            # Mostrar información del equipo
            with st.expander("📋 Información del Equipo", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Nombre del Equipo:**", equipo_encontrado.get('Nombre del equipo', 'N/A'))
                    st.write("**Serie:**", equipo_encontrado.get('Serie', 'N/A'))
                    st.write("**Modelo:**", equipo_encontrado.get('Modelo', 'N/A'))
                    st.write("**Marca:**", equipo_encontrado.get('Marca', 'N/A'))
                    st.write("**Código de Barras:**", equipo_encontrado.get('Código de barras', 'N/A'))
                
                with col2:
                    st.write("**Ubicación:**", equipo_encontrado.get('Ubicación', 'N/A'))
                    st.write("**Estado actual:**", equipo_encontrado.get('Estado', 'N/A'))
                    st.write("**Fecha de Adquisición:**", equipo_encontrado.get('Fecha de adquisición', 'N/A'))
                    st.write("**Proveedor:**", equipo_encontrado.get('Proveedor', 'N/A'))
                    st.write("**Costo:**", equipo_encontrado.get('Costo', 'N/A'))
        else:
            st.warning("⚠️ No se encontró ningún equipo con ese criterio de búsqueda")
    
    # Formulario de informe
    if equipo_encontrado is not None:
        st.markdown("### 📝 Completar Informe Técnico")
        
        with st.form("formulario_informe"):
            # Tipo de servicio
            st.markdown("**II. TIPO DE SERVICIO**")
            tipo_servicio = st.selectbox(
                "Seleccione el tipo de servicio:",
                ["Mantenimiento Preventivo", "Mantenimiento Correctivo", "Instalación", "Calibración", "Otros"]
            )
            
            st.markdown("**III. DESCRIPCIÓN DEL TRABAJO**")
            col1, col2 = st.columns(2)
            
            with col1:
                motivo = st.text_area(
                    "Motivo del Servicio:",
                    height=100,
                    help="Describa el motivo por el cual se realizó el servicio"
                )
                
                trabajos_realizados = st.text_area(
                    "Trabajos Realizados:",
                    height=120,
                    help="Detalle los trabajos específicos realizados en el equipo"
                )
            
            with col2:
                repuestos = st.text_area(
                    "Repuestos y/o Materiales Utilizados:",
                    height=100,
                    help="Liste los repuestos, materiales o consumibles utilizados"
                )
                
                diagnostico = st.text_area(
                    "Diagnóstico y Observaciones:",
                    height=120,
                    help="Describa el diagnóstico técnico y observaciones importantes"
                )
            
            st.markdown("**V. RECOMENDACIONES**")
            recomendaciones = st.text_area(
                "Recomendaciones:",
                height=80,
                help="Proporcione recomendaciones para el mantenimiento futuro"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                observaciones = st.text_area(
                    "Observaciones Adicionales (Opcional):",
                    height=60
                )
            
            with col2:
                estado_final = st.selectbox(
                    "Estado Final del Equipo:",
                    ["Operativo", "Inoperativo", "En Observación", "Baja Definitiva"]
                )
                
                servicio = st.text_input(
                    "Servicio/Departamento:",
                    value="INGENIERÍA CLÍNICA"
                )
            
            submitted = st.form_submit_button("🔄 Generar Informe Técnico", type="primary", use_container_width=True)
            
            if submitted:
                # Validar campos obligatorios
                campos_faltantes = []
                if not motivo.strip():
                    campos_faltantes.append("Motivo del Servicio")
                if not trabajos_realizados.strip():
                    campos_faltantes.append("Trabajos Realizados")
                if not diagnostico.strip():
                    campos_faltantes.append("Diagnóstico y Observaciones")
                if not recomendaciones.strip():
                    campos_faltantes.append("Recomendaciones")
                
                if campos_faltantes:
                    st.error(f"❌ Por favor complete los siguientes campos obligatorios: {', '.join(campos_faltantes)}")
                else:
                    # Datos del informe
                    datos_informe = {
                        'servicio': servicio,
                        'tipo_servicio': tipo_servicio,
                        'motivo': motivo,
                        'trabajos_realizados': trabajos_realizados,
                        'repuestos': repuestos,
                        'diagnostico': diagnostico,
                        'observaciones': observaciones,
                        'recomendaciones': recomendaciones,
                        'estado_final': estado_final
                    }
                    
                    try:
                        with st.spinner("Generando informe técnico..."):
                            # Generar PDF
                            pdf_buffer = generar_pdf_informe(equipo_encontrado, datos_informe, técnico_info)
                            
                            # Nombre del archivo
                            fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
                            serie_limpia = str(equipo_encontrado.get('Serie', 'SIN_SERIE')).replace('/', '_').replace(' ', '_')
                            nombre_archivo = f"Informe_Tecnico_{serie_limpia}_{fecha_actual}.pdf"
                            
                            # Subir a Drive
                            file_id = subir_informe_drive(pdf_buffer, nombre_archivo, técnico_info)
                            
                            if file_id:
                                st.success("✅ Informe técnico generado y guardado exitosamente en Google Drive")
                                st.info(f"📁 Archivo guardado como: {nombre_archivo}")
                                st.info(f"📋 Número de informe: IC-{datetime.now().strftime('%Y%m%d')}-{equipo_encontrado.get('Serie', 'SN')}")
                                
                                # Botón de descarga
                                pdf_buffer.seek(0)
                                st.download_button(
                                    label="📥 Descargar Informe PDF",
                                    data=pdf_buffer.read(),
                                    file_name=nombre_archivo,
                                    mime="application/pdf",
                                    type="secondary",
                                    use_container_width=True
                                )
                            else:
                                st.warning("⚠️ Error al guardar en Google Drive, pero puede descargar el archivo")
                                # Botón de descarga como fallback
                                pdf_buffer.seek(0)
                                st.download_button(
                                    label="📥 Descargar Informe PDF",
                                    data=pdf_buffer.read(),
                                    file_name=nombre_archivo,
                                    mime="application/pdf",
                                    type="secondary",
                                    use_container_width=True
                                )
                                
                    except Exception as e:
                        st.error(f"❌ Error generando informe: {e}")
    
    # Instrucciones
    with st.expander("ℹ️ Instrucciones de Uso"):
        st.markdown("""
        **Pasos para generar un informe técnico:**
        
        1. **🔍 Buscar Equipo**: Ingrese el número de serie, código de barras o nombre del equipo
        2. **✅ Verificar Datos**: Revise que la información del equipo sea correcta
        3. **📝 Completar Formulario**: Llene todos los campos del informe técnico
        4. **🔄 Generar**: Haga clic en "Generar Informe Técnico"
        5. **📥 Descargar**: El informe se guardará automáticamente en Drive y podrá descargarlo
        
        **Campos Obligatorios:**
        - Motivo del Servicio
        - Trabajos Realizados  
        - Diagnóstico y Observaciones
        - Recomendaciones
        
        **Formato:** El informe sigue exactamente el formato oficial del Hospital Nacional Cayetano Heredia.
        
        **Almacenamiento:** Los informes se guardan automáticamente en la carpeta "Informes Técnicos" del Drive institucional.
        """)
    
    # Estadísticas
    if df is not None:
        st.markdown("### 📊 Estadísticas de la Base de Datos")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Equipos", len(df))
        with col2:
            operativos = len(df[df['Estado'] == 'Operativo']) if 'Estado' in df.columns else 0
            st.metric("Operativos", operativos)
        with col3:
            marcas_unicas = df['Marca'].nunique() if 'Marca' in df.columns else 0
            st.metric("Marcas", marcas_unicas)
        with col4:
            ubicaciones = df['Ubicación'].nunique() if 'Ubicación' in df.columns else 0
            st.metric("Ubicaciones", ubicaciones)