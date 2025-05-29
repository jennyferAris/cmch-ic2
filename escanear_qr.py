import streamlit as st
from PIL import Image

def mostrar_escaner_qr():
    """Función principal del escáner QR - Versión simple"""
    st.title("📱 Escáner de Códigos QR")
    st.write("Toma una foto del código QR para verlo y copiarlo")
    
    # Tabs para diferentes métodos
    tab1, tab2 = st.tabs(["📷 Cámara", "📁 Subir Imagen"])
    
    with tab1:
        st.subheader("📷 Escáner con Cámara")
        
        # Usar camera_input de Streamlit
        foto_camara = st.camera_input("Toma una foto del código QR")
        
        if foto_camara is not None:
            imagen = Image.open(foto_camara)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(imagen, caption="Foto tomada", use_column_width=True)
            
            with col2:
                st.info("📱 Foto capturada exitosamente")
                st.write("**Instrucciones:**")
                st.write("1. Observa la imagen y lee el código QR manualmente")
                st.write("2. Introduce el código en el campo de abajo")
                
                # Campo para introducir el código manualmente
                codigo_manual = st.text_input(
                    "Código del QR:", 
                    placeholder="EQU-0000001",
                    help="Introduce el código que ves en el QR"
                )
                
                if codigo_manual:
                    st.success("✅ Código introducido")
                    st.code(codigo_manual)
    
    with tab2:
        st.subheader("📁 Subir Imagen con QR")
        
        archivo_imagen = st.file_uploader(
            "Selecciona una imagen que contenga un código QR",
            type=['png', 'jpg', 'jpeg']
        )
        
        if archivo_imagen is not None:
            imagen = Image.open(archivo_imagen)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(imagen, caption="Imagen subida", use_column_width=True)
            
            with col2:
                st.info("📁 Imagen subida exitosamente")
                st.write("**Instrucciones:**")
                st.write("1. Observa la imagen y lee el código QR")
                st.write("2. Introduce el código en el campo de abajo")
                
                # Campo para introducir el código manualmente
                codigo_manual = st.text_input(
                    "Código del QR:", 
                    placeholder="EQU-0000001",
                    help="Introduce el código que ves en el QR",
                    key="upload_manual"
                )
                
                if codigo_manual:
                    st.success("✅ Código introducido")
                    st.code(codigo_manual)

if __name__ == "__main__":
    mostrar_escaner_qr()