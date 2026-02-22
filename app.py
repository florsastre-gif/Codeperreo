import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="CodePerreo", page_icon="🎵", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div.stButton > button {
        background-color: #FF4B4B !important;
        color: white !important;
        width: 100%;
        font-weight: bold;
        border-radius: 10px;
    }
    .lyrics-box {
        background-color: #1A1C24;
        border-left: 5px solid #FF4B4B;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE GENERACIÓN ---
def generar_perreo(key, concepto, genero, mood, bpm):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.5-flash') # Modelo estable
        
        prompt = f"""
        Escribe una letra de canción urbana sobre este concepto tech: {concepto}.
        Género: {genero}
        Estado de ánimo: {mood}
        BPM aproximado: {bpm}
        
        Instrucciones:
        - Usa rimas con "flow" y lenguaje urbano.
        - Estructura: Intro, Coro, Verso, Coro, Outro.
        - Idioma: Español.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en la conexión: {str(e)}"

# --- INTERFAZ ---
st.title("🎵 CodePerreo")
st.write("Tech concepts. Dembow energy. 100 BPM learning.")

with st.sidebar:
    st.header("🧠 Configuración Gemini")
    api_key = st.text_input("Gemini API Key:", type="password")
    st.info("Usa tu clave de Nivel 1. No requiere GCP.")

# Formulario de entrada
st.subheader("1) Concepto tech")
concepto = st.text_input("¿Qué quieres aprender hoy?", placeholder="ej: Docker, APIs, Python...")

col1, col2, col3 = st.columns(3)
with col1:
    genero = st.selectbox("Género / Estilo:", ["Reggaetón clásico", "Trap", "Dembo", "RKT"])
with col2:
    mood = st.selectbox("Estado de Ánimo:", ["Feliz", "Agresivo", "Melancólico", "Party"])
with col3:
    bpm = st.selectbox("BPM aprox:", ["90", "100", "115", "128"])

if st.button("🎹 Generar Letra con Flow"):
    if not api_key:
        st.error("Falta la API Key en la barra lateral.")
    elif not concepto:
        st.warning("Escribe un concepto para empezar.")
    else:
        with st.spinner("Cocinando el beat mental..."):
            resultado = generar_perreo(api_key, concepto, genero, mood, bpm)
            st.markdown("### 📜 Tu Letra:")
            st.markdown(f'<div class="lyrics-box">{resultado}</div>', unsafe_allow_html=True)

st.divider()
st.caption("Hecho con ❤️ para la comunidad tech.")
