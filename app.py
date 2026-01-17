import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection # Librería para conectar con Sheets
import json
import re
from datetime import datetime

# --- CONFIGURACIÓN VISUAL (ESTILO RAPPI PERFORMANCE) ---
st.set_page_config(page_title="Performance | OKR Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F1F3F4; }
    .main-header { color: #202124; font-size: 32px; font-weight: 500; margin-bottom: 20px; }
    .card { background-color: #FFFFFF; padding: 25px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 4px; border: none; width: 100%; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
# URL de tu documento de Rappi
URL_SHEET = "https://docs.google.com/spreadsheets/d/1XMkYvkD1XIme_B5u0xZd160XFBLahCh3UgybVHF1b6Y/edit#gid=1300408541"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INTERFAZ ---
st.markdown('<h1 class="main-header">Performance Management: OKR Builder</h1>', unsafe_allow_html=True)

col_info, col_action = st.columns([1, 2], gap="large")

with col_info:
    st.markdown("### 📘 Guía de Ciclo 2026")
    with st.expander("Estructura de OKRs en Rappi", expanded=True):
        st.write("Asegúrate de que tus KRs impacten directamente en el EBITDA o Growth de Turbo/Merchants.")
    
    # Historial rápido (opcional, lee las últimas 5 filas)
    try:
        existing_data = conn.read(spreadsheet=URL_SHEET, usecols=[0,1,2])
        st.info(f"Total OKRs registrados en el tracker: {len(existing_data)}")
    except:
        pass

with col_action:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    user_draft = st.text_area("Borrador de tu objetivo estratégico:", height=150, placeholder="Ej: 100% Talent Pool en Turbo MX...")
    
    generate_btn = st.button("GENERAR Y PREVISUALIZAR")
    st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE IA Y ESCRITURA ---
if generate_btn:
    if not user_draft:
        st.warning("Escribe un borrador primero.")
    else:
        with st.spinner('Gemini optimizando y conectando con el Tracker...'):
            try:
                # 1. Generación con IA
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Actúa como estratega Rappi. Refina: '{user_draft}' para {role}. Devuelve SOLO un JSON lista con: Objetivo, KR, Metrica, Meta, Deadline."
                
                response = model.generate_content(prompt)
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                
                if match:
                    okr_results = json.loads(match.group())
                    st.session_state.temp_okrs = okr_results # Guardar en sesión
                    
                    st.success("✅ OKRs Sugeridos:")
                    st.table(okr_results)
                    
                    # 2. Botón para confirmar envío a Google Sheets
                    if st.button("Confirmar y enviar a Google Sheets"):
                        df_to_add = pd.DataFrame(okr_results)
                        df_to_add['Fecha_Registro'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        df_to_add['Rol'] = role
                        
                        # Actualizar la hoja (Append)
                        conn.create(spreadsheet=URL_SHEET, data=df_to_add)
                        st.balloons()
                        st.success("¡Enviado con éxito al Excel de Performance!")
                else:
                    st.error("Error en formato de IA. Intenta de nuevo.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

st.sidebar.caption("v2.7 | Connected to Performance Tracker")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=100)
