import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import json
import re

# --- 1. CONFIGURACIÓN VISUAL (ESTILO RAPPI PERFORMANCE PORTAL) ---
st.set_page_config(page_title="Performance Management | Rappi", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F1F3F4; }
    .main-header { color: #202124; font-size: 40px; font-weight: 600; margin-bottom: 5px; }
    .card { background-color: #FFFFFF; padding: 25px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 4px; border: none; font-weight: bold; height: 3.5em; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
# URL de tu Tracker oficial
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XMkYvkD1XIme_B5u0xZd160XFBLahCh3UgybVHF1b6Y/edit#gid=1300408541"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. INTERFAZ ---
st.markdown('<h1 class="main-header">Performance Management</h1>', unsafe_allow_html=True)
st.write("OKR Builder & Strategic Tracker")

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown("### Guidelines")
    st.info("Escribe tu idea técnica (Turbo MX, Merchants, CPGs) y selecciona tu nivel para que la IA proponga el KR.")
    role = st.selectbox("Job Level", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])

with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    user_draft = st.text_area("Borrador del Objetivo", height=200, placeholder="Ej: Asegurar el 100% de capacitación en Turbo MX...")
    generate_btn = st.button("GENERAR Y GUARDAR EN TRACKER")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. LÓGICA DE PROCESAMIENTO ---
if generate_btn:
    if not user_draft:
        st.warning("⚠️ Ingresa un borrador.")
    else:
        with st.spinner('Conectando con Gemini & Google Sheets...'):
            try:
                # Configurar Gemini
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Actúa como Strategy Manager en Rappi. Refina: '{user_draft}' para nivel {role}. Devuelve un JSON lista con: Objetivo, KR, Metrica, Meta, Deadline."
                response = model.generate_content(prompt)
                
                # Extraer JSON
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if match:
                    okr_data = json.loads(match.group())
                    st.success("✅ Propuesta generada:")
                    st.table(okr_data)
                    
                    # GUARDAR EN GOOGLE SHEETS
                    # Leemos datos actuales, agregamos los nuevos y escribimos
                    existing_data = conn.read(spreadsheet=SHEET_URL)
                    new_data = pd.DataFrame(okr_data)
                    new_data['User_Role'] = role
                    updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                    
                    conn.update(spreadsheet=SHEET_URL, data=updated_df)
                    st.balloons()
                    st.info("🚀 OKRs sincronizados con el Google Sheet de Performance.")
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- SIDEBAR ---
st.sidebar.caption("v3.0 | Secure Internal Tool")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)
