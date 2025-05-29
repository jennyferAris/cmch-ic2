import streamlit as st
from PIL import Image

def mostrar_escaner_qr():
    st.title("📱 Escáner de Códigos QR")
    st.write("Captura una foto del código QR")
    
    # Solo cámara simple - sin procesamiento automático
    foto_camara = st.camera_input("Toma una foto del código QR")
    
    if foto_camara is not None:
        imagen = Image.open(foto_camara)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(imagen, caption="Foto tomada", use_column_width=True)
        
        with col2:
            st.success("📱 Foto capturada exitosamente")
            
            # Input manual del código
            codigo_qr = st.text_input(
                "Introduce el código del QR:", 
                placeholder="EQU-0000001",
                help="Lee el código del QR en la imagen"
            )
            
            if codigo_qr:
                st.success(f"✅ Código: **{codigo_qr}**")
                
                # Acciones
                if st.button("📝 Reportar Evento"):
                    st.info("🚧 Módulo en desarrollo")

if __name__ == "__main__":
    mostrar_escaner_qr()