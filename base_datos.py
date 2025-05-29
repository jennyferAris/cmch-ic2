import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def mostrar_base_datos():
    st.title("📊 Base de Datos - Clínica")

    # Autenticación
    info = st.secrets["google_service_account"]
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']
    credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    cliente = gspread.authorize(credenciales)

    try:
        hoja = cliente.open("Base de datos").sheet1
        datos = hoja.get_all_records()
        df = pd.DataFrame(datos)

        st.success("✅ Datos cargados correctamente desde Google Sheets.")
        st.dataframe(df)

    except Exception as e:
        st.error("❌ Error al cargar los datos.")
        st.exception(e)
