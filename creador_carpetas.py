from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import re
import streamlit as st

# Autenticación con la API de Google Drive
info = st.secrets["google_service_account"]
scope = ['https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
drive_service = build('drive', 'v3', credentials=credentials)

# **ID de la carpeta donde se encuentran las subcarpetas EQU-0000001** 
QR_FOLDER_ID = "1ziehslbMBQZ626dHDn5tJlOkCOVW9xYM"  

# Lista de subcarpetas a crear dentro de cada carpeta EQU-XXXXXXX
subcarpetas = [
    "Manual", 
    "Fotos", 
    "Ficha técnica", 
    "Prueba de seguridad", 
    "Informe de mal uso", 
    "Informes técnicos"
]

def obtener_ultimo_codigo():
    """Obtener el último código de carpeta creado y generar el siguiente"""
    try:
        query = f"'{QR_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = drive_service.files().list(q=query, pageSize=1000).execute()
        folders = results.get('files', [])

        nombres_folders = [f['name'] for f in folders if re.match(r"EQU-\d{7}", f['name'])]
        
        if nombres_folders:
            numeros = [int(re.sub(r"\D", "", name)) for name in nombres_folders]
            siguiente_numero = max(numeros) + 1
        else:
            siguiente_numero = 1

        return f"EQU-{siguiente_numero:07d}"
    except HttpError as error:
        print(f"Hubo un error al obtener las carpetas: {error}")
        return None

def crear_nueva_carpeta(nombre_carpeta):
    """Crear una nueva carpeta en Google Drive"""
    file_metadata = {
        'name': nombre_carpeta,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [QR_FOLDER_ID]
    }
    try:
        carpeta = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"Carpeta principal creada: {nombre_carpeta}")
        return carpeta.get('id')
    except HttpError as error:
        print(f"Hubo un error al crear la carpeta principal: {error}")
        return None

def crear_subcarpetas(carpeta_id):
    """Crear las subcarpetas dentro de la carpeta principal creada"""
    for subcarpeta in subcarpetas:
        file_metadata = {
            'name': subcarpeta,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [carpeta_id]
        }
        try:
            drive_service.files().create(body=file_metadata, fields='id').execute()
            print(f"Subcarpeta creada: {subcarpeta}")
        except HttpError as error:
            print(f"Hubo un error al crear la subcarpeta: {error}")
