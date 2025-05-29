import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def cargar_hoja_tareas():
    info = st.secrets["google_service_account"]
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    cliente = gspread.authorize(creds)
    hoja = cliente.open("Base de datos").worksheet("Tareas")
    return hoja

def mostrar_tareas_asignadas(correo_usuario):
    hoja = cargar_hoja_tareas()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    tareas_usuario = df[df["Responsable"] == correo_usuario]

    st.subheader("📋 Tareas asignadas a ti")
    for i, fila in tareas_usuario.iterrows():
        with st.expander(f"Tarea #{fila['ID']} - {fila['Equipo']}"):
            st.write(f"📅 Fecha: {fila['Fecha asignación']}")
            st.write(f"📝 Descripción: {fila['Descripción']}")
            st.write(f"⚠️ Urgencia: `{fila['Urgencia']}`")
            st.write(f"🔄 Estado actual: `{fila['Estado']}`")

            if fila["Estado"] != "Completada":
                if st.button(f"✅ Marcar como completada (ID {fila['ID']})"):
                    hoja.update_cell(i + 2, 7, "Completada")
                    st.success("✅ Tarea marcada como completada.")
                    st.experimental_rerun()

def mostrar_todas_las_tareas():
    hoja = cargar_hoja_tareas()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    st.subheader("📂 Todas las tareas")
    st.dataframe(df)

def asignar_tarea_form():
    st.subheader("🆕 Asignar nueva tarea")

    hoja = cargar_hoja_tareas()
    datos = hoja.get_all_records()
    nuevo_id = len(datos) + 1

    with st.form("form_tarea"):
        equipo = st.text_input("Equipo")
        descripcion = st.text_area("Descripción")
        responsable = st.text_input("Responsable (correo)")
        fecha = st.date_input("Fecha de asignación")
        urgencia = st.selectbox("Nivel de urgencia", ["Alta", "Media", "Baja"])
        enviar = st.form_submit_button("Asignar")

        if enviar:
            nueva_fila = [nuevo_id, equipo, descripcion, responsable, str(fecha), urgencia, "Pendiente"]
            hoja.append_row(nueva_fila)
            st.success("📌 Tarea asignada exitosamente.")
