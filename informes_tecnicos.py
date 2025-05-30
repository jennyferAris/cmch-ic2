import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread

info = st.secrets["google_service_account"]
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
cliente = gspread.authorize(credenciales)

drive_service = build('drive', 'v3', credentials=credenciales)

folder2 = st.secrets["google_drive"]["qr_folder_id2"]

def subir_informe_drive(pdf_buffer, nombre_archivo, tecnico_info):
    """Sube el informe PDF a Google Drive usando solo la carpeta folder2"""
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