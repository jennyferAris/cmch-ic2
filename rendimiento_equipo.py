import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date

def verificar_permisos_rendimiento():
    """Verifica permisos para acceso al módulo"""
    nivel_usuario = st.session_state.get('rol_nivel', 0)
    return nivel_usuario >= 3

def cargar_datos_personal():
    """Datos del personal del departamento"""
    if 'personal_departamento' not in st.session_state:
        st.session_state.personal_departamento = [
            {
                'id': 1, 'nombre': 'Ing. Walter Ríos', 'cargo': 'Jefe de Ingeniería Clínica',
                'tipo': 'permanente', 'nivel': 5, 'activo': True
            },
            {
                'id': 2, 'nombre': 'Ing. Milagros Alvites', 'cargo': 'Ingeniero Junior',
                'tipo': 'permanente', 'nivel': 2, 'activo': True
            },
            {
                'id': 3, 'nombre': 'Piero ', 'cargo': 'Practicante Preprofesional',
                'tipo': 'permanente', 'nivel': 1, 'activo': True
            },
            {
                'id': 4, 'nombre': 'Ana Torres', 'cargo': 'Pasante Rotatorio',
                'tipo': 'temporal', 'nivel': 1, 'activo': True
            },
            {
                'id': 5, 'nombre': 'Luis Ramírez', 'cargo': 'Pasante Rotatorio',
                'tipo': 'temporal', 'nivel': 1, 'activo': True
            }
        ]
    return st.session_state.personal_departamento

def generar_metricas_persona(persona_id):
    """Genera métricas simuladas para una persona"""
    np.random.seed(persona_id + 42)
    personal = cargar_datos_personal()
    persona = next((p for p in personal if p['id'] == persona_id), None)
    
    if not persona:
        return {}
    
    # Factor según nivel y tipo
    factor = persona['nivel'] * 0.2
    es_temporal = persona['tipo'] == 'temporal'
    
    if es_temporal:
        # Métricas para pasantes (más básicas)
        metricas = {
            'ordenes': np.random.randint(5, 12),
            'tiempo_promedio': np.random.uniform(5, 9),
            'satisfaccion': np.random.uniform(3.0, 4.2),
            'asistencia': np.random.uniform(85, 98),
            'capacitacion': np.random.randint(15, 25),
            'puntuacion': np.random.uniform(55, 80)
        }
    else:
        # Métricas para personal permanente
        metricas = {
            'ordenes': int(np.random.randint(15, 35) * (1 + factor)),
            'tiempo_promedio': np.random.uniform(2, 6) / (1 + factor),
            'satisfaccion': np.random.uniform(3.5 + factor, 5.0),
            'asistencia': np.random.uniform(90, 100),
            'capacitacion': np.random.randint(5, 20),
            'puntuacion': np.random.uniform(70 + factor*10, 95 + factor*5)
        }
    
    return metricas

