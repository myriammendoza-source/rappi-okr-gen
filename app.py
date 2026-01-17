import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import json
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL Y DICCIONARIO MULTIDIOMA ---
st.set_page_config(page_title="Rappi OKR Builder | Performance", layout="wide")

languages = {
    "Español 🇲🇽": {
        "title": "OKR Performance Builder",
        "subtitle": "Transforma tus ideas en objetivos SMART alineados a Rappi.",
        "step1": "1. Define tu Objetivo",
        "step2": "2. Revisa y Envía",
        "draft_label": "Borrador de tu OKR:",
        "role_label": "Nivel del Rol:",
        "btn_gen": "REFINAR CON IA",
        "btn_send": "ENVIAR A REPOSITORIO OFICIAL",
        "success_gen": "✅ Propuesta generada:",
        "success_send": "¡Registrado con éxito en el Tracker!",
        "info_wait": "La propuesta de la IA aparecerá aquí.",
        "placeholder": "Ej: Mejorar el tiempo de entrega en Turbo MX..."
    },
    "Português 🇧🇷": {
        "title": "Gerador de OKRs Rappi",
        "subtitle": "Transforme suas ideias em objetivos SMART alinhados à Rappi.",
        "step1": "1. Defina seu Objetivo",
        "step2": "2. Revise e Envie",
        "draft_label": "Rascunho do seu OKR:",
        "role_label": "Nível do Cargo:",
        "btn_gen": "REFINAR COM IA",
        "btn_send": "ENVIAR PARA REPOSITÓRIO OFICIAL",
        "success_gen": "✅ Proposta gerada:",
        "success_send": "Registrado com sucesso no Tracker!",
        "info_wait": "A proposta da IA aparecerá aqui.",
        "placeholder": "Ex: Melhorar o tempo de entrega no Turbo MX..."
    },
    "English 🇺🇸": {
        "title": "OKR Performance Builder",
        "subtitle": "Transform your ideas into SMART goals aligned with Rappi.",
        "step1": "1. Define your Goal",
        "step2": "2. Review & Submit",
        "draft_label": "Your OKR Draft:",
        "role_label": "Job Level:",
        "btn_gen": "REFINE WITH AI",
        "btn_send": "SEND TO OFFICIAL REPOSITORY",
        "success_gen": "✅ Generated Proposal:",
        "success_send": "Successfully registered in the Tracker!",
        "info_wait": "The AI proposal will appear here.",
        "placeholder": "Ex: Improve delivery time in Turbo MX..."
    }
}

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; }
    .main-title { color: #1a1a1a; font-size: 42px; font-weight: 800; margin-bottom: 0px; }
    .card { background-color: #FFFFFF; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #E0E0E0; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; height: 3.5em; }
    .udemy-card { background-color: #FFFFFF; padding: 15px; border-left: 5px solid #A435F0; border-radius: 8px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR Y SELECTOR DE IDIOMA ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)
    selected_lang = st.selectbox("🌐 Language / Idioma", list(languages.keys()))
    t = languages[selected_lang]
    st.markdown("---")
    st.markdown(f'<div class="udemy-card"><strong>Udemy Business</strong><br>Ruta OKRs Rappi<br><a href="https://rappi.udemy.com/" target="_blank">Acceder →</a></div>', unsafe_allow_html=True)
    st.caption("v3.2 | Secure & Internal")

# --- 3. INTERFAZ PRINCIPAL ---
st.markdown(f'<h1 class="main-title">{t["title"]}</h1>', unsafe_allow_html=True)
st.write(t["subtitle"])

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t["step1"])
    role = st.selectbox(t["role_label"], ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    draft = st.text_area(t["draft_label"], height=200, placeholder=t["placeholder"])
    
    if st.button(t["btn_gen"]):
        if not draft:
            st.warning("⚠️ Escribe algo para comenzar.")
        elif "GEMINI_API_KEY" not in st.secrets:
            st.error("🔑 API Key no configurada en Secrets.")
        else:
            with st.spinner('Analizando...'):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Seguridad para evitar InvalidArgument
                    safety = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                    
                    prompt = f"Expert OKR Coach at Rappi. Role: {role}. Language: {selected_lang}. Convert this: '{draft}' into 3 SMART OKRs. Return ONLY a JSON list with: Objetivo, KR, Metrica, Meta, Deadline."
                    
                    response = model.generate_content(prompt, safety_settings=safety)
                    match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if match:
                        st.session_state.okr_results = json.loads(match.group())
                        st.session_state.current_role = role
                    else:
                        st.error("Error de formato en la respuesta de IA.")
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_output:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t["step2"])
    
    if 'okr_results' in st.session_state:
        st.table(st.session_state.okr_results)
        
        if st.button(t["btn_send"]):
            try:
                # Conexión al Sheet
                conn = st.connection("gsheets", type=GSheetsConnection)
                url = "https://docs.google.com/spreadsheets/d/1XMkYvkD1XIme_B5u0xZd160XFBLahCh3UgybVHF1b6Y/edit#gid=1300408541"
                
                new_data = pd.DataFrame(st.session_state.okr_results)
                new_data['Role'] = st.session_state.current_role
                new_data['Language'] = selected_lang
                new_data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Leer y actualizar
                existing = conn.read(spreadsheet=url)
                updated = pd.concat([existing, new_data], ignore_index=True)
                conn.update(spreadsheet=url, data=updated)
                
                st.balloons()
                st.success(t["success_send"])
            except Exception as e:
                st.error(f"Error al guardar: {e}")
    else:
        st.info(t["info_wait"])
    st.markdown('</div>', unsafe_allow_html=True)
