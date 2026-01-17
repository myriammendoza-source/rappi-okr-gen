import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import json
import re
from datetime import datetime

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Rappi OKR Generator", layout="wide")

# Diccionario de Idiomas
languages = {
    "Español 🇲🇽": {"title": "OKR Performance Builder", "btn_gen": "REFINAR CON IA", "btn_send": "ENVIAR AL REPOSITORIO", "success": "¡Enviado al Excel!", "draft": "Tu Borrador:"},
    "Português 🇧🇷": {"title": "Gerador de OKRs Rappi", "btn_gen": "REFINAR COM IA", "btn_send": "ENVIAR AO REPOSITÓRIO", "success": "Enviado para o Excel!", "draft": "Seu Rascunho:"},
    "English 🇺🇸": {"title": "OKR Performance Builder", "btn_gen": "REFINE WITH AI", "btn_send": "SEND TO REPOSITORY", "success": "Sent to Excel!", "draft": "Your Draft:"}
}

st.markdown("""
    <style>
    .main-title { color: #FF441F; font-size: 42px; font-weight: 800; }
    .card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid #EEE; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & IDIOMA ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)
    selected_lang = st.selectbox("🌐 Language", list(languages.keys()))
    t = languages[selected_lang]
    st.info("v3.4 | Automated Repository Mode")

# --- CUERPO PRINCIPAL ---
st.markdown(f'<h1 class="main-title">{t["title"]}</h1>', unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    role = st.selectbox("Job Level", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    draft = st.text_area(t["draft"], height=200)
    
    if st.button(t["btn_gen"]):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Expert OKR Coach. Role: {role}. Language: {selected_lang}. Convert: '{draft}' into 3 SMART OKRs. Return ONLY a JSON list with: Objetivo, KR, Metrica, Meta, Deadline."
            
            response = model.generate_content(prompt)
            match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if match:
                st.session_state.okrs = json.loads(match.group())
                st.session_state.role = role
            else:
                st.error("AI Format Error.")
        except Exception as e:
            st.error(f"API Error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_out:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if 'okrs' in st.session_state:
        st.write("### Review / Revisión")
        st.table(st.session_state.okrs)
        
        if st.button(t["btn_send"]):
            try:
                # CONEXIÓN Y ESCRITURA ESTILO FORMS
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # Crear DataFrame con el nuevo registro
                new_entry = pd.DataFrame(st.session_state.okrs)
                new_entry['Role'] = st.session_state.role
                new_entry['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry['Language'] = selected_lang

                # 1. Leer datos existentes
                existing_data = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
                
                # 2. Concatenar (Añadir fila al final)
                updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
                
                # 3. Guardar todo el set actualizado en el repositorio
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated_data)
                
                st.balloons()
                st.success(t["success"])
                del st.session_state.okrs # Limpiar para nuevo envío
            except Exception as e:
                st.error(f"Error saving to Sheets: {e}")
    else:
        st.info("Waiting for AI generation...")
    st.markdown('</div>', unsafe_allow_html=True)
