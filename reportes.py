import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import io
import plotly.io as pio

COLORES_REPORTE = {
    'primary': '#1f4e79',
    'secondary': '#2e8b57',
    'accent': '#ff6b35',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8'
}

def verificar_permisos_reportes():
    """Verifica permisos para acceso a reportes"""
    #nivel_usuario = st.session_state.get('rol_nivel', 0)
    #if nivel_usuario < 1:
        #return False
    return True

def generar_datos_reporte(mes_seleccionado, ano_seleccionado):
    """Genera datos simulados para el reporte del período seleccionado"""
    np.random.seed(hash(f"{mes_seleccionado}_{ano_seleccionado}") % 2**32)
    
    datos_departamento = {
        'nombre_hospital': 'Clínica Médica Cayetano Heredia',
        'departamento': 'Ingeniería Clínica',
        'jefe_departamento': st.session_state.get('name', 'Ing. Clínico'),
        'periodo': f"{mes_seleccionado}/{ano_seleccionado}",
        'fecha_reporte': datetime.now().strftime('%d/%m/%Y')
    }
    
    kpis_mes = {
        'uptime_promedio': np.random.uniform(88, 96),
        'downtime_total_horas': np.random.uniform(150, 400),
        'equipos_operativos': np.random.randint(45, 55),
        'equipos_mantenimiento': np.random.randint(3, 8),
        'equipos_fuera_servicio': np.random.randint(1, 4),
        'costo_mantenimiento_correctivo': np.random.uniform(8000, 18000),
        'costo_mantenimiento_preventivo': np.random.uniform(5000, 12000),
        'ordenes_trabajo_completadas': np.random.randint(85, 120),
        'ordenes_trabajo_pendientes': np.random.randint(5, 15),
        'ppm_cumplimiento': np.random.uniform(82, 95),
        'cosr': np.random.uniform(0.18, 0.35),
        'tiempo_respuesta_promedio': np.random.uniform(2.5, 6.0)
    }
    
    areas = ['UCI', 'Quirófanos', 'Emergencia', 'Imagenología', 'Laboratorio', 'Hospitalización']
    datos_areas = []
    
    for area in areas:
        datos_areas.append({
            'area': area,
            'equipos_total': np.random.randint(8, 15),
            'uptime': np.random.uniform(85, 98),
            'ordenes_trabajo': np.random.randint(10, 25),
            'costo_mantenimiento': np.random.uniform(1500, 4000),
            'incidentes': np.random.randint(1, 6)
        })
    
    eventos = [
        "Mantenimiento preventivo programado completado al 92%",
        "Actualización de software en equipos de imagenología",
        "Capacitación al personal técnico en nuevos protocolos",
        "Implementación de nuevo sistema de tickets",
        "Auditoría interna de calidad realizada"
    ]
    
    proyectos = [
        {
            'nombre': 'Modernización UCI',
            'progreso': np.random.randint(60, 85),
            'estado': 'En Progreso'
        },
        {
            'nombre': 'Sistema de Gestión RFID',
            'progreso': np.random.randint(30, 60),
            'estado': 'Planificación'
        },
        {
            'nombre': 'Certificación ISO 13485',
            'progreso': np.random.randint(70, 90),
            'estado': 'Implementación'
        }
    ]
    
    return datos_departamento, kpis_mes, datos_areas, eventos, proyectos

def crear_graficos_reporte(kpis_mes, datos_areas):
    """Crea gráficos para incluir en el reporte PDF"""
    graficos = {}
    
    fig_uptime = px.bar(
        pd.DataFrame(datos_areas),
        x='area',
        y='uptime',
        title='Uptime por Área (%)',
        color='uptime',
        color_continuous_scale='RdYlGn',
        text='uptime'
    )
    fig_uptime.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_uptime.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Área",
        yaxis_title="Uptime (%)",
        title_x=0.5
    )
    graficos['uptime_areas'] = pio.to_image(fig_uptime, format='png', width=800, height=400)
    
    costos_data = {
        'Tipo': ['Correctivo', 'Preventivo'],
        'Costo': [kpis_mes['costo_mantenimiento_correctivo'], kpis_mes['costo_mantenimiento_preventivo']]
    }
    
    fig_costos = px.pie(
        pd.DataFrame(costos_data),
        values='Costo',
        names='Tipo',
        title='Distribución de Costos de Mantenimiento',
        color_discrete_map={'Correctivo': '#dc3545', 'Preventivo': '#28a745'}
    )
    fig_costos.update_traces(textposition='inside', textinfo='percent+label')
    fig_costos.update_layout(height=400, title_x=0.5)
    graficos['costos_mantenimiento'] = pio.to_image(fig_costos, format='png', width=600, height=400)
    
    estados_equipos = {
        'Estado': ['Operativos', 'En Mantenimiento', 'Fuera de Servicio'],
        'Cantidad': [
            kpis_mes['equipos_operativos'],
            kpis_mes['equipos_mantenimiento'],
            kpis_mes['equipos_fuera_servicio']
        ]
    }
    
    fig_equipos = px.bar(
        pd.DataFrame(estados_equipos),
        x='Estado',
        y='Cantidad',
        title='Estado de Equipos',
        color='Estado',
        color_discrete_map={
            'Operativos': '#28a745',
            'En Mantenimiento': '#ffc107',
            'Fuera de Servicio': '#dc3545'
        }
    )
    fig_equipos.update_layout(height=400, showlegend=False, title_x=0.5)
    graficos['estado_equipos'] = pio.to_image(fig_equipos, format='png', width=700, height=400)
    
    return graficos

def generar_pdf_reporte(datos_departamento, kpis_mes, datos_areas, eventos, proyectos, graficos):
    """Genera el reporte en formato PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor(COLORES_REPORTE['primary'])
    )
    
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor(COLORES_REPORTE['primary'])
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        alignment=TA_JUSTIFY
    )
    
    story = []
    
    story.append(Spacer(1, 0.5*inch))
    
    header_data = [
        [f"{datos_departamento['nombre_hospital']}", ""],
        [f"Departamento de {datos_departamento['departamento']}", f"Período: {datos_departamento['periodo']}"],
        ["", f"Fecha: {datos_departamento['fecha_reporte']}"]
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("REPORTE EJECUTIVO MENSUAL", titulo_style))
    story.append(Paragraph("Departamento de Ingeniería Clínica", subtitulo_style))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("RESUMEN EJECUTIVO", subtitulo_style))
    
    resumen_texto = f"""
    Durante el período de {datos_departamento['periodo']}, el Departamento de Ingeniería Clínica ha mantenido 
    un rendimiento sólido en la gestión de equipos médicos. El uptime promedio de {kpis_mes['uptime_promedio']:.1f}% 
    demuestra la eficacia de nuestros programas de mantenimiento preventivo, con un cumplimiento del 
    {kpis_mes['ppm_cumplimiento']:.1f}% en las actividades programadas.
    
    Se completaron {kpis_mes['ordenes_trabajo_completadas']} órdenes de trabajo con un tiempo de respuesta 
    promedio de {kpis_mes['tiempo_respuesta_promedio']:.1f} horas. Los costos de mantenimiento se mantuvieron 
    dentro del presupuesto establecido, con una distribución equilibrada entre mantenimiento correctivo 
    (${kpis_mes['costo_mantenimiento_correctivo']:,.0f}) y preventivo (${kpis_mes['costo_mantenimiento_preventivo']:,.0f}).
    """
    
    story.append(Paragraph(resumen_texto, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("INDICADORES CLAVE DE RENDIMIENTO (KPIs)", subtitulo_style))
    
    kpi_data = [
        ['Indicador', 'Valor', 'Objetivo', 'Estado'],
        ['Uptime Promedio', f"{kpis_mes['uptime_promedio']:.1f}%", "≥85%", "✓" if kpis_mes['uptime_promedio'] >= 85 else "⚠"],
        ['PPM Cumplimiento', f"{kpis_mes['ppm_cumplimiento']:.1f}%", "≥90%", "✓" if kpis_mes['ppm_cumplimiento'] >= 90 else "⚠"],
        ['COSR', f"{kpis_mes['cosr']:.3f}", "≤0.30", "✓" if kpis_mes['cosr'] <= 0.30 else "⚠"],
        ['Tiempo Respuesta', f"{kpis_mes['tiempo_respuesta_promedio']:.1f} hrs", "≤4 hrs", "✓" if kpis_mes['tiempo_respuesta_promedio'] <= 4 else "⚠"],
        ['Equipos Operativos', f"{kpis_mes['equipos_operativos']}", "≥45", "✓" if kpis_mes['equipos_operativos'] >= 45 else "⚠"]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 1*inch, 1*inch, 0.8*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORES_REPORTE['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 0.3*inch))
    
    for titulo, imagen in graficos.items():
        story.append(Spacer(1, 0.2*inch))
        img_buffer = io.BytesIO(imagen)
        img = Image(img_buffer, width=6*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 0.3*inch))
    
    conclusiones = f"""
    Basándose en el análisis de los datos del período {datos_departamento['periodo']}, se concluye:
    
    1. El departamento mantiene un rendimiento operativo satisfactorio con un uptime del {kpis_mes['uptime_promedio']:.1f}%.
    2. El programa de mantenimiento preventivo requiere refuerzo para alcanzar el objetivo del 90% de cumplimiento.
    3. La gestión de órdenes de trabajo es eficiente con {kpis_mes['ordenes_trabajo_pendientes']} órdenes pendientes.
    4. Se recomienda continuar con la estrategia actual de mantenimiento y considerar la ampliación del equipo técnico.
    
    Elaborado por: {datos_departamento['jefe_departamento']}
    Cargo: Jefe de Ingeniería Clínica
    """
    
    story.append(Paragraph(conclusiones, normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def mostrar_reportes():
    """Función principal del módulo de reportes"""
    
    if not verificar_permisos_reportes():
        st.error("🚫 **Acceso Denegado**")
        st.warning("Solo Ingenieros (Nivel 4+) pueden acceder a los Reportes.")
        return
    
    st.title("📊 Reportes Ejecutivos")
    st.info(f"👤 **{st.session_state.get('name', '')}** | Generación de reportes departamentales")
    
    st.markdown("## ⚙️ Configuración del Reporte")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        mes_actual = datetime.now().month
        mes_seleccionado = st.selectbox(
            "📅 Mes del Reporte",
            options=list(meses.keys()),
            format_func=lambda x: meses[x],
            index=mes_actual - 1
        )
    
    with col2:
        ano_actual = datetime.now().year
        anos_disponibles = list(range(ano_actual - 2, ano_actual + 1))
        ano_seleccionado = st.selectbox(
            "📅 Año del Reporte",
            options=anos_disponibles,
            index=len(anos_disponibles) - 1
        )
    
    with col3:
        tipo_reporte = st.selectbox(
            "📋 Tipo de Reporte",
            ["Reporte Mensual Completo", "Reporte Ejecutivo Resumido", "Análisis de KPIs"]
        )
    
    st.markdown("## 📋 Vista Previa del Reporte")
    
    datos_departamento, kpis_mes, datos_areas, eventos, proyectos = generar_datos_reporte(
        mes_seleccionado, ano_seleccionado
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏥 Información del Departamento")
        st.write(f"**Hospital:** {datos_departamento['nombre_hospital']}")
        st.write(f"**Departamento:** {datos_departamento['departamento']}")
        st.write(f"**Período:** {meses[mes_seleccionado]} {ano_seleccionado}")
        st.write(f"**Jefe de Departamento:** {datos_departamento['jefe_departamento']}")
    
    with col2:
        st.markdown("### 📊 KPIs Destacados")
        st.metric("Uptime Promedio", f"{kpis_mes['uptime_promedio']:.1f}%")
        st.metric("PPM Cumplimiento", f"{kpis_mes['ppm_cumplimiento']:.1f}%")
        st.metric("Órdenes Completadas", kpis_mes['ordenes_trabajo_completadas'])
        st.metric("COSR", f"{kpis_mes['cosr']:.3f}")
    
    st.markdown("### 📈 Indicadores Detallados")
    
    kpis_df = pd.DataFrame([
        ["Uptime Promedio", f"{kpis_mes['uptime_promedio']:.1f}%", "≥85%"],
        ["Downtime Total", f"{kpis_mes['downtime_total_horas']:.0f} hrs", "≤200 hrs"],
        ["Equipos Operativos", kpis_mes['equipos_operativos'], "≥45"],
        ["Equipos en Mantenimiento", kpis_mes['equipos_mantenimiento'], "≤10"],
        ["PPM Cumplimiento", f"{kpis_mes['ppm_cumplimiento']:.1f}%", "≥90%"],
        ["COSR", f"{kpis_mes['cosr']:.3f}", "≤0.30"],
        ["Tiempo Respuesta", f"{kpis_mes['tiempo_respuesta_promedio']:.1f} hrs", "≤4 hrs"],
        ["Costo Mantenimiento Correctivo", f"${kpis_mes['costo_mantenimiento_correctivo']:,.0f}", "Variable"],
        ["Costo Mantenimiento Preventivo", f"${kpis_mes['costo_mantenimiento_preventivo']:,.0f}", "Variable"]
    ], columns=["Indicador", "Valor Actual", "Objetivo"])
    
    st.dataframe(kpis_df, use_container_width=True, hide_index=True)
    
    st.markdown("### 🏢 Análisis por Área")
    
    areas_df = pd.DataFrame(datos_areas)
    areas_df['Costo Formateado'] = areas_df['costo_mantenimiento'].apply(lambda x: f"${x:,.0f}")
    areas_df['Uptime %'] = areas_df['uptime'].round(1)
    
    st.dataframe(
        areas_df[['area', 'equipos_total', 'Uptime %', 'ordenes_trabajo', 'Costo Formateado', 'incidentes']].rename(columns={
            'area': 'Área',
            'equipos_total': 'Equipos',
            'ordenes_trabajo': 'Órdenes Trabajo',
            'Costo Formateado': 'Costo Mantenimiento',
            'incidentes': 'Incidentes'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("### 📊 Gráficos Incluidos en el Reporte")
    
    tab1, tab2, tab3 = st.tabs(["Uptime por Área", "Costos de Mantenimiento", "Estado de Equipos"])
    
    with tab1:
        fig_uptime = px.bar(
            areas_df,
            x='area',
            y='uptime',
            title='Uptime por Área (%)',
            color='uptime',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_uptime, use_container_width=True)
    
    with tab2:
        costos_data = pd.DataFrame({
            'Tipo': ['Correctivo', 'Preventivo'],
            'Costo': [kpis_mes['costo_mantenimiento_correctivo'], kpis_mes['costo_mantenimiento_preventivo']]
        })
        
        fig_costos = px.pie(
            costos_data,
            values='Costo',
            names='Tipo',
            title='Distribución de Costos de Mantenimiento'
        )
        st.plotly_chart(fig_costos, use_container_width=True)
    
    with tab3:
        estados_data = pd.DataFrame({
            'Estado': ['Operativos', 'En Mantenimiento', 'Fuera de Servicio'],
            'Cantidad': [
                kpis_mes['equipos_operativos'],
                kpis_mes['equipos_mantenimiento'],
                kpis_mes['equipos_fuera_servicio']
            ]
        })
        
        fig_equipos = px.bar(
            estados_data,
            x='Estado',
            y='Cantidad',
            title='Estado de Equipos',
            color='Estado',
            color_discrete_map={
                'Operativos': '#28a745',
                'En Mantenimiento': '#ffc107',
                'Fuera de Servicio': '#dc3545'
            }
        )
        st.plotly_chart(fig_equipos, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📌 Eventos Relevantes")
        for i, evento in enumerate(eventos, 1):
            st.write(f"{i}. {evento}")
    
    with col2:
        st.markdown("### 🚧 Proyectos en Curso")
        for proyecto in proyectos:
            st.write(f"**{proyecto['nombre']}**: {proyecto['progreso']}% - {proyecto['estado']}")
    
    st.markdown("---")
    st.markdown("## 📥 Generar Reporte PDF")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        incluir_graficos = st.checkbox("📊 Incluir Gráficos", value=True)
    
    with col2:
        incluir_analisis_areas = st.checkbox("🏢 Incluir Análisis por Área", value=True)
    
    with col3:
        incluir_proyectos = st.checkbox("🚧 Incluir Proyectos", value=True)
    
    if st.button("📄 Generar Reporte PDF", type="primary", use_container_width=True):
        with st.spinner("🔄 Generando reporte PDF..."):
            try:
                if incluir_graficos:
                    graficos = crear_graficos_reporte(kpis_mes, datos_areas)
                else:
                    graficos = {}
                
                datos_areas_filtrados = datos_areas if incluir_analisis_areas else []
                proyectos_filtrados = proyectos if incluir_proyectos else []
                
                pdf_buffer = generar_pdf_reporte(
                    datos_departamento,
                    kpis_mes,
                    datos_areas_filtrados,
                    eventos,
                    proyectos_filtrados,
                    graficos
                )
                
                nombre_archivo = f"Reporte_Ejecutivo_{meses[mes_seleccionado]}_{ano_seleccionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                st.success("✅ Reporte generado exitosamente!")
                st.download_button(
                    label="📥 Descargar Reporte PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                st.info(f"""
                **📄 Archivo generado:** {nombre_archivo}
                **📊 Período:** {meses[mes_seleccionado]} {ano_seleccionado}
                **🔢 Tamaño:** {len(pdf_buffer.getvalue())} bytes
                **📅 Fecha de generación:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                """)
                
            except Exception as e:
                st.error(f"❌ Error al generar el reporte: {str(e)}")
                st.error("Por favor, contacta al administrador del sistema.")

def mostrar_modulo_reportes():
    """Función de compatibilidad para main.py"""
    mostrar_reportes()