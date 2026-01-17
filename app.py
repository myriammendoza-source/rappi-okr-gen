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
    .stButton>button { 
        background-color: #FF441F; 
        color: white; 
        border-radius: 8px; 
        font-weight: bold; 
        height: 3em; 
        width: 100%;
        border: none;
    }
    .main-title { color: #FF441F; font-size: 35px; font-weight: bold; margin-bottom: 0px; }
    .subtitle { color: #666666; font-size: 16px; margin-bottom: 30px; }
    .privacy-tag { color: #999999; font-size: 11px; margin-top: 10px; }
    /* Estilo para el logo en el sidebar */
    .sidebar-logo { margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Propuesta_OKRs')
    return output.getvalue()

# --- HEADER PRINCIPAL ---
st.markdown('<p class="main-title">Rappi OKR Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Herramienta estratégica para la creación de OKRs basados en roles y documentación corporativa.</p>', unsafe_allow_html=True)

# --- CUERPO DE LA APP ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("1. Contexto Estratégico")
    context_text = st.text_area(
        "Ingresa información del 6Pager, OKRs de Jefe o Estrategia:", 
        height=250, 
        placeholder="Pega aquí el contenido relevante..."
    )
    
    st.subheader("2. Tu Borrador de OKR")
    user_draft = st.text_area(
        "Escribe tu idea inicial:", 
        placeholder="Ej: Aumentar la eficiencia del equipo de soporte.",
        height=100
    )
    st.markdown('<p class="privacy-tag">🔒 Procesamiento seguro en memoria. Datos no almacenados.</p>', unsafe_allow_html=True)

with col2:
    st.subheader("Configuración")
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    
    st.markdown("---")
    generate_btn = st.button("OPTIMIZAR HACIA SMART")

st.divider()

# --- LÓGICA DE IA ---
if generate_btn:
    if not user_draft:
        st.warning("Debes ingresar un borrador para que la IA pueda trabajar.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("API Key no configurada.")
    else:
        with st.spinner('Refinando OKR con estándares SMART de Rappi...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como un Senior Strategy Manager de Rappi. 
                Convierte este borrador: "{user_draft}" en versiones SMART.
                Usa este contexto: {context_text}
                Nivel del rol: {role}
                
                Reglas:
                1. Genera 3 sugerencias SMART.
                2. Asegura alineación con eficiencia, IA o prioridades Rappi.
                3. Responde solo JSON con: Objetivo, KR, Métrica, Meta, Deadline, Explicacion_SMART.
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                st.subheader("🚀 Propuestas SMART Generadas")
                st.table(okr_data)
                
                excel_file = export_to_excel(okr_data)
                st.download_button("📥 DESCARGAR EN EXCEL", excel_file, "Rappi_OKRs_Optimized.xlsx")
                
            except Exception as e:
                st.error("No se pudo procesar la solicitud. Intenta con un borrador más descriptivo.")

# --- SIDEBAR (LOGO Y VERSIÓN) ---
st.sidebar.markdown("---")
st.sidebar.caption("v2.1 | Secure Internal Tool")
# El logo debajo de la versión como solicitaste
st.sidebar.markdown(
    '<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="100"></div>', 
    unsafe_allow_html=True
)
