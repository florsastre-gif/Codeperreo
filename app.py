import os
import io
import re
import streamlit as st
import requests
import fal_client
from pydub import AudioSegment

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="CodePerreo", page_icon="🎶", layout="wide")
st.title("🎶 CodePerreo")
st.markdown("Conceptos tech → **letra reggaetón (20s)** + **beat instrumental (Lyria 2)**")

# --- 2. BARRA LATERAL (CREDENCIALES Y CONFIGURACIÓN) ---
with st.sidebar:
    st.header("🔑 Credenciales")
    gemini_api_key = st.text_input("Google API Key (Gemini)", type="password", help="Tu API Key de Google AI Studio")
    fal_key = st.text_input("FAL_KEY (Lyria 2)", type="password", help="API Key para usar fal.ai / Lyria 2")

    st.divider()
    st.header("🎛️ Ajustes")
    mood = st.selectbox("Mood", ["Energético", "Feliz", "Épico", "Tenso"], index=0)
    bpm = st.selectbox("BPM", ["95", "100", "105"], index=1)

    with st.expander("⚙️ Opciones avanzadas"):
        negative_prompt = st.text_input(
            "Negative prompt (audio)",
            value="vocals, singing, speech, low quality",
            help="Lyria 2 aquí genera instrumental. Esto ayuda a evitar voces."
        )
        seed_text = st.text_input("Seed (opcional)", value="")

# --- 3. INTERFAZ CREATIVA (EL INPUT DEL USUARIO) ---
st.header("1) ¿Qué concepto querés explicar?")
concepto = st.text_input("Concepto:", placeholder="Ej: ¿Qué es una API? ¿Qué es Docker? ¿Qué es RAG?")

col1, col2 = st.columns([1, 2])
with col1:
    generar = st.button("🎧 Generar CodePerreo (20s)", type="primary", use_container_width=True)
with col2:
    st.info("Tip: pedí ejemplos concretos (ej: “con una compra online”) para que la letra sea más visual.", icon="💡")

# --- Helpers ---
def gemini_generate_lyrics(api_key: str, concept: str, mood_value: str) -> str:
    """
    Letra ORIGINAL con vibe reggaetón clásico 2000s (sin imitar artistas específicos).
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    prompt = f"""
Escribe una letra ORIGINAL en español neutro para ~20 segundos con vibe reggaetón clásico 2000s:
- 10 a 12 líneas cortas.
- Estructura: Intro (2) + Hook (4, repetible) + Verso (4-6).
- Recurso: call & response, frases pegajosas, tono divertido/pro.
- Sin groserías. Sin contenido sexual explícito. Sin odio.
- No imites ni menciones artistas reales.
- Tema tech a explicar: {concept}
- Mood: {mood_value}

Devuelve SOLO la letra.
""".strip()

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 250},
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return "No pude extraer la letra. Revisa la respuesta de Gemini."

def build_lyria_prompt_en(concept: str, mood_value: str, bpm_value: str) -> str:
    """
    Prompt en inglés para el beat (mejor performance).
    """
    return (
        f"INSTRUMENTAL ONLY. Classic reggaeton dembow beat, early 2000s club vibe. "
        f"Tempo {bpm_value} BPM. Mood: {mood_value}. "
        f"Punchy kick, crisp snare, latin percussion, bouncy bass, simple catchy synth hook. "
        f"Theme inspired by: {concept}. High fidelity."
    )

def generate_audio_lyria2_fal(fal_api_key: str, prompt: str, negative: str, seed: int | None) -> bytes:
    os.environ["FAL_KEY"] = fal_api_key

    args = {"prompt": prompt, "negative_prompt": negative or ""}
    if seed is not None:
        args["seed"] = seed

    # Devuelve un URL a un WAV (según el modelo)
    result = fal_client.subscribe("fal-ai/lyria2", arguments=args)
    audio_url = result["audio"]["url"]

    resp = requests.get(audio_url, timeout=120)
    resp.raise_for_status()
    return resp.content  # wav bytes

def trim_wav(wav_bytes: bytes, seconds: int = 20) -> bytes:
    audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
    trimmed = audio[: seconds * 1000]
    out = io.BytesIO()
    trimmed.export(out, format="wav")
    return out.getvalue()

# --- 4. LÓGICA DE GENERACIÓN ---
if generar:
    if not concepto.strip():
        st.warning("⚠️ Escribe un concepto primero.")
        st.stop()
    if not gemini_api_key.strip():
        st.error("⚠️ Falta tu Google API Key (Gemini).")
        st.stop()
    if not fal_key.strip():
        st.error("⚠️ Falta tu FAL_KEY (para Lyria 2).")
        st.stop()

    seed = int(seed_text) if seed_text.strip().isdigit() else None

    with st.spinner("✍️ Generando letra (Gemini)..."):
        letra = gemini_generate_lyrics(gemini_api_key, concepto.strip(), mood)

    st.subheader("📝 Letra (20s aprox)")
    st.code(letra, language="text")

    prompt_audio = build_lyria_prompt_en(concepto.strip(), mood, bpm)

    with st.spinner("🥁 Generando beat (Lyria 2)..."):
        wav_30 = generate_audio_lyria2_fal(
            fal_api_key=fal_key,
            prompt=prompt_audio,
            negative=negative_prompt,
            seed=seed
        )
        wav_20 = trim_wav(wav_30, seconds=20)

    st.subheader("🎧 Beat (20s)")
    st.audio(wav_20, format="audio/wav")

    st.download_button(
        "⬇️ Descargar WAV (20s)",
        data=wav_20,
        file_name="codeperreo_20s.wav",
        mime="audio/wav",
        use_container_width=True,
    )

    with st.expander("Ver prompt de audio"):
        st.code(prompt_audio, language="text")
st.divider()
st.caption("Hecho con ❤️ para la comunidad tech.")
