import streamlit as st
import pandas as pd
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from datetime import datetime
import tempfile
import os

class GoogleDriveManager:
    def __init__(self):
        """Inicializa el manager de Google Drive con las credenciales de secrets"""
        try:
            # Obtener credenciales del service account desde secrets
            service_account_info = {
                "type": st.secrets["google_service_account"]["type"],
                "project_id": st.secrets["google_service_account"]["project_id"],
                "private_key_id": st.secrets["google_service_account"]["private_key_id"],
                "private_key": st.secrets["google_service_account"]["private_key"],
                "client_email": st.secrets["google_service_account"]["client_email"],
                "client_id": st.secrets["google_service_account"]["client_id"],
                "auth_uri": st.secrets["google_service_account"]["auth_uri"],
                "token_uri": st.secrets["google_service_account"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["google_service_account"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["google_service_account"]["client_x509_cert_url"],
                "universe_domain": st.secrets["google_service_account"]["universe_domain"]
            }
            
            # Scopes necesarios
            SCOPES = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            
            # Crear credenciales
            self.credentials = Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            
            # Crear servicio de Drive
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            
            # IDs de carpetas desde secrets
            self.qr_folder_id = st.secrets["google_drive"]["qr_folder_id"]
            self.informes_folder_id = "1rPsYh4MABv7VD524ub60BB2HZcpCApQb"  # Carpeta de Informes técnicos
            
            print("✅ GoogleDriveManager inicializado correctamente")
            
        except Exception as e:
            st.error(f"❌ Error inicializando Google Drive: {str(e)}")
            self.drive_service = None

    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def obtener_base_datos_equipos(_self):
        """Obtiene la base de datos de equipos desde Google Drive"""
        try:
            # Buscar el archivo "Base de datos.xlsx" en Google Drive
            query = "name='Base de datos.xlsx' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            results = _self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if not files:
                st.error("❌ No se encontró el archivo 'Base de datos.xlsx' en Google Drive")
                return None
            
            file_id = files[0]['id']
            
            # Descargar el archivo
            request = _self.drive_service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            
            # Leer el Excel
            equipos_df = pd.read_excel(file_content, sheet_name=0)  # Primera hoja
            
            # Convertir a diccionario para fácil búsqueda
            equipos_dict = {}
            for _, row in equipos_df.iterrows():
                # Asumir que las columnas son: Codigo, Nombre, Marca, Modelo, Serie, Ubicacion, etc.
                codigo = str(row.get('Codigo', row.get('CODIGO', row.get('código', ''))))
                if codigo and codigo != 'nan':
                    equipos_dict[codigo] = {
                        'nombre': str(row.get('Nombre', row.get('NOMBRE', row.get('nombre', ''))),
                        'marca': str(row.get('Marca', row.get('MARCA', row.get('marca', ''))),
                        'modelo': str(row.get('Modelo', row.get('MODELO', row.get('modelo', ''))),
                        'serie': str(row.get('Serie', row.get('SERIE', row.get('serie', ''))),
                        'ubicacion': str(row.get('Ubicacion', row.get('UBICACION', row.get('ubicación', ''))),
                        'fecha_instalacion': str(row.get('Fecha_Instalacion', row.get('FECHA_INSTALACION', ''))),
                        'estado': str(row.get('Estado', row.get('ESTADO', row.get('estado', 'Operativo'))))
                    }
            
            print(f"✅ Base de datos cargada: {len(equipos_dict)} equipos")
            return equipos_dict
            
        except Exception as e:
            st.error(f"❌ Error cargando base de datos: {str(e)}")
            return None

    def guardar_informe_tecnico(self, datos_informe):
        """Guarda un informe técnico en Google Drive como Excel"""
        try:
            # Crear DataFrame con los datos del informe
            informe_data = {
                'INFORMACIÓN DEL EQUIPO': [
                    'Código:', datos_informe.get('codigo_equipo', ''),
                    'Nombre:', datos_informe.get('nombre_equipo', ''),
                    'Marca:', datos_informe.get('marca_equipo', ''),
                    'Modelo:', datos_informe.get('modelo_equipo', ''),
                    'Serie:', datos_informe.get('serie_equipo', ''),
                    'Ubicación:', datos_informe.get('ubicacion_equipo', ''),
                    '', '',
                    'INFORMACIÓN DEL MANTENIMIENTO', '',
                    'Fecha:', datos_informe.get('fecha_mantenimiento', ''),
                    'Hora inicio:', datos_informe.get('hora_inicio', ''),
                    'Hora fin:', datos_informe.get('hora_fin', ''),
                    'Tipo mantenimiento:', datos_informe.get('tipo_mantenimiento', ''),
                    'Personal asignado:', datos_informe.get('personal_asignado', ''),
                    'N° Orden trabajo:', datos_informe.get('orden_trabajo', ''),
                    '', '',
                    'TRABAJO REALIZADO', '',
                    datos_informe.get('trabajo_realizado', ''),
                    '', '',
                    'OBSERVACIONES Y HALLAZGOS', '',
                    datos_informe.get('observaciones', ''),
                    'Estado post-mantenimiento:', datos_informe.get('estado_equipo', ''),
                    '', '',
                    'REPUESTOS Y MATERIALES', '',
                    datos_informe.get('repuestos_utilizados', ''),
                    '', '',
                    'PRUEBAS REALIZADAS', '',
                    'Pruebas eléctricas:', datos_informe.get('pruebas_electricas', ''),
                    'Pruebas mecánicas:', datos_informe.get('pruebas_mecanicas', ''),
                    'Pruebas de seguridad:', datos_informe.get('pruebas_seguridad', ''),
                    '', '',
                    'MEDICIONES', '',
                    f"Voltaje: {datos_informe.get('voltaje_medido', '')} V",
                    f"Corriente: {datos_informe.get('corriente_medida', '')} A",
                    f"Presión: {datos_informe.get('presion_medida', '')} bar",
                    f"Temperatura: {datos_informe.get('temperatura_medida', '')} °C",
                    f"Flujo: {datos_informe.get('flujo_medido', '')} L/min",
                    f"Otras: {datos_informe.get('otras_mediciones', '')}",
                    '', '',
                    'RECOMENDACIONES', '',
                    datos_informe.get('recomendaciones', ''),
                    '', '',
                    'PRÓXIMO MANTENIMIENTO', '',
                    'Fecha programada:', datos_informe.get('proximo_mantenimiento', ''),
                    'Tipo:', datos_informe.get('tipo_proximo', ''),
                    '', '',
                    'VALIDACIÓN', '',
                    'Técnico:', datos_informe.get('tecnico_firma', ''),
                    'Supervisor:', datos_informe.get('supervisor_validacion', ''),
                    'Estado informe:', datos_informe.get('estado_informe', ''),
                    'Fecha creación:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            
            df_informe = pd.DataFrame(informe_data)
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                df_informe.to_excel(tmp_file.name, index=False, header=False)
                tmp_file_path = tmp_file.name
            
            # Nombre del archivo
            numero_informe = datos_informe.get('numero_informe', f"IT-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            file_name = f"{numero_informe}.xlsx"
            
            # Subir a Google Drive
            file_metadata = {
                'name': file_name,
                'parents': [self.informes_folder_id]
            }
            
            media = MediaFileUpload(
                tmp_file_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Limpiar archivo temporal
            os.unlink(tmp_file_path)
            
            print(f"✅ Informe guardado en Drive: {file_name} (ID: {file.get('id')})")
            return {
                'success': True,
                'file_id': file.get('id'),
                'file_name': file_name,
                'numero_informe': numero_informe
            }
            
        except Exception as e:
            st.error(f"❌ Error guardando informe: {str(e)}")
            return {'success': False, 'error': str(e)}

    def listar_informes_tecnicos(self):
        """Lista todos los informes técnicos de la carpeta"""
        try:
            query = f"'{self.informes_folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name, createdTime, modifiedTime, size)",
                orderBy="createdTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            informes_list = []
            for file in files:
                # Extraer información del nombre del archivo
                nombre = file['name'].replace('.xlsx', '')
                partes = nombre.split('-')
                
                informe_info = {
                    'id': file['id'],
                    'nombre_archivo': file['name'],
                    'numero_informe': nombre,
                    'fecha_creacion': file['createdTime'][:10],  # Solo la fecha
                    'fecha_modificacion': file['modifiedTime'][:10],
                    'tamaño': file.get('size', 0)
                }
                
                # Intentar extraer más información del nombre
                if len(partes) >= 2:
                    informe_info['codigo_equipo'] = partes[-1] if partes[-1].startswith('EQU') else ''
                
                informes_list.append(informe_info)
            
            return informes_list
            
        except Exception as e:
            st.error(f"❌ Error listando informes: {str(e)}")
            return []

    def buscar_equipo_por_codigo(self, codigo):
        """Busca un equipo específico por código en la base de datos"""
        equipos_db = self.obtener_base_datos_equipos()
        if equipos_db and codigo in equipos_db:
            equipo = equipos_db[codigo].copy()
            equipo['codigo'] = codigo
            return equipo
        return None

    def buscar_equipos_por_nombre(self, nombre_parcial):
        """Busca equipos que coincidan parcialmente con el nombre"""
        equipos_db = self.obtener_base_datos_equipos()
        if not equipos_db:
            return []
        
        resultados = []
        nombre_lower = nombre_parcial.lower()
        
        for codigo, equipo in equipos_db.items():
            if nombre_lower in equipo.get('nombre', '').lower():
                equipo_result = equipo.copy()
                equipo_result['codigo'] = codigo
                resultados.append(equipo_result)
        
        return resultados

    def obtener_roles_autorizados(self):
        """Obtiene los roles autorizados desde secrets"""
        try:
            roles_data = st.secrets["roles_autorizados"]["data"]
            roles_dict = json.loads(roles_data)
            return roles_dict
        except Exception as e:
            st.error(f"❌ Error cargando roles: {str(e)}")
            return {}

# Instancia global del manager
@st.cache_resource
def get_drive_manager():
    return GoogleDriveManager()