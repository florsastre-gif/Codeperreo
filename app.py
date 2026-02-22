import streamlit as st
import requests
import base64
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="CodePerreo", page_icon="🎵")
st.title("🎵 CodePerreo")
st.markdown("Tech concepts. Dembow energy. 100 BPM learning")

# --- 2. BARRA LATERAL (CREDENCIALES Y CONFIGURACIÓN) ---
with st.sidebar:
    st.header("🔑 Configuración GCP (Lyria 2)")
    project_id = st.text_input("GCP Project ID:", placeholder="tu-proyecto-demos")
    access_token = st.text_input("GCP Access Token:", type="password", help="Token Bearer (OAuth2)")

    st.markdown("---")
    st.header("🧠 Configuración Gemini (letra)")
    gemini_api_key = st.text_input("Gemini API Key:", type="password", help="Key de Google AI Studio (Gemini API)")


# --- 3. INTERFAZ CREATIVA (EL INPUT DEL USUARIO) ---
st.header("1) Concepto tech")
concepto = st.text_input(
    "¿Qué queres aprender hoy? te respondemos con flow",
    placeholder="Ej: ¿Qué es una API? ¿Qué es Docker? ¿Qué es RAG?",
)

col1, col2, col3 = st.columns(3)
with col1:
    estilo = st.selectbox(
        "Género / Estilo:",
        ["Reggaetón clásico 2000s (instrumental)", "Reggaetón pop moderno (instrumental)", "Dembow minimal (instrumental)"],
        index=0,
    )
with col2:
    estado_animo = st.selectbox(
        "Estado de Ánimo (Mood):",
        ["Energético", "Feliz", "Épico", "Tenso"],
        index=0,
    )
with col3:
    bpm = st.selectbox("BPM aprox:", ["95", "100", "105"], index=1)

with st.expander("⚙️ Opciones Avanzadas"):
    negative_prompt = st.text_input(
        "¿Qué quieres EVITAR en la base?",
        placeholder="vocals, singing, speech, trap hats, harsh synths...",
        value="vocals, singing, speech"
    )
    region = st.selectbox("Región Vertex:", ["us-central1", "europe-west4"], index=0)
    seed_text = st.text_input("Seed (opcional)", value="", help="Número para repetir resultados (opcional).")

# --- Helpers ---
def gemini_generate_lyrics(api_key: str, concept: str, mood: str) -> str:
    """
    Genera letra corta tipo reggaetón clásico 2000s (sin imitar artistas específicos).
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    prompt = f"""
Escribe una letra ORIGINAL en español neutro, para un clip de ~20 segundos, con vibe de reggaetón clásico 2000s:
- 10 a 12 líneas cortas.
- Estructura: (Intro 2 líneas) + (Hook 4 líneas, repetible) + (Verso 4-6 líneas).
- Recurso: call & response (líneas que se contestan), y frases cortas pegajosas.
- Sin groserías, sin contenido sexual explícito, sin odio.
- No imites ni menciones artistas reales.

Tema tech: {concept}
Mood: {mood}

Devuelve SOLO la letra (sin títulos, sin explicaciones).
""".strip()

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 250
        }
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    # Extraer texto de forma robusta
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return "No pude extraer la letra. Revisa la respuesta de Gemini."

def build_lyria_prompt(concept: str, style: str, mood: str, bpm_value: str) -> str:
    # Prompt en inglés (funciona mejor en Lyria)
    # Importante: Lyria genera instrumental (lo reforzamos).
    base_style = {
        "Reggaetón clásico 2000s (instrumental)": "classic reggaeton dembow, early 2000s club vibe, punchy kick, snappy snare, latin percussion",
        "Reggaetón pop moderno (instrumental)": "modern reggaeton, polished pop club vibe, tight dembow, clean synths, bouncy bass",
        "Dembow minimal (instrumental)": "minimal dembow beat, sparse percussion, deep sub bass, simple catchy groove",
    }[style]

    return (
        f"INSTRUMENTAL ONLY. {base_style}. "
        f"Tempo {bpm_value} BPM. Mood: {mood}. "
        f"Theme inspired by: {concept}. "
        f"High fidelity, clear low end, danceable groove, 48kHz wav."
    )

def lyria_generate_audio(project_id: str, token: str, location: str, prompt_final: str, negative: str, seed: int | None):
    # Endpoint oficial del modelo Lyria 2 en Vertex: lyria-002:predict
    api_endpoint = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}"
        f"/publishers/google/models/lyria-002:predict"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    instance = {
        "prompt": prompt_final,
        "negative_prompt": negative or ""
    }
    if seed is not None:
        instance["seed"] = seed

    payload = {"instances": [instance]}

    response = requests.post(api_endpoint, headers=headers, json=payload, timeout=120)
    return response

# --- 4. LÓGICA DE GENERACIÓN ---
if st.button("🎹 Generar (letra + base)", type="primary"):
    if not project_id or not access_token:
        st.error("⚠️ Faltan credenciales GCP en la barra lateral.")
        st.stop()
    if not gemini_api_key:
        st.error("⚠️ Falta Gemini API Key (para generar la letra).")
        st.stop()
    if not concepto:
        st.warning("⚠️ Por favor, escribe un concepto primero.")
        st.stop()

    # Seed
    seed = int(seed_text) if seed_text.strip().isdigit() else None

    # A) Generar letra con Gemini
    with st.spinner("✍️ Generando letra (20s) con Gemini..."):
        try:
            letra = gemini_generate_lyrics(gemini_api_key, concepto, estado_animo)
        except Exception as e:
            st.error(f"Error generando letra con Gemini: {e}")
            st.stop()

    # B) Construcción del prompt final para Lyria
    prompt_final = build_lyria_prompt(concepto, estilo, estado_animo, bpm)
    st.markdown("### 📝 Letra (20s aprox)")
    st.code(letra, language="text")

    st.markdown("### 🥁 Base instrumental (Lyria 2)")
    with st.spinner(f"🎧 Generando audio en Vertex: '{prompt_final}'..."):
        try:
            response = lyria_generate_audio(
                project_id=project_id,
                token=access_token,
                location=region,
                prompt_final=prompt_final,
                negative=negative_prompt,
                seed=seed
            )

            if response.status_code == 200:
                datos = response.json()

                # Respuesta oficial: predictions -> [{ audioContent: "...", mimeType: "audio/wav" }, ...]
                predictions = datos.get("predictions", [])
                if not predictions:
                    st.error("La API respondió 200 pero no trajo 'predictions'.")
                    st.json(datos)
                    st.stop()

                audio_b64 = predictions[0].get("audioContent", "")
                mime_type = predictions[0].get("mimeType", "audio/wav")

                if not audio_b64:
                    st.error("No vino 'audioContent' en la predicción.")
                    st.json(datos)
                    st.stop()

                audio_bytes = base64.b64decode(audio_b64)

                st.success("✅ ¡Listo! (Beat instrumental generado)")
                st.audio(audio_bytes, format=mime_type)

                st.download_button(
                    "⬇️ Descargar WAV",
                    data=audio_bytes,
                    file_name="lyria_reggaeton.wav",
                    mime=mime_type
                )

            else:
                st.error(f"Error en la API: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"Ocurrió un error en la conexión: {e}")

    with st.expander("Ver prompts usados"):
        st.markdown("**Prompt Lyria (EN):**")
        st.code(prompt_final, language="text")
        st.markdown("**Negative prompt (EN):**")
        st.code(negative_prompt, language="text")