def mostrar_dashboard_rendimiento():
    """Dashboard principal simplificado"""
    st.markdown("## 📊 Rendimiento del Equipo")
    
    # Información básica
    st.info("📋 Las métricas departamentales se basan en personal permanente. Los pasantes se evalúan individualmente.")
    
    # Personal permanente vs temporal
    personal = cargar_datos_personal()
    permanentes = [p for p in personal if p['tipo'] == 'permanente' and p['activo']]
    temporales = [p for p in personal if p['tipo'] == 'temporal' and p['activo']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👔 Personal Permanente")
        for p in permanentes:
            st.write(f"• {p['nombre']} - {p['cargo']}")
    
    with col2:
        st.markdown("### 🔄 Pasantes Rotativos")
        for p in temporales:
            st.write(f"• {p['nombre']} - {p['cargo']}")
    
    # KPIs principales
    st.markdown("### 📈 Indicadores Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⚡ Uptime General", "92.5%", "+2.5%")
    
    with col2:
        st.metric("😊 Satisfacción", "4.2/5", "+0.2")
    
    with col3:
        st.metric("⏱️ Tiempo Respuesta", "3.8h", "-0.5h")
    
    with col4:
        st.metric("👥 Personal Activo", f"{len(personal)}", f"+{len(temporales)} pasantes")
    
    # Ranking del equipo
    st.markdown("### 🏆 Top Performers")
    
    ranking_data = []
    for persona in personal:
        metricas = generar_metricas_persona(persona['id'])
        ranking_data.append({
            'Nombre': persona['nombre'],
            'Tipo': '🔄' if persona['tipo'] == 'temporal' else '👔',
            'Puntuación': f"{metricas['puntuacion']:.1f}",
            'Órdenes': metricas['ordenes'],
            'Satisfacción': f"{metricas['satisfaccion']:.1f}"
        })
    
    df_ranking = pd.DataFrame(ranking_data)
    df_ranking = df_ranking.sort_values('Puntuación', ascending=False, key=lambda x: pd.to_numeric(x))
    
    st.dataframe(df_ranking, use_container_width=True, hide_index=True)

def mostrar_rendimiento_individual():
    """Análisis individual simplificado"""
    st.markdown("## 👤 Rendimiento Individual")
    
    personal = cargar_datos_personal()
    
    # Selección de persona
    persona_seleccionada = st.selectbox(
        "Seleccionar Personal",
        options=personal,
        format_func=lambda x: f"{x['nombre']} - {x['cargo']} {'[PASANTE]' if x['tipo'] == 'temporal' else ''}",
    )
    
    if persona_seleccionada:
        metricas = generar_metricas_persona(persona_seleccionada['id'])
        es_temporal = persona_seleccionada['tipo'] == 'temporal'
        
        # Info del empleado
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📋 Información")
            st.write(f"**Nombre:** {persona_seleccionada['nombre']}")
            st.write(f"**Cargo:** {persona_seleccionada['cargo']}")
            st.write(f"**Tipo:** {'Pasante Rotatorio' if es_temporal else 'Personal Permanente'}")
            
            # Puntuación con color
            puntuacion = metricas['puntuacion']
            if puntuacion >= 85:
                color, nivel = "#28a745", "Excelente"
            elif puntuacion >= 75:
                color, nivel = "#17a2b8", "Bueno"
            elif puntuacion >= 65:
                color, nivel = "#ffc107", "Regular"
            else:
                color, nivel = "#dc3545", "Necesita Mejora"
            
            st.markdown(f"""
            <div style="background-color: {color}; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <h3>{puntuacion:.1f}/100</h3>
                <h4>{nivel}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Métricas clave
            st.markdown("### 📊 Métricas del Período")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Órdenes Completadas", metricas['ordenes'])
                st.metric("Tiempo Promedio", f"{metricas['tiempo_promedio']:.1f}h")
            
            with col_b:
                st.metric("Satisfacción Usuario", f"{metricas['satisfaccion']:.1f}/5")
                st.metric("Asistencia", f"{metricas['asistencia']:.1f}%")
            
            with col_c:
                st.metric("Horas Capacitación", metricas['capacitacion'])
                if es_temporal:
                    st.info("📚 En formación")
                else:
                    st.success("✅ Personal clave")
        
        # Gráfico de radar simple
        st.markdown("### 🎯 Perfil de Rendimiento")
        
        if es_temporal:
            categorias = ['Productividad', 'Calidad', 'Asistencia', 'Aprendizaje']
            valores = [
                min(100, metricas['ordenes'] * 8),
                metricas['satisfaccion'] * 20,
                metricas['asistencia'],
                min(100, metricas['capacitacion'] * 4)
            ]
            objetivo = [60, 70, 85, 80]
        else:
            categorias = ['Productividad', 'Calidad', 'Asistencia', 'Desarrollo']
            valores = [
                min(100, metricas['ordenes'] * 3),
                metricas['satisfaccion'] * 20,
                metricas['asistencia'],
                min(100, metricas['capacitacion'] * 5)
            ]
            objetivo = [80, 85, 90, 75]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=objetivo,
            theta=categorias,
            fill='toself',
            name='Objetivo',
            opacity=0.3,
            line_color='gray'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias,
            fill='toself',
            name=persona_seleccionada['nombre'],
            line_color=color
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=f"Rendimiento - {persona_seleccionada['nombre']}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recomendaciones simples
        st.markdown("### 💡 Recomendaciones")
        
        if es_temporal:
            if metricas['tiempo_promedio'] > 7:
                st.warning("⚡ Enfocarse en mejorar velocidad de procedimientos")
            if metricas['capacitacion'] < 20:
                st.info("📚 Aumentar horas de capacitación teórica")
            if metricas['satisfaccion'] >= 4.0:
                st.success("👍 Excelente recepción por parte de usuarios")
        else:
            if metricas['ordenes'] < 20:
                st.warning("📈 Incrementar productividad en órdenes")
            if metricas['satisfaccion'] >= 4.5:
                st.success("⭐ Alta satisfacción del usuario")
            if metricas['capacitacion'] < 10:
                st.info("🎓 Considerar capacitación adicional")

def mostrar_rendimiento_equipo():
    """Función principal del módulo"""
    if not verificar_permisos_rendimiento():
        st.error("❌ No tienes permisos para acceder a este módulo")
        st.info("👮‍♂️ Requiere nivel de Supervisor o superior")
        return
    
    st.title("📊 Rendimiento del Equipo")
    
    # Pestañas principales
    tab1, tab2 = st.tabs(["📊 Dashboard General", "👤 Análisis Individual"])
    
    with tab1:
        mostrar_dashboard_rendimiento()
    
    with tab2:
        mostrar_rendimiento_individual()