import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import json
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL Y DICCIONARIO ---
st.set_page_config(page_title="Rappi OKR Generator", layout="wide")

languages = {
    "Español 🇲🇽": {
        "title": "OKR Performance Builder",
        "subtitle": "Define y registra tus objetivos estratégicos.",
        "draft_label": "Tu Borrador:",
        "role_label": "Nivel del Rol:",
        "btn_gen": "REFINAR CON IA",
        "btn_send": "ENVIAR AL REPOSITORIO",
        "success": "¡Registrado con éxito!",
        "placeholder": "Ej: Mejorar la conversión de Turbo MX..."
    },
    "Português 🇧🇷": {
        "title": "Gerador de OKRs Rappi",
        "subtitle": "Defina e registre seus objetivos estratégicos.",
        "draft_label": "Seu Rascunho:",
        "role_label": "Nível do Cargo:",
        "btn_gen": "REFINAR COM IA",
        "btn_send": "ENVIAR AO REPOSITÓRIO",
        "success": "Registrado com sucesso!",
        "placeholder": "Ex: Melhorar a conversão do Turbo MX..."
    },
    "English 🇺🇸": {
        "title": "OKR Performance Builder",
        "subtitle": "Define and register your strategic goals.",
        "draft_label": "Your Draft:",
        "role_label": "Job Level:",
        "btn_gen": "REFINE WITH AI",
        "btn_send": "SEND TO REPOSITORY",
        "success": "Successfully registered!",
        "placeholder": "Ex: Improve Turbo MX conversion..."
    }
}

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; }
    .main-title { color: #FF441F; font-size: 42px; font-weight: 800; margin-bottom: 5px; }
    .card { background-color: #FFFFFF; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #E0E0E0; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; font-weight: bold; border: none; height: 3.5em; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)
    selected_lang = st.selectbox("🌐 Idioma / Language", list(languages.keys()))
    t = languages[selected_lang]
    st.markdown("---")
    st.markdown(f"**Ruta Udemy Business**\n[Acceder a Rappi Udemy](https://rappi.udemy.com/)")
    st.caption("v3.4 | Automated Repository Mode")

# --- 3. CUERPO PRINCIPAL ---
st.markdown(f'<h1 class="main-title">{t["title"]}</h1>', unsafe_allow_html=True)
st.write(t["subtitle"])

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    role = st.selectbox(t["role_label"], ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    draft = st.text_area(t["draft_label"], height=200, placeholder=t["placeholder"])
    
    if st.button(t["btn_gen"]):
        if not draft:
            st.warning("Escribe algo para procesar.")
        else:
            with st.spinner('Gemini is thinking...'):
                try:
                    # Configuración robusta para evitar error 404
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Context: Rappi Performance. Role: {role}. Language: {selected_lang}.
                    Task: Refine this draft: '{draft}' into 3 SMART OKRs.
                    Output: Return ONLY a JSON list with: Objetivo, KR, Metrica, Meta, Deadline.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Extracción de JSON
                    match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    if match:
                        st.session_state.okrs = json.loads(match.group())
                        st.session_state.role = role
                        st.success("✅ Generado.")
                    else:
                        st.error("Error de formato en la respuesta.")
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_out:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if 'okrs' in st.session_state:
        st.write("### Review / Revisión")
        st.table(st.session_state.okrs)
        
        if st.button(t["btn_send"]):
            with st.spinner('Sending to Repository...'):
                try:
                    # Conector a Sheets
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    url = "https://docs.google.com/spreadsheets/d/1XMkYvkD1XIme_B5u0xZd160XFBLahCh3UgybVHF1b6Y/edit"
                    
                    # Preparar nuevos datos
                    df_new = pd.DataFrame(st.session_state.okrs)
                    df_new['Role'] = st.session_state.role
                    df_new['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    df_new['Language'] = selected_lang
                    
                    # Leer repositorio actual
                    existing_data = conn.read(spreadsheet=url)
                    
                    # Concatenar (Efecto Formulario)
                    updated_data = pd.concat([existing_data, df_new], ignore_index=True)
                    
                    # Guardar
                    conn.update(spreadsheet=url, data=updated_data)
                    
                    st.balloons()
                    st.success(t["success"])
                    # Limpiar después de enviar
                    del st.session_state.okrs
                except Exception as e:
                    st.error(f"Error saving to Sheets: {e}")
    else:
        st.info("Esperando generación de IA...")
    st.markdown('</div>', unsafe_allow_html=True)
