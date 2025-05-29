import streamlit as st
import cv2
from pyzbar import pyzbar
import numpy as np
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

class QRCodeScanner(VideoTransformerBase):
    """Clase para procesar video y detectar códigos QR"""
    
    def __init__(self):
        self.qr_data = None
        self.qr_detected = False
    
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Detectar códigos QR
        codigos = pyzbar.decode(img)
        
        for codigo in codigos:
            # Extraer datos del QR
            qr_text = codigo.data.decode('utf-8')
            self.qr_data = qr_text
            self.qr_detected = True
            
            # Dibujar rectángulo alrededor del QR
            puntos = codigo.polygon
            if len(puntos) == 4:
                pts = np.array([[p.x, p.y] for p in puntos], np.int32)
                cv2.polylines(img, [pts], True, (0, 255, 0), 3)
                
                # Mostrar el texto del QR
                cv2.putText(img, qr_text, (puntos[0].x, puntos[0].y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return img

def decodificar_qr_imagen(imagen_array):
    """Decodificar QR de una imagen estática"""
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
    st.write("Escanea códigos QR usando la cámara o subiendo una imagen")
    
    # Tabs para diferentes métodos
    tab1, tab2 = st.tabs(["📷 Cámara en Vivo", "📁 Subir Imagen"])
    
    with tab1:
        st.subheader("📷 Escáner con Cámara")
        st.write("Apunta la cámara hacia el código QR para escanearlo")
        
        # Configuración WebRTC
        rtc_config = RTCConfiguration({
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        })
        
        # Crear el scanner
        scanner = QRCodeScanner()
        
        # Stream de video
        ctx = webrtc_streamer(
            key="qr-scanner",
            video_transformer_factory=lambda: scanner,
            rtc_configuration=rtc_config,
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 640},
                    "height": {"ideal": 480}
                },
                "audio": False
            }
        )
        
        # Mostrar resultado cuando se detecta QR
        if ctx.video_transformer:
            if ctx.video_transformer.qr_detected and ctx.video_transformer.qr_data:
                st.success("✅ ¡Código QR detectado!")
                st.markdown("### Código escaneado:")
                st.code(ctx.video_transformer.qr_data)
                
                # Botón para copiar al portapapeles
                if st.button("📋 Copiar Código"):
                    st.write("Código copiado al portapapeles")
                
                # Reiniciar para escanear otro
                if st.button("🔄 Escanear Otro"):
                    ctx.video_transformer.qr_detected = False
                    ctx.video_transformer.qr_data = None
                    st.rerun()
        
        # Instrucciones
        st.markdown("""
        **Instrucciones:**
        1. Haz clic en "START" para activar la cámara
        2. Apunta la cámara hacia el código QR
        3. Mantén el código centrado y enfocado
        4. El código se detectará automáticamente
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
                        
                else:
                    st.error("❌ No se detectaron códigos QR en la imagen")
                    st.info("Asegúrate de que la imagen contenga un código QR claro y legible")
    
    # Información adicional
    with st.expander("ℹ️ Información y Solución de Problemas"):
        st.markdown("""
        **Si la cámara no funciona:**
        - Asegúrate de dar permisos de cámara al navegador
        - Verifica que no haya otras aplicaciones usando la cámara
        - Usa HTTPS (no HTTP) para acceder a la aplicación
        - Algunos navegadores requieren configuración adicional
        
        **Para mejores resultados:**
        - Mantén el código QR bien iluminado
        - Evita reflejos y sombras
        - Mantén una distancia adecuada (15-30 cm)
        - Mantén la cámara estable
        """)

if __name__ == "__main__":
    mostrar_escaner_qr()