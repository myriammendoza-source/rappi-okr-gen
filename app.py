import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Generator", layout="wide")

# CSS Forzado para Título Gigante y Limpieza
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* TITULO GIGANTE FORZADO */
    .main-title { 
        color: #FF441F !important; 
        font-size: 80px !important; 
        font-weight: 900 !important; 
        line-height: 1 !important;
        margin-bottom: 5px !important;
        letter-spacing: -3px !important;
    }
    
    .subtitle { color: #444444; font-size: 22px; margin-bottom: 40px; }
    
    .stButton>button { 
        background-color: #FF441F; 
        color: white; 
        border-radius: 12px; 
        font-weight: bold; 
        height: 4em; 
        width: 100%;
        border: none;
        font-size: 18px;
    }
    
    .sidebar-logo { margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Propuesta_OKRs')
    return output.getvalue()

# --- HEADER (SIN PUNTOS EXTRA) ---
st.markdown('<h1 class="main-title">Rappi OKR Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transforma tus ideas en objetivos SMART de alto impacto.</p>', unsafe_allow_html=True)

# --- CUERPO DE LA APP ---
col_main, col_side = st.columns([1.6, 1])

with col_main:
    # ÚNICA ENTRADA: El borrador
    st.subheader("Tu Borrador de OKR")
    user_draft = st.text_area(
        "¿Qué quieres lograr?", 
        placeholder="Ej: Mejorar la experiencia de usuario en el checkout de Turbo...",
        height=250,
        label_visibility="collapsed" # Escondemos el label para más limpieza
    )
    st.caption("🔒 Los datos se procesan de forma segura y privada.")

with col_side:
    st.subheader("Configuración")
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    
    st.write("Presiona el botón para que Gemini optimice tu idea basándose en estándares de Rappi.")
    generate_btn = st.button("OPTIMIZAR HACIA SMART")

st.divider()

# --- LÓGICA DE IA ---
if generate_btn:
    if not user_draft:
        st.warning("⚠️ Escribe un borrador primero.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Error: API Key no encontrada.")
    else:
        with st.spinner('Refinando...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como estratega Senior en Rappi. 
                Convierte este borrador: "{user_draft}" en 3 versiones SMART.
                Nivel: {role}.
                Formato JSON: Objetivo, KR, Métrica, Meta, Deadline, Explicacion_SMART.
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                st.subheader("🚀 Propuestas Generadas")
                st.table(okr_data)
                
                excel_file = export_to_excel(okr_data)
                st.download_button("📥 DESCARGAR EXCEL", excel_file, "OKRs_Rappi.xlsx")
                
            except:
                st.error("Error al procesar. Intenta con un borrador más claro.")

# --- SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.caption("v2.3 | Secure Internal Tool")
st.sidebar.markdown(
    '<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="130"></div>', 
    unsafe_allow_html=True
)
