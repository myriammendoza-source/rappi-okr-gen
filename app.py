import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json
import re

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Generator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #FF441F !important; font-size: 50px !important; font-weight: 800 !important; line-height: 1.1 !important; }
    .subtitle { color: #555555; font-size: 18px; margin-bottom: 30px; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 10px; font-weight: bold; height: 3.5em; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKRs')
    return output.getvalue()

# --- HEADER ---
st.markdown('<h1 class="main-title">Rappi OKR Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Optimización inteligente para Turbo, Merchants, CPGs y Staff.</p>', unsafe_allow_html=True)

col_main, col_side = st.columns([1.6, 1])

with col_main:
    st.subheader("Tu Borrador de OKR")
    user_draft = st.text_area(
        "Describe tu objetivo:", 
        placeholder="Ej: Asegurar que el 100% del Talent Pool en Turbo MX participe en programas de desarrollo...",
        height=280,
        label_visibility="collapsed"
    )

with col_side:
    st.subheader("Configuración")
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    generate_btn = st.button("GENERAR OKRs SMART")

st.divider()

if generate_btn:
    if not user_draft:
        st.warning("⚠️ Ingresa un borrador.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Configura la API Key en Secrets.")
    else:
        with st.spinner('Analizando estrategia de Talent Pool y Upskilling...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt reforzado
                prompt = f"""
                Actúa como Chief People Officer o Strategy Director en Rappi.
                Refina este borrador técnico: "{user_draft}"
                Nivel del rol: {role}.
                Contexto: Talent Management, Upskilling, Turbo MX, CPGs.
                
                Genera 3 opciones SMART en formato JSON.
                IMPORTANTE: Devuelve SOLO el JSON, sin texto explicativo.
                Campos: Objetivo, KR, Métrica, Meta, Deadline, Explicacion_SMART.
                """
                
                response = model.generate_content(prompt)
                
                # LÓGICA DE EXTRACCIÓN ROBUSTA (Busca el contenido entre corchetes [ ])
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if match:
                    okr_data = json.loads(match.group())
                    st.subheader("🚀 Propuestas de OKRs Refinados")
                    st.table(okr_data)
                    
                    excel_file = export_to_excel(okr_data)
                    st.download_button("📥 DESCARGAR EXCEL", excel_file, "OKRs_Rappi_Talent.xlsx")
                else:
                    st.error("La IA devolvió un formato inesperado. Intenta de nuevo.")
                
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")

# --- SIDEBAR ---
st.sidebar.caption("v2.4 | Secure Internal Tool")
st.sidebar.markdown('<img src="[https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg](https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg)" width="110">', unsafe_allow_html=True)
