import streamlit as st
import json

def gestion_usuarios_app(roles_dict):
    st.title("👥 Gestión de Usuarios y Roles")

    # Mostrar usuarios actuales (ocultando nivel para seguridad)
    st.subheader("Usuarios autorizados actuales:")
    for email, (rol, nivel) in roles_dict.items():
        st.write(f"- {email} : {rol} (nivel {nivel})")

    st.markdown("---")

    st.subheader("Agregar nuevo usuario")

    with st.form("agregar_usuario_form"):
        nuevo_email = st.text_input("Correo electrónico institucional")
        nuevo_rol = st.selectbox("Rol", ["Pasante 0", "Pasante 1", "Pasante 2", "Ingeniero Preprofesional", "Ingeniero Profesional", "Jefe del Departamento"])
        # Mapear rol a nivel
        niveles = {
            "Pasante 0": 0,
            "Pasante 1": 1,
            "Pasante 2": 2,
            "Ingeniero Preprofesional": 3,
            "Ingeniero Profesional": 4,
            "Jefe del Departamento": 5
        }
        nuevo_nivel = niveles[nuevo_rol]

        enviar = st.form_submit_button("Agregar usuario")

        if enviar:
            if nuevo_email in roles_dict:
                st.warning("El usuario ya existe.")
            else:
                roles_dict[nuevo_email] = [nuevo_rol, nuevo_nivel]
                st.success(f"Usuario {nuevo_email} agregado con rol {nuevo_rol}")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("Eliminar usuario")

    eliminar_email = st.selectbox("Selecciona usuario a eliminar", options=list(roles_dict.keys()))

    if st.button("Eliminar usuario seleccionado"):
        if eliminar_email:
            if eliminar_email == st.session_state.get("email"):
                st.error("No puedes eliminar tu propio usuario.")
            else:
                del roles_dict[eliminar_email]
                st.success(f"Usuario {eliminar_email} eliminado.")
                st.experimental_rerun()

    st.markdown("---")

    # Mostrar cómo exportar para actualizar el secrets.toml manualmente
    st.info("**Nota:** Los cambios se guardan solo en esta sesión y no se escriben automáticamente en `secrets.toml`.\nPara que los cambios sean permanentes, actualiza el archivo `secrets.toml` con el siguiente contenido JSON:")

    json_roles = json.dumps(roles_dict, indent=2)
    st.code(f'{{\n"roles_autorizados": {{\n  "data": """{json_roles}"""\n}}\n}}', language="toml")
