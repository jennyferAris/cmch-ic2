import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuración de colores del tema
COLORES = {
    'primary': '#1f77b4',
    'success': '#2ca02c', 
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'info': '#17becf',
    'secondary': '#7f7f7f'
}

def generar_datos_simulados():
    """Genera datos simulados para los KPIs mientras no hay datos reales"""
    
    # Datos base simulados
    np.random.seed(42)  # Para resultados consistentes
    
    # Generar fechas del último año
    fechas = pd.date_range(
        start=datetime.now() - timedelta(days=365),
        end=datetime.now(),
        freq='D'
    )
    
    # Datos por equipo (simulados)
    equipos_data = []
    equipos_sample = [
        {'nombre': 'Ventilador UCI-001', 'area': 'UCI', 'tipo': 'Ventilador'},
        {'nombre': 'Resonancia RM-15', 'area': 'Imagenología', 'tipo': 'Resonancia'},
        {'nombre': 'Bomba Infusión BM-23', 'area': 'UCI', 'tipo': 'Bomba'},
        {'nombre': 'Monitor Signos VM-08', 'area': 'Emergencia', 'tipo': 'Monitor'},
        {'nombre': 'Rayos X RX-12', 'area': 'Imagenología', 'tipo': 'Rayos X'},
        {'nombre': 'Ventilador EMER-004', 'area': 'Emergencia', 'tipo': 'Ventilador'},
        {'nombre': 'Ecógrafo ECO-09', 'area': 'Consulta Externa', 'tipo': 'Ecógrafo'},
        {'nombre': 'Desfibrilador DEF-17', 'area': 'Emergencia', 'tipo': 'Desfibrilador'}
    ]
    
    for equipo in equipos_sample:
        # Métricas base para cada equipo
        uptime_base = np.random.uniform(85, 98)  # % uptime base
        downtime_hours = np.random.uniform(10, 150)  # horas downtime al mes
        
        equipos_data.append({
            'equipo': equipo['nombre'],
            'area': equipo['area'],
            'tipo': equipo['tipo'],
            'uptime': uptime_base,
            'downtime_horas_mes': downtime_hours,
            'costo_correctivo': np.random.uniform(500, 5000),  # USD
            'costo_preventivo': np.random.uniform(200, 1500),  # USD
            'mantenimientos_programados': np.random.randint(8, 15),
            'mantenimientos_realizados': np.random.randint(6, 14),
            'cosr': np.random.uniform(0.15, 0.45)  # Cost of Service Ratio
        })
    
    # Datos históricos mensuales
    meses_data = []
    for i in range(12):
        mes = datetime.now() - timedelta(days=30*i)
        meses_data.append({
            'mes': mes.strftime('%Y-%m'),
            'mes_nombre': mes.strftime('%B %Y'),
            'uptime_promedio': np.random.uniform(88, 96),
            'downtime_total': np.random.uniform(200, 800),
            'costo_correctivo_total': np.random.uniform(8000, 25000),
            'costo_preventivo_total': np.random.uniform(5000, 15000),
            'ppm_cumplimiento': np.random.uniform(75, 95)
        })
    
    return pd.DataFrame(equipos_data), pd.DataFrame(meses_data)

def calcular_kpis_globales(df_equipos, df_historico):
    """Calcula KPIs globales del hospital"""
    
    # Uptime promedio
    uptime_global = df_equipos['uptime'].mean()
    
    # Downtime total (horas por mes)
    downtime_global = df_equipos['downtime_horas_mes'].sum()
    
    # Costos
    costo_correctivo_total = df_equipos['costo_correctivo'].sum()
    costo_preventivo_total = df_equipos['costo_preventivo'].sum()
    costo_total = costo_correctivo_total + costo_preventivo_total
    
    # COSR promedio
    cosr_global = df_equipos['cosr'].mean()
    
    # PPM (Planned Preventive Maintenance)
    mantenimientos_programados = df_equipos['mantenimientos_programados'].sum()
    mantenimientos_realizados = df_equipos['mantenimientos_realizados'].sum()
    ppm_cumplimiento = (mantenimientos_realizados / mantenimientos_programados * 100) if mantenimientos_programados > 0 else 0
    
    return {
        'uptime': uptime_global,
        'downtime': downtime_global,
        'costo_correctivo': costo_correctivo_total,
        'costo_preventivo': costo_preventivo_total,
        'costo_total': costo_total,
        'cosr': cosr_global,
        'ppm_cumplimiento': ppm_cumplimiento
    }

