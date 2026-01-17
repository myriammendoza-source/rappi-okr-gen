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
        height: 3.5em; 
        width: 100%;
        border: none;
        font-size: 16px;
    }
    /* Título con letra más grande (50px) */
    .main-title { 
        color: #FF441F; 
        font-size: 50px; 
        font-weight: 900; 
        margin-bottom: -10px;
        line-height: 1.2;
    }
    .subtitle { color: #666666; font-size: 18px; margin-bottom: 35px; }
    .privacy-tag { color: #999999; font-size: 11px; margin-top: 10px; }
    .sidebar-logo { margin-top: 25px; }
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
st.markdown('<p class="subtitle">Transforma borradores en objetivos SMART alineados con la estrategia de Rappi.</p>', unsafe_allow_html=True)

# --- CUERPO DE LA APP ---
col1, col2 = st.columns([1.6, 1])

with col1:
    st.subheader("1. Contexto Estratégico")
    context_text = st.text_area(
        "Documentación de soporte (6Pager, OKRs de Jefe, etc.):", 
        height=250, 
        placeholder="Pega aquí el contenido que servirá de guía para la IA..."
    )
    
    st.subheader("2. Tu Borrador de OKR")
    user_draft = st.text_area(
        "Idea inicial de tu objetivo:", 
        placeholder="Ej: Optimizar la conversión del funnel de Rappi Pay.",
        height=100
    )
    st.markdown('<p class="privacy-tag">🔒 Procesamiento seguro. Los datos no se guardan en servidores externos.</p>', unsafe_allow_html=True)

with col2:
    st.subheader("Configuración")
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    
    st.info("""
    **Guía rápida:**
    1. Define tu **Nivel de Rol**.
    2. Provee el **Contexto** (estrategia).
    3. Escribe tu **Borrador**.
    4. El sistema generará 3 opciones SMART.
    """)
    
    generate_btn = st.button("GENERAR OKRs OPTIMIZADOS")

st.divider()

# --- LÓGICA DE IA ---
if generate_btn:
    if not user_draft:
        st.warning("⚠️ Ingresa un borrador para continuar.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Error: API Key no detectada en Secrets.")
    else:
        with st.spinner('Gemini está puliendo tus objetivos...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como experto en estrategia corporativa en Rappi. 
                Refina este borrador: "{user_draft}" basándote en: {context_text}
                Para un perfil nivel: {role}.
                
                Salida requerida:
                - 3 opciones SMART.
                - Incluir enfoque en IA y prioridades de negocio (Growth/EBITDA).
                - Formato JSON lista de objetos: Objetivo, KR, Métrica, Meta, Deadline, Explicacion_SMART.
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                st.subheader("🚀 Propuestas de OKRs Refinados")
                st.table(okr_data)
                
                excel_file = export_to_excel(okr_data)
                st.download_button("📥 DESCARGAR RESULTADOS (EXCEL)", excel_file, "Rappi_OKR_Optimized.xlsx")
                
            except Exception as e:
                st.error("Hubo un problema al generar la respuesta. Intenta simplificar el texto de entrada.")

# --- SIDEBAR (VERSIÓN Y LOGO AL FINAL) ---
st.sidebar.markdown("---")
st.sidebar.caption("v2.1 | Secure Internal Tool")
st.sidebar.markdown(
    '<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="120"></div>', 
    unsafe_allow_html=True
)
