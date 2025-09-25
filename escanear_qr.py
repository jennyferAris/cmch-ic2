# escanear_qr.py
from __future__ import annotations
import io
from typing import List, Dict, Optional, Tuple

import streamlit as st

# Google Drive (Service Account)
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# ==========================
# CONFIG
# ==========================
PARENT_FOLDER_ID = "1ziehslbMBQZ626dHDn5tJlOkCOVW9xYM"
SCOPES = ["https://www.googleapis.com/auth/drive"]

GOOGLE_EXPORT_MAP = {
    "application/vnd.google-apps.document": "application/pdf",
    "application/vnd.google-apps.spreadsheet": "application/pdf",
    "application/vnd.google-apps.presentation": "application/pdf",
    "application/vnd.google-apps.drawing": "application/pdf",
}

# ==========================
# AUTH / SERVICE
# ==========================
@st.cache_resource(show_spinner=False)
def build_drive_service():
    info = st.secrets["google_service_account"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPES)
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    return service

# ==========================
# HELPERS DRIVE
# ==========================
def find_folder_by_name(service, parent_id: str, name: str) -> Optional[str]:
    q = (
        f"'{parent_id}' in parents and "
        f"name = '{name}' and "
        "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    res = service.files().list(
        q=q,
        fields="files(id,name)",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def list_files_in_folder(service, folder_id: str) -> List[Dict]:
    res = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id,name,mimeType,size,webViewLink,iconLink)",
        pageSize=1000,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return res.get("files", [])

def download_file_bytes(service, file_id: str, mime_type: str, name_fallback: str) -> Tuple[bytes, str, str]:
    """
    Descarga un archivo de Drive. 
    Si es nativo de Google (Docs/Sheets/Slides) -> exporta.
    Si es binario -> descarga normal.
    """

    # 🔹 Consultar siempre el MIME real
    meta = service.files().get(fileId=file_id, fields="name,mimeType").execute()
    real_name = meta.get("name", name_fallback)
    real_mime = meta.get("mimeType", mime_type or "application/octet-stream")

    try:
        # 🔹 Si es archivo nativo de Google, usar export
        if real_mime in GOOGLE_EXPORT_MAP:
            export_mime = GOOGLE_EXPORT_MAP[real_mime]
            request = service.files().export(fileId=file_id, mimeType=export_mime)
        else:
            # 🔹 Si no, intentar descarga normal
            request = service.files().get_media(fileId=file_id)

        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        data = buf.getvalue()

        # Ajustar nombre si se exportó
        download_name = real_name
        if real_mime in GOOGLE_EXPORT_MAP and GOOGLE_EXPORT_MAP[real_mime] == "application/pdf":
            if not download_name.lower().endswith(".pdf"):
                download_name += ".pdf"

        return data, download_name, GOOGLE_EXPORT_MAP.get(real_mime, real_mime)

    except HttpError as he:
        # 🔹 Fallback: si dio 403 (archivo Google tratado como binario), forzar export
        if "fileNotDownloadable" in str(he) and real_mime in GOOGLE_EXPORT_MAP:
            export_mime = GOOGLE_EXPORT_MAP[real_mime]
            request = service.files().export(fileId=file_id, mimeType=export_mime)
            buf = io.BytesIO()
            downloader = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            data = buf.getvalue()
            download_name = real_name + ".pdf"
            return data, download_name, export_mime
        else:
            raise


def get_files_for_code(service, code: str) -> List[Dict]:
    if not code or not code.strip():
        raise ValueError("Código vacío.")
    code = code.strip()
    folder_id = find_folder_by_name(service, PARENT_FOLDER_ID, code)
    if not folder_id:
        raise ValueError(f"No se encontró la carpeta '{code}' dentro de Equipos médicos.")
    return list_files_in_folder(service, folder_id)

# ==========================
# UI STREAMLIT
# ==========================
def render_ui():
    st.set_page_config(page_title="Escanear QR – Equipos médicos", page_icon="🩺", layout="centered")
    st.title("Escaneo de QR – Equipos médicos")
    st.caption("Lee el código (p. ej. `EQU-000012`) y muestra/descarga los archivos de la carpeta correspondiente.")

    service = build_drive_service()

    code = st.text_input("Código leído", placeholder="EQU-000012")

    if st.button("Buscar archivos", use_container_width=True) and code:
        try:
            with st.spinner("Buscando carpeta y listando archivos..."):
                files = get_files_for_code(service, code)

            st.subheader(f"Equipo: {code}")
            if not files:
                st.info("La carpeta existe pero no contiene archivos.")
                return

            for f in files:
                with st.container(border=True):
                    st.write(f"**{f['name']}**")
                    meta = f"{f['mimeType']}"
                    if f.get("size"):
                        meta += f" · {int(f['size']):,} bytes".replace(",", ".")
                    st.caption(meta)

                    c1, c2 = st.columns(2)
                    with c1:
                        if f.get("webViewLink"):
                            st.link_button("Ver en Drive", f["webViewLink"], use_container_width=True)

                    with c2:
                        try:
                            data, dl_name, dl_mime = download_file_bytes(service, f["id"], f["mimeType"], f["name"])
                            st.download_button(
                                "Descargar",
                                data=data,
                                file_name=dl_name,
                                mime=dl_mime,
                                use_container_width=True,
                            )
                        except HttpError as he:
                            st.error(f"No se pudo descargar: {he}")

                st.divider()

        except ValueError as ve:
            st.warning(str(ve))
        except HttpError as he:
            st.error(f"Error de Google Drive: {he}")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    render_ui()
