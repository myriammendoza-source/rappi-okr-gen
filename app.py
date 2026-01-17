import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import json
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL Y BRANDING ---
st.set_page_config(page_title="Rappi OKR Builder | Performance", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; }
    
    .main-title { color: #1a1a1a; font-size: 42px; font-weight: 800; margin-bottom: 0px; }
    .card { background-color: #FFFFFF; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #E0E0E0; }
    
    .stButton>button { 
        background-color: #FF441F; color: white; border-radius: 8px; 
        font-weight: bold; border: none; width: 100%; height: 3.8em;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #E63D1C; transform: translateY(-2px); }
    
    .udemy-card { 
        background-color: #FFFFFF; padding: 15px; border-left: 5px solid #A435F0; 
        border-radius: 8px; margin-bottom: 20px; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIONES ---
# Conexión al Repositorio Excel (Google Sheets)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1XMkYvkD1XIme_B5u0xZd160XFBLahCh3UgybVHF1b6Y/edit#gid=1300408541"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. BARRA LATERAL (RECURSOS) ---
with st.sidebar:
    st.markdown("### 🎓 Learning Resources")
    st.markdown("""
        <div class="udemy-card">
        <strong>Udemy Business: OKR Mastery</strong><br>
        Ruta de aprendizaje recomendada para Rappi Latam.<br>
        <a href="https://rappi.udemy.com/" target="_blank">Acessar Udemy →</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("v3.1 | Internal & Confidential")
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)

# --- 4. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="main-title">OKR Performance Builder</h1>', unsafe_allow_html=True)
st.write("Define, refine and register your strategic objectives / Defina, refine e registre seus objetivos.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("1. Define tu Objetivo / Goal")
    role = st.selectbox("Nivel del Rol / Job Level", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    
    draft = st.text_area(
        "Borrador (ES/EN/PT):", 
        height=220, 
        placeholder="Escribe tu idea aquí... / Escreva sua ideia aqui..."
    )
    
    generate_btn = st.button("REFINAR Y GENERAR PROPUESTA (AI)")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LÓGICA DE INTELIGENCIA ARTIFICIAL (GEMINI) ---
if generate_btn:
    if not draft:
        st.warning("Please enter a draft first / Por favor, ingresa un borrador.")
    else:
        with st.spinner('Gemini is processing (Multilingual Mode)...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                
                # Configuración para evitar errores de InvalidArgument
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt que gestiona el idioma automáticamente
                prompt = f"""
                You are a Rappy Strategy Expert. 
                TASK: Convert the following draft into 3 SMART OKRS.
                DRAFT: {draft}
                LEVEL: {role}
                
                INSTRUCTIONS:
                1. Language: Detect language (ES, EN, or PT) and respond in the SAME language.
                2. Format: Return ONLY a JSON list of objects. No extra text.
                3. Structure: Use keys: Objetivo, KR, Metrica, Meta, Deadline.
                """
                
                response = model.generate_content(prompt, safety_settings=safety_settings)
                
                # Extracción robusta del JSON
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if match:
                    st.session_state.okr_results = json.loads(match.group())
                    st.session_state.current_role = role
                else:
                    st.error("Format Error. Please try a simpler draft.")
            except Exception as e:
                st.error("Connection Error with Gemini. Please verify API Key.")

# --- 6. REVISIÓN Y ENVÍO AL REPOSITORIO (EXCEL) ---
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("2. Revisa y Envía / Review & Submit")
    
    if 'okr_results' in st.session_state:
        st.table(st.session_state.okr_results)
        
        if st.button("📤 ENVIAR AL TRACKER OFICIAL"):
            with st.spinner('Synchronizing with Google Sheets...'):
                try:
                    # Preparar datos para el envío
                    df_new = pd.DataFrame(st.session_state.okr_results)
                    df_new['Role'] = st.session_state.current_role
                    df_new['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Conexión y Update (Append)
                    existing_data = conn.read(spreadsheet=URL_SHEET)
                    updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, data=updated_df)
                    
                    st.balloons()
                    st.success("Successfully registered in Repository! / Registrado com sucesso!")
                except Exception as e:
                    st.error(f"Error syncing with Sheets: {e}")
    else:
        st.info("La propuesta de la IA aparecerá aquí para tu revisión.")
    st.markdown('</div>', unsafe_allow_html=True)
