import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import json
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Rappi OKR Builder | Multilingual", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; }
    .main-title { color: #1a1a1a; font-size: 42px; font-weight: 800; margin-bottom: 0px; }
    .card { background-color: #FFFFFF; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #E0E0E0; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; height: 3.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DICCIONARIO DE IDIOMAS (ESTÉTICA Y TEXTOS) ---
languages = {
    "Español 🇲🇽": {
        "title": "OKR Performance Builder",
        "subtitle": "Define y registra tus objetivos estratégicos.",
        "step1": "1. Define tu Objetivo",
        "step2": "2. Revisa y Envía",
        "draft_label": "Borrador de tu OKR:",
        "role_label": "Nivel del Rol:",
        "btn_gen": "REFINAR CON AI",
        "btn_send": "ENVIAR A TRACKER OFICIAL",
        "success_gen": "✅ OKRs Sugeridos:",
        "success_send": "¡Registrado con éxito!",
        "info_wait": "La propuesta aparecerá aquí.",
        "placeholder": "Ej: Mejorar el performance de Turbo..."
    },
    "Português 🇧🇷": {
        "title": "Gerador de OKRs Rappi",
        "subtitle": "Defina e registre seus objetivos estratégicos.",
        "step1": "1. Defina seu Objetivo",
        "step2": "2. Revise e Envie",
        "draft_label": "Rascunho do seu OKR:",
        "role_label": "Nível do Cargo:",
        "btn_gen": "REFINAR COM IA",
        "btn_send": "ENVIAR PARA TRACKER OFICIAL",
        "success_gen": "✅ OKRs Sugeridos:",
        "success_send": "Registrado com sucesso!",
        "info_wait": "A proposta aparecerá aqui.",
        "placeholder": "Ex: Melhorar o desempenho do Turbo..."
    },
    "English 🇺🇸": {
        "title": "OKR Performance Builder",
        "subtitle": "Define and register your strategic goals.",
        "step1": "1. Define your Goal",
        "step2": "2. Review & Submit",
        "draft_label": "Your OKR Draft:",
        "role_label": "Job Level:",
        "btn_gen": "REFINE WITH AI",
        "btn_send": "SEND TO OFFICIAL TRACKER",
        "success_gen": "✅ Suggested OKRs:",
        "success_send": "Successfully registered!",
        "info_wait": "The AI proposal will appear here.",
        "placeholder": "Ex: Improve Turbo's performance..."
    }
}

# --- 3. BARRA LATERAL (SELECTOR DE IDIOMA) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)
    selected_lang = st.selectbox("🌐 Idioma / Language", list(languages.keys()))
    t = languages[selected_lang] # Atajo para los textos
    
    st.markdown("---")
    st.markdown(f"### 🎓 Udemy")
    st.markdown(f'<a href="https://rappi.udemy.com/" target="_blank">Udemy Business →</a>', unsafe_allow_html=True)

# --- 4. INTERFAZ ---
st.markdown(f'<h1 class="main-title">{t["title"]}</h1>', unsafe_allow_html=True)
st.write(t["subtitle"])

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t["step1"])
    role = st.selectbox(t["role_label"], ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    draft = st.text_area(t["draft_label"], height=200, placeholder=t["placeholder"])
    
    if st.button(t["btn_gen"]):
        if draft:
            with st.spinner('AI is processing...'):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Prompt dinámico según idioma seleccionado
                    prompt = f"""
                    Context: Rappi Performance Cycle. Role: {role}.
                    Task: Convert draft into 3 SMART OKRs in {selected_lang}.
                    Draft: {draft}
                    Output: JSON list with keys: Objetivo, KR, Metrica, Meta, Deadline.
                    """
                    
                    response = model.generate_content(prompt)
                    match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    if match:
                        st.session_state.okr_results = json.loads(match.group())
                        st.session_state.current_role = role
                    else: st.error("Error: JSON format.")
                except: st.error("API Key Error.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t["step2"])
    
    if 'okr_results' in st.session_state:
        st.table(st.session_state.okr_results)
        if st.button(t["btn_send"]):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_new = pd.DataFrame(st.session_state.okr_results)
                df_new['Role'] = st.session_state.current_role
                df_new['Language'] = selected_lang
                df_new['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                existing = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
                updated = pd.concat([existing, df_new], ignore_index=True)
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated)
                st.success(t["success_send"])
                st.balloons()
            except Exception as e: st.error(f"Error: {e}")
    else:
        st.info(t["info_wait"])
    st.markdown('</div>', unsafe_allow_html=True)
