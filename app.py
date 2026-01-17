import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import json
import re

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Rappi OKR Performance", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; }
    .main-title { color: #1a1a1a; font-size: 48px; font-weight: 700; margin-bottom: 0px; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 6px; font-weight: bold; border: none; width: 100%; height: 3.5em; }
    .udemy-card { background-color: #FFFFFF; padding: 20px; border-left: 5px solid #A435F0; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN TRACKER ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1XMkYvkD1XIme_B5u0xZd160XFBLahCh3UgybVHF1b6Y/edit#gid=1300408541"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SIDEBAR: RECURSOS Y UDEMY ---
with st.sidebar:
    st.markdown("### 🎓 Recursos de Aprendizaje")
    st.markdown("""
        <div class="udemy-card">
        <strong>Ruta Udemy Business</strong><br>
        Aprende a redactar OKRs de alto impacto.<br>
        <a href="https://rappi.udemy.com/" target="_blank">Ir a Udemy →</a>
        </div>
    """, unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=120)

# --- CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">OKR Performance Builder</h1>', unsafe_allow_html=True)
st.write("Refina tus objetivos con IA y regístralos en el Tracker oficial de Rappi.")

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("Paso 1: Tu Borrador")
    role = st.selectbox("Nivel del Rol", ["Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    draft = st.text_area("¿Cuál es tu objetivo para este ciclo?", height=200, placeholder="Ej: Mejorar el performance de Turbo MX...")
    
    if st.button("Refinar con Gemini AI"):
        if draft:
            with st.spinner('Gemini está aplicando metodología SMART...'):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Actúa como un experto en OKRs de Rappi. Convierte este borrador: '{draft}' en un OKR SMART para un nivel {role}. Devuelve solo un JSON con: Objetivo, KR, Metrica, Meta, Deadline."
                response = model.generate_content(prompt)
                
                # Extracción de datos
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if match:
                    st.session_state.okrs = json.loads(match.group())
                else:
                    st.error("Error al procesar el formato. Intenta nuevamente.")

with col_output:
    st.subheader("Paso 2: Revisión y Envío")
    if 'okrs' in st.session_state:
        st.table(st.session_state.okrs)
        
        if st.button("🚀 ENVIAR A REPOSITORIO (EXCEL)"):
            # Lógica de registro en Google Sheets
            existing_df = conn.read(spreadsheet=URL_SHEET)
            new_row = pd.DataFrame(st.session_state.okrs)
            new_row['User_Role'] = role
            
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, data=updated_df)
            
            st.success("¡Registrado con éxito en el Tracker de Performance!")
            st.balloons()
    else:
        st.info("Aquí aparecerá tu propuesta SMART una vez que hagas clic en 'Refinar'.")
