import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Generator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* TITULO EQUILIBRADO (50px) */
    .main-title { 
        color: #FF441F !important; 
        font-size: 50px !important; 
        font-weight: 800 !important; 
        line-height: 1.1 !important;
        margin-bottom: 5px !important;
    }
    
    .subtitle { color: #555555; font-size: 18px; margin-bottom: 30px; }
    
    .stButton>button { 
        background-color: #FF441F; 
        color: white; 
        border-radius: 10px; 
        font-weight: bold; 
        height: 3.5em; 
        width: 100%;
        border: none;
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

# --- HEADER ---
st.markdown('<h1 class="main-title">Rappi OKR Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Optimización inteligente de objetivos estratégicos.</p>', unsafe_allow_html=True)

# --- CUERPO DE LA APP ---
col_main, col_side = st.columns([1.6, 1])

with col_main:
    # Solo entrada de borrador
    st.subheader("Tu Borrador de OKR")
    user_draft = st.text_area(
        "Describe tu objetivo:", 
        placeholder="Ej: Incrementar la adopción de Rappi Pro en usuarios de Turbo...",
        height=280,
        label_visibility="collapsed"
    )
    st.caption("🔒 Seguridad Rappi: Procesamiento privado en tiempo real.")

with col_side:
    st.subheader("Configuración")
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    
    st.info("Escribe tu idea a la izquierda y selecciona tu nivel para generar sugerencias alineadas.")
    generate_btn = st.button("GENERAR OKRs SMART")

st.divider()

# --- LÓGICA DE IA ---
if generate_btn:
    if not user_draft:
        st.warning("⚠️ Ingresa un borrador para continuar.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Error de configuración de API.")
    else:
        with st.spinner('Refinando OKR...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como estratega de Rappi. Convierte este borrador: "{user_draft}"
                Nivel de jerarquía: {role}.
                Salida: 3 opciones SMART en JSON (Objetivo, KR, Métrica, Meta, Deadline, Explicacion_SMART).
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                st.subheader("🚀 Propuestas de OKRs Sugeridos")
                st.table(okr_data)
                
                excel_file = export_to_excel(okr_data)
                st.download_button("📥 DESCARGAR EXCEL", excel_file, "Sugerencias_OKR.xlsx")
                
            except:
                st.error("Error al procesar. Intenta ser más descriptivo.")

# --- SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.caption("v2.3 | Secure Internal Tool")
st.sidebar.markdown(
    '<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="110"></div>', 
    unsafe_allow_html=True
)