def crear_gauge_chart(valor, titulo, min_val=0, max_val=100, color_ranges=None):
    """Crea un gráfico de gauge (velocímetro)"""
    
    if color_ranges is None:
        color_ranges = [
            {'range': [0, 50], 'color': COLORES['danger']},
            {'range': [50, 80], 'color': COLORES['warning']},
            {'range': [80, 100], 'color': COLORES['success']}
        ]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': titulo, 'font': {'size': 16}},
        delta = {'reference': 85, 'increasing': {'color': COLORES['success']}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, max_val * 0.5], 'color': '#ffebee'},
                {'range': [max_val * 0.5, max_val * 0.8], 'color': '#fff3e0'},
                {'range': [max_val * 0.8, max_val], 'color': '#e8f5e8'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def crear_grafico_tendencia(df_historico, columna, titulo):
    """Crea gráfico de tendencia temporal"""
    
    fig = px.line(
        df_historico.sort_values('mes'),
        x='mes_nombre',
        y=columna,
        title=titulo,
        markers=True,
        line_shape='spline'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Mes",
        yaxis_title=titulo,
        hovermode='x unified',
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color=COLORES['primary'], width=3),
        marker=dict(size=8, color=COLORES['primary'])
    )
    
    return fig

def crear_grafico_barras_areas(df_equipos):
    """Crea gráfico de barras por área"""
    
    df_areas = df_equipos.groupby('area').agg({
        'uptime': 'mean',
        'costo_correctivo': 'sum',
        'costo_preventivo': 'sum'
    }).reset_index()
    
    df_areas['costo_total'] = df_areas['costo_correctivo'] + df_areas['costo_preventivo']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Uptime Promedio por Área (%)', 'Costos de Mantenimiento por Área (USD)'),
        vertical_spacing=0.15
    )
    
    # Gráfico de Uptime
    fig.add_trace(
        go.Bar(
            x=df_areas['area'],
            y=df_areas['uptime'],
            name='Uptime (%)',
            marker_color=COLORES['success'],
            text=df_areas['uptime'].round(1),
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Gráfico de Costos
    fig.add_trace(
        go.Bar(
            x=df_areas['area'],
            y=df_areas['costo_correctivo'],
            name='Correctivo',
            marker_color=COLORES['danger']
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df_areas['area'],
            y=df_areas['costo_preventivo'],
            name='Preventivo',
            marker_color=COLORES['success']
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        barmode='group'
    )
    
    return fig

def crear_grafico_distribucion_equipos(df_equipos):
    """Crea gráfico de distribución de equipos por tipo"""
    
    distribucion = df_equipos['tipo'].value_counts()
    
    fig = px.pie(
        values=distribucion.values,
        names=distribucion.index,
        title="Distribución de Equipos por Tipo",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.05)
    )
    
    return fig

def mostrar_dashboard_kpis():
    """Función principal del dashboard KPIs"""
    
    # Verificar permisos
    nivel_usuario = st.session_state.get('rol_nivel', 0)
    nombre_usuario = st.session_state.get('name', '')
    
    if nivel_usuario < 4:
        st.error("🚫 **Acceso Denegado**")
        st.warning("Solo Ingenieros (Nivel 4+) pueden acceder al Dashboard KPIs.")
        return
    
    st.title("📊 Dashboard KPIs - Bioingeniería")
    st.info(f"👤 **{nombre_usuario}** | Análisis de Indicadores Clave de Rendimiento")
    
    # Advertencia de datos simulados
    st.warning("⚠️ **Datos Simulados**: Este dashboard muestra datos de ejemplo. Conecta con tu sistema real para obtener métricas precisas.")
    
    # Cargar datos simulados
    with st.spinner("📊 Cargando datos de KPIs..."):
        df_equipos, df_historico = generar_datos_simulados()
        kpis = calcular_kpis_globales(df_equipos, df_historico)
    
    # Filtros principales
    st.markdown("### 🎛️ Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        areas_disponibles = ['Todas'] + sorted(df_equipos['area'].unique().tolist())
        filtro_area = st.selectbox("🏢 Área", areas_disponibles)
    
    with col2:
        tipos_disponibles = ['Todos'] + sorted(df_equipos['tipo'].unique().tolist())
        filtro_tipo = st.selectbox("⚙️ Tipo de Equipo", tipos_disponibles)
    
    with col3:
        periodo = st.selectbox("📅 Período", ["Último mes", "Últimos 3 meses", "Últimos 6 meses", "Último año"])
    
    # Aplicar filtros
    df_filtrado = df_equipos.copy()
    if filtro_area != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['area'] == filtro_area]
    if filtro_tipo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipo'] == filtro_tipo]
    
    # Recalcular KPIs con datos filtrados
    if not df_filtrado.empty:
        kpis_filtrado = calcular_kpis_globales(df_filtrado, df_historico)
    else:
        kpis_filtrado = kpis
    
    st.markdown("---")
    
    # **SECCIÓN 1: KPIs PRINCIPALES**
    st.markdown("## 🎯 KPIs Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Uptime
        uptime_color = COLORES['success'] if kpis_filtrado['uptime'] >= 90 else COLORES['warning'] if kpis_filtrado['uptime'] >= 80 else COLORES['danger']
        st.metric(
            label="⬆️ Uptime",
            value=f"{kpis_filtrado['uptime']:.1f}%",
            delta=f"{kpis_filtrado['uptime'] - 85:.1f}% vs objetivo (85%)",
            delta_color="normal"
        )
    
    with col2:
        # Downtime
        st.metric(
            label="⬇️ Downtime",
            value=f"{kpis_filtrado['downtime']:.0f} hrs/mes",
            delta=f"{50 - kpis_filtrado['downtime']:.0f} hrs vs objetivo (50h)",
            delta_color="inverse"
        )
    
    with col3:
        # COSR
        cosr_status = "Excelente" if kpis_filtrado['cosr'] < 0.2 else "Bueno" if kpis_filtrado['cosr'] < 0.3 else "Mejorable"
        st.metric(
            label="💰 COSR",
            value=f"{kpis_filtrado['cosr']:.3f}",
            delta=f"Estado: {cosr_status}",
            delta_color="normal"
        )
    
    with col4:
        # PPM
        ppm_color = COLORES['success'] if kpis_filtrado['ppm_cumplimiento'] >= 90 else COLORES['warning']
        st.metric(
            label="🔧 PPM Cumplimiento",
            value=f"{kpis_filtrado['ppm_cumplimiento']:.1f}%",
            delta=f"{kpis_filtrado['ppm_cumplimiento'] - 90:.1f}% vs objetivo (90%)",
            delta_color="normal"
        )
    
    # **SECCIÓN 2: GRÁFICOS GAUGE**
    st.markdown("## 🎛️ Indicadores Visuales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_uptime = crear_gauge_chart(
            kpis_filtrado['uptime'], 
            "Uptime (%)",
            min_val=0, 
            max_val=100
        )
        st.plotly_chart(fig_uptime, use_container_width=True)
    
    with col2:
        fig_cosr = crear_gauge_chart(
            kpis_filtrado['cosr'] * 100, 
            "COSR (%)",
            min_val=0, 
            max_val=50,
            color_ranges=[
                {'range': [0, 20], 'color': COLORES['success']},
                {'range': [20, 30], 'color': COLORES['warning']},
                {'range': [30, 50], 'color': COLORES['danger']}
            ]
        )
        st.plotly_chart(fig_cosr, use_container_width=True)
    
    with col3:
        fig_ppm = crear_gauge_chart(
            kpis_filtrado['ppm_cumplimiento'], 
            "PPM Cumplimiento (%)",
            min_val=0, 
            max_val=100
        )
        st.plotly_chart(fig_ppm, use_container_width=True)
    
    # **SECCIÓN 3: ANÁLISIS DE COSTOS**
    st.markdown("## 💸 Análisis de Costos de Mantenimiento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de torta para costos
        costos_data = {
            'Correctivo': kpis_filtrado['costo_correctivo'],
            'Preventivo': kpis_filtrado['costo_preventivo']
        }
        
        fig_costos = px.pie(
            values=list(costos_data.values()),
            names=list(costos_data.keys()),
            title="Distribución de Costos de Mantenimiento",
            color_discrete_map={
                'Correctivo': COLORES['danger'],
                'Preventivo': COLORES['success']
            }
        )
        
        fig_costos.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            hovertemplate='<b>%{label}</b><br>Costo: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
        )
        
        st.plotly_chart(fig_costos, use_container_width=True)
    
    with col2:
        # Métricas de costo
        st.markdown("### 📊 Resumen de Costos")
        
        costo_total = kpis_filtrado['costo_correctivo'] + kpis_filtrado['costo_preventivo']
        ratio_correctivo = (kpis_filtrado['costo_correctivo'] / costo_total * 100) if costo_total > 0 else 0
        
        st.metric("💰 Costo Total", f"${costo_total:,.0f}")
        st.metric("🔴 Mantenimiento Correctivo", f"${kpis_filtrado['costo_correctivo']:,.0f}", f"{ratio_correctivo:.1f}% del total")
        st.metric("🟢 Mantenimiento Preventivo", f"${kpis_filtrado['costo_preventivo']:,.0f}", f"{100-ratio_correctivo:.1f}% del total")
        
        # Recomendación
        if ratio_correctivo > 60:
            st.error("⚠️ **Alto costo correctivo**. Considera aumentar mantenimiento preventivo.")
        elif ratio_correctivo > 40:
            st.warning("⚠️ **Costo correctivo moderado**. Monitorea tendencias.")
        else:
            st.success("✅ **Buen balance** entre mantenimiento correctivo y preventivo.")
    
    # **SECCIÓN 4: TENDENCIAS TEMPORALES**
    st.markdown("## 📈 Tendencias Temporales")
    
    tab1, tab2, tab3 = st.tabs(["📊 Uptime/Downtime", "💰 Costos", "🔧 PPM"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_uptime_trend = crear_grafico_tendencia(df_historico, 'uptime_promedio', 'Uptime Promedio (%)')
            st.plotly_chart(fig_uptime_trend, use_container_width=True)
        
        with col2:
            fig_downtime_trend = crear_grafico_tendencia(df_historico, 'downtime_total', 'Downtime Total (horas)')
            st.plotly_chart(fig_downtime_trend, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_cm_trend = crear_grafico_tendencia(df_historico, 'costo_correctivo_total', 'Costo Correctivo (USD)')
            st.plotly_chart(fig_cm_trend, use_container_width=True)
        
        with col2:
            fig_sm_trend = crear_grafico_tendencia(df_historico, 'costo_preventivo_total', 'Costo Preventivo (USD)')
            st.plotly_chart(fig_sm_trend, use_container_width=True)
    
    with tab3:
        fig_ppm_trend = crear_grafico_tendencia(df_historico, 'ppm_cumplimiento', 'PPM Cumplimiento (%)')
        st.plotly_chart(fig_ppm_trend, use_container_width=True)
    
    # **SECCIÓN 5: ANÁLISIS POR ÁREA**
    st.markdown("## 🏢 Análisis por Área")
    
    fig_areas = crear_grafico_barras_areas(df_filtrado)
    st.plotly_chart(fig_areas, use_container_width=True)
    
    # **SECCIÓN 6: DISTRIBUCIÓN DE EQUIPOS**
    st.markdown("## ⚙️ Distribución de Equipos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tipos = crear_grafico_distribucion_equipos(df_filtrado)
        st.plotly_chart(fig_tipos, use_container_width=True)
    
    with col2:
        # Tabla resumen por área
        st.markdown("### 📋 Resumen por Área")
        
        resumen_areas = df_filtrado.groupby('area').agg({
            'uptime': ['mean', 'min', 'max'],
            'downtime_horas_mes': 'sum',
            'costo_correctivo': 'sum',
            'costo_preventivo': 'sum'
        }).round(2)
        
        # Aplanar columnas
        resumen_areas.columns = ['Uptime Prom', 'Uptime Min', 'Uptime Max', 'Downtime Total', 'Costo Correctivo', 'Costo Preventivo']
        resumen_areas['Costo Total'] = resumen_areas['Costo Correctivo'] + resumen_areas['Costo Preventivo']
        
        st.dataframe(resumen_areas, use_container_width=True)
    
    # **SECCIÓN 7: ALERTAS Y RECOMENDACIONES**
    st.markdown("## 🚨 Alertas y Recomendaciones")
    
    alertas = []
    
    # Generar alertas basadas en KPIs
    if kpis_filtrado['uptime'] < 85:
        alertas.append({
            'tipo': 'error',
            'mensaje': f"⬇️ **Uptime crítico**: {kpis_filtrado['uptime']:.1f}% (objetivo: >85%)"
        })
    
    if kpis_filtrado['ppm_cumplimiento'] < 80:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"🔧 **PPM bajo**: {kpis_filtrado['ppm_cumplimiento']:.1f}% de cumplimiento (objetivo: >90%)"
        })
    
    if kpis_filtrado['cosr'] > 0.35:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"💰 **COSR alto**: {kpis_filtrado['cosr']:.3f} (objetivo: <0.30)"
        })
    
    if (kpis_filtrado['costo_correctivo'] / (kpis_filtrado['costo_correctivo'] + kpis_filtrado['costo_preventivo'])) > 0.6:
        alertas.append({
            'tipo': 'info',
            'mensaje': "📊 **Recomendación**: Incrementar inversión en mantenimiento preventivo para reducir costos correctivos"
        })
    
    if not alertas:
        st.success("✅ **Todos los KPIs dentro de rangos aceptables**")
    else:
        for alerta in alertas:
            if alerta['tipo'] == 'error':
                st.error(alerta['mensaje'])
            elif alerta['tipo'] == 'warning':
                st.warning(alerta['mensaje'])
            else:
                st.info(alerta['mensaje'])
    
    # **SECCIÓN 8: EXPORTACIÓN DE DATOS**
    st.markdown("## 📥 Exportación de Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar KPIs", type="secondary"):
            kpis_export = pd.DataFrame([kpis_filtrado])
            csv = kpis_export.to_csv(index=False)
            st.download_button(
                "📥 Descargar KPIs CSV",
                csv,
                f"kpis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("⚙️ Exportar Equipos", type="secondary"):
            csv_equipos = df_filtrado.to_csv(index=False)
            st.download_button(
                "📥 Descargar Equipos CSV",
                csv_equipos,
                f"equipos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    with col3:
        if st.button("📈 Exportar Histórico", type="secondary"):
            csv_historico = df_historico.to_csv(index=False)
            st.download_button(
                "📥 Descargar Histórico CSV",
                csv_historico,
                f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

# Función de compatibilidad para main.py
def mostrar_modulo_dashboard():
    """Función de compatibilidad para main.py"""
    mostrar_dashboard_kpis()