import streamlit as st
import cv2
from pyzbar import pyzbar
import numpy as np
from PIL import Image

def decodificar_qr_imagen(imagen_array):
    """Decodificar QR de una imagen"""
    try:
        # Convertir a escala de grises si es necesario
        if len(imagen_array.shape) == 3:
            gray = cv2.cvtColor(imagen_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = imagen_array
        
        # Detectar códigos QR
        codigos = pyzbar.decode(gray)
        
        resultados = []
        for codigo in codigos:
            # Decodificar el texto
            texto = codigo.data.decode('utf-8')
            resultados.append(texto)
        
        return resultados
    except Exception as e:
        st.error(f"Error decodificando QR: {e}")
        return []

def mostrar_escaner_qr():
    """Función principal del escáner QR"""
    st.title("📱 Escáner de Códigos QR")
    st.write("Escanea códigos QR subiendo una imagen o usando la cámara")
    
    # Tabs para diferentes métodos
    tab1, tab2 = st.tabs(["📷 Cámara", "📁 Subir Imagen"])
    
    with tab1:
        st.subheader("📷 Escáner con Cámara")
        
        # Usar camera_input de Streamlit (más simple y compatible)
        foto_camara = st.camera_input("Toma una foto del código QR")
        
        if foto_camara is not None:
            # Procesar imagen de la cámara
            imagen = Image.open(foto_camara)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(imagen, caption="Foto tomada", use_column_width=True)
            
            with col2:
                st.write("**Procesando imagen...**")
                
                # Convertir imagen para procesamiento
                imagen_array = np.array(imagen)
                
                # Decodificar QR
                resultados = decodificar_qr_imagen(imagen_array)
                
                if resultados:
                    st.success(f"✅ Se encontraron {len(resultados)} código(s) QR")
                    
                    for i, codigo in enumerate(resultados):
                        st.markdown(f"### QR {i+1}:")
                        st.code(codigo)
                        
                        # Mostrar el código de forma destacada
                        st.markdown(f"**Código detectado:** `{codigo}`")
                        
                        # Botón para copiar
                        if st.button(f"📋 Copiar código {i+1}", key=f"copy_{i}"):
                            st.success("Código copiado!")
                        
                else:
                    st.error("❌ No se detectaron códigos QR en la imagen")
                    st.info("Toma otra foto asegurándote de que el código QR esté claro y centrado")
        
        # Instrucciones para la cámara
        st.markdown("""
        **Instrucciones:**
        1. Haz clic en "Take Photo" para activar la cámara
        2. Apunta la cámara hacia el código QR
        3. Asegúrate de que el código esté centrado y enfocado
        4. Toma la foto haciendo clic en el botón de captura
        """)
    
    with tab2:
        st.subheader("📁 Subir Imagen con QR")
        
        # Subir imagen
        archivo_imagen = st.file_uploader(
            "Selecciona una imagen que contenga un código QR",
            type=['png', 'jpg', 'jpeg'],
            help="Formatos soportados: PNG, JPG, JPEG"
        )
        
        if archivo_imagen is not None:
            # Mostrar imagen subida
            imagen = Image.open(archivo_imagen)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(imagen, caption="Imagen subida", use_column_width=True)
            
            with col2:
                st.write("**Procesando imagen...**")
                
                # Convertir imagen para procesamiento
                imagen_array = np.array(imagen)
                
                # Decodificar QR
                resultados = decodificar_qr_imagen(imagen_array)
                
                if resultados:
                    st.success(f"✅ Se encontraron {len(resultados)} código(s) QR")
                    
                    for i, codigo in enumerate(resultados):
                        st.markdown(f"### QR {i+1}:")
                        st.code(codigo)
                        
                        # Mostrar el código de forma destacada
                        st.markdown(f"**Código detectado:** `{codigo}`")
                        
                        # Botón para copiar
                        if st.button(f"📋 Copiar código {i+1}", key=f"upload_copy_{i}"):
                            st.success("Código copiado!")
                        
                else:
                    st.error("❌ No se detectaron códigos QR en la imagen")
                    st.info("Asegúrate de que la imagen contenga un código QR claro y legible")
    
    # Información adicional
    with st.expander("ℹ️ Consejos para mejores resultados"):
        st.markdown("""
        **Para obtener mejores resultados:**
        - Mantén el código QR bien iluminado
        - Evita reflejos y sombras
        - Asegúrate de que el código esté completo en la imagen
        - Mantén una distancia adecuada (el código debe ser legible)
        - Usa imágenes de buena calidad
        
        **Formatos soportados:**
        - PNG
        - JPG / JPEG
        - Funciona con códigos QR estándar
        """)

if __name__ == "__main__":
    mostrar_escaner_qr()