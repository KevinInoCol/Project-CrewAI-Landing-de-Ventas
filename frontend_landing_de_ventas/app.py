# app.py - Frontend con Formulario de Captura de Leads

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Datapath - Programas de IA y Automatización",
    page_icon="🤖",
    layout="centered"
)

# --- URL del Backend ---
# Usamos una variable de entorno para producción, con un valor por defecto para pruebas locales.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8005/process-lead")

# --- Título y Descripción ---
#st.image("https://i.imgur.com/u42K6yI.png", width=200) # Reemplaza con la URL de tu logo
st.title("Inscríbete en Nuestros Programas de IA y Automatización")
st.markdown("Completa el siguiente formulario para recibir más información y el brochure del programa de tu interés. ¡Un asesor se comunicará contigo a la brevedad!")

# --- Formulario de Captura de Leads ---
# Usamos st.form para agrupar los campos y tener un único botón de envío.
with st.form("lead_form", clear_on_submit=True):
    st.subheader("Tus Datos")
    
    # Dividimos en columnas para un mejor diseño
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre", placeholder="Ej: Juan")
    with col2:
        apellido = st.text_input("Apellido", placeholder="Ej: Pérez")

    correo = st.text_input("Correo Electrónico", placeholder="juan.perez@email.com")
    
    col3, col4 = st.columns([1, 2]) # El código de país es más corto
    with col3:
        codigo_pais = st.selectbox("Código", ("+51", "+52", "+54", "+57", "+1", "+34"))
    with col4:
        celular = st.text_input("Número de Celular", placeholder="999 888 777")

    st.subheader("Programas de Interés")
    
    # Opciones de programas
    programas_disponibles = [
        "AI Engineer",
        "n8n Básico",
        "n8n Avanzado",
        "Make Básico",
        "Make Avanzado"
    ]
    
    # Usamos multiselect para que puedan elegir varios
    programas_interes = st.multiselect(
        "Selecciona uno o más programas:",
        programas_disponibles,
        placeholder="Elige una opción"
    )

    # El botón de envío del formulario
    submit_button = st.form_submit_button(label="🚀 ¡Enviar y Recibir Información!")

# --- Lógica de Envío del Formulario ---
if submit_button:
    # Validación simple
    if not all([nombre, apellido, correo, celular, programas_interes]):
        st.error("Por favor, completa todos los campos del formulario.")
    else:
        # Construir el número de celular completo
        numero_completo = f"{codigo_pais}{celular}"
        
        # Preparar los datos para enviar a la API
        payload = {
            "nombre": nombre,
            "apellido": apellido,
            "pais": codigo_pais, # Asumimos que el código de país es suficiente
            "correo_electronico": correo,
            "numero_celular": numero_completo,
            "programas_interes": programas_interes
        }

        # Lógica de envío y feedback al usuario
        with st.spinner("Procesando tu solicitud... ¡Ya casi está!"):
            try:
                response = requests.post(BACKEND_URL, json=payload)
                response.raise_for_status() # Lanza un error si la respuesta es 4xx o 5xx

                # Si todo sale bien
                st.success("¡Gracias! Hemos recibido tu información. Revisa tu correo electrónico (y la carpeta de spam) para ver el brochure. Un asesor te contactará pronto.")
                st.balloons()

            except requests.exceptions.RequestException as e:
                st.error(f"Hubo un problema al enviar tu solicitud. Por favor, inténtalo de nuevo más tarde. Error: {e}")