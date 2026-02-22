import streamlit as st
import google.generativeai as genai

# CONFIGURACIÓN UI
st.set_page_config(page_title="CodePerreo", page_icon="🎵")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; font-family: monospace; }
    input, textarea, [data-baseweb="select"] > div {
        background-color: #111 !important;
        color: #FF4B4B !important;
        border: 1px solid #333 !important;
    }
    div.stButton > button {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 5px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA
def generar_letra(key, tema, estilo):
    try:
        genai.configure(api_key=key)
        # Usamos el modelo estable para evitar el error 404
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Escribe una letra de {estilo} en español sobre {tema}. Usa rimas urbanas y flow."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# INTERFAZ
st.title("🎵 CODEPERREO")
st.write("Tech con Dembow. Sin errores de GCP.")

with st.sidebar:
    api_key = st.text_input("Gemini API Key (Nivel 1):", type="password")

tema = st.text_input("Concepto Tech:", placeholder="Ej: Bases de datos")
estilo = st.selectbox("Estilo:", ["Reggaetón", "Trap", "RKT"])

if st.button("GENERAR FLOW"):
    if not api_key or not tema:
        st.error("Faltan datos.")
    else:
        with st.spinner("Cocinando..."):
            letra = generar_letra(api_key, tema, estilo)
            st.markdown("### 📜 Letra:")
            st.write(letra)

st.divider()
st.caption("Hecho con ❤️ para la comunidad tech.")
