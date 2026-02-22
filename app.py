import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

st.set_page_config(page_title="CODEPERREO", page_icon="🎵")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    div.stButton > button { background-color: #FF4B4B !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def generar_flow(key, tema, estilo):
    try:
        genai.configure(api_key=key)
        # Forzamos el uso del modelo sin v1beta para evitar el 404
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Escribe una letra corta de {estilo} en español sobre {tema}. Solo la letra, con mucho flow."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

st.title("🎵 CODEPERREO v2")

with st.sidebar:
    api_key = st.text_input("Gemini API Key:", type="password")

tema = st.text_input("Concepto Tech:", placeholder="ej: Que es RAG")
estilo = st.selectbox("Estilo:", ["Reggaetón", "Trap", "RKT"])

if st.button("GENERAR FLOW Y AUDIO"):
    if not api_key or not tema:
        st.error("Faltan datos en la configuración.")
    else:
        with st.spinner("Cocinando el ritmo..."):
            letra = generar_flow(api_key, tema, estilo)
            
            if "Error" not in letra:
                st.markdown("### 📜 Letra:")
                st.write(letra)
                
                # GENERACIÓN DE AUDIO (La solución al "donde está el audio")
                tts = gTTS(text=letra, lang='es', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                
                st.markdown("### 🔊 Escuchar:")
                st.audio(audio_fp, format='audio/mp3')
            else:
                st.error(letra)
