import streamlit as st
from pyzbar import pyzbar
import numpy as np
from PIL import Image

def decodificar_qr_imagen(imagen_pil):
    """Decodificar QR de una imagen usando solo PIL y pyzbar"""
    try:
        # Convertir PIL a array numpy
        imagen_array = np.array(imagen_pil)
        
        # Detectar códigos QR directamente
        codigos = pyzbar.decode(imagen_array)
        
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
        
        # Usar camera_input de Streamlit
        foto_camara = st.camera_input("Toma una foto del código QR")
        
        if foto_camara is not None:
            # Procesar imagen de la cámara
            imagen = Image.open(foto_camara)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(imagen, caption="Foto tomada", use_column_width=True)
            
            with col2:
                st.write("**Procesando imagen...**")
                
                # Decodificar QR
                with st.spinner("Escaneando código QR..."):
                    resultados = decodificar_qr_imagen(imagen)
                
                if resultados:
                    st.success(f"✅ Se encontraron {len(resultados)} código(s) QR")
                    
                    for i, codigo in enumerate(resultados):
                        st.markdown(f"### 📱 QR {i+1}:")
                        
                        # Mostrar el código en una caja destacada
                        st.markdown(f"""
                        <div style="
                            background-color: #f0f2f6; 
                            padding: 15px; 
                            border-radius: 10px; 
                            border-left: 4px solid #DC143C;
                            margin: 10px 0;
                        ">
                            <strong>Código detectado:</strong><br>
                            <code style="font-size: 16px;">{codigo}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # También mostrar en formato código
                        st.code(codigo)
                        
                else:
                    st.error("❌ No se detectaron códigos QR en la imagen")
                    st.info("💡 Toma otra foto asegurándote de que el código QR esté claro y centrado")
        
        # Instrucciones para la cámara
        st.markdown("""
        ### 📋 Instrucciones:
        1. **Haz clic en "Take Photo"** para activar la cámara
        2. **Apunta la cámara** hacia el código QR  
        3. **Asegúrate** de que el código esté centrado y enfocado
        4. **Toma la foto** haciendo clic en el botón de captura
        5. **Espera** a que se procese automáticamente
        """)
    
    with tab2:
        st.subheader("📁 Subir Imagen con QR")
        
        # Subir imagen
        archivo_imagen = st.file_uploader(
            "Selecciona una imagen que contenga un código QR",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Formatos soportados: PNG, JPG, JPEG, BMP, TIFF"
        )
        
        if archivo_imagen is not None:
            # Mostrar imagen subida
            imagen = Image.open(archivo_imagen)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(imagen, caption="Imagen subida", use_column_width=True)
            
            with col2:
                st.write("**Procesando imagen...**")
                
                # Decodificar QR
                with st.spinner("Escaneando código QR..."):
                    resultados = decodificar_qr_imagen(imagen)
                
                if resultados:
                    st.success(f"✅ Se encontraron {len(resultados)} código(s) QR")
                    
                    for i, codigo in enumerate(resultados):
                        st.markdown(f"### 📱 QR {i+1}:")
                        
                        # Mostrar el código en una caja destacada
                        st.markdown(f"""
                        <div style="
                            background-color: #f0f2f6; 
                            padding: 15px; 
                            border-radius: 10px; 
                            border-left: 4px solid #DC143C;
                            margin: 10px 0;
                        ">
                            <strong>Código detectado:</strong><br>
                            <code style="font-size: 16px;">{codigo}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # También mostrar en formato código
                        st.code(codigo)
                        
                else:
                    st.error("❌ No se detectaron códigos QR en la imagen")
                    st.info("💡 Asegúrate de que la imagen contenga un código QR claro y legible")
    
    # Información adicional
    with st.expander("💡 Consejos para mejores resultados"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📷 Para la cámara:**
            - Mantén el código QR bien iluminado
            - Evita reflejos y sombras  
            - Centra el código en la imagen
            - Mantén distancia adecuada (15-30cm)
            """)
        
        with col2:
            st.markdown("""
            **📁 Para imágenes:**
            - Usa imágenes de buena calidad
            - Asegúrate de que el QR esté completo
            - Evita imágenes borrosas
            - Formatos: PNG, JPG, JPEG, BMP, TIFF
            """)
    
    # Estadísticas (opcional)
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📱 QRs Escaneados Hoy", "0", help="Contador en desarrollo")
    with col2:
        st.metric("✅ Éxito de Escaneo", "100%", help="Tasa de éxito")
    with col3:
        st.metric("⚡ Tiempo Promedio", "< 1s", help="Velocidad de procesamiento")

if __name__ == "__main__":
    mostrar_escaner_qr()