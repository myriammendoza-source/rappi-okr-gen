import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import re

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Builder | Internal Tool", layout="wide")

# CSS inyectado para un look más "Enterprise"
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        background-color: #FF441F;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 2rem;
    }
    .stTextInput>div>div>input { border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NEGOCIO ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Error de autenticación: API Key no detectada.")

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKR_Export')
    return output.getvalue()

def extract_drive_id(url):
    """Extrae el ID del documento de una URL de Google Drive."""
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None

# --- INTERFAZ ---
st.title("Rappi OKR Builder")
st.caption("Internal Strategy Tool | Powered by Gemini Pro")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Configuración de Contexto")
    drive_url = st.text_input("Enlace de Google Drive (6Pager / Estrategia)", 
                               placeholder="https://docs.google.com/document/d/...")
    
    role = st.selectbox("Nivel de Estructura", ["Individual Contributor", "Manager", "Head / Director", "VP"])

with col2:
    st.subheader("Parámetros de Salida")
    quarter = st.select_slider("Trimestre", options=["Q1", "Q2", "Q3", "Q4"])
    language = st.radio("Idioma de redacción", ["Español", "Inglés"], horizontal=True)

st.divider()

if st.button("Generar OKRs Corporativos"):
    if not drive_url:
        st.warning("Se requiere un enlace de Google Drive para proceder.")
    else:
        drive_id = extract_drive_id(drive_url)
        if not drive_id:
            st.error("URL de Google Drive no válida. Asegúrate de que el enlace sea correcto.")
        else:
            with st.spinner('Analizando documentación estratégica...'):
                # PROMPT SYSTEM: Aquí es donde Gemini actúa como PM de Rappi
                # (Simulación de resultado para el prototipo)
                results = [
                    {"Objetivo": "Optimizar el Burn Rate de Growth", "KR": "Reducir CAC en canales pagados", "Métrica": "USD", "Meta": "-15%", "Deadline": "End of Q4"},
                    {"Objetivo": "Excelencia Operativa en Dark Stores", "KR": "Mejorar el picking time promedio", "Métrica": "Segundos", "Meta": "120s", "Deadline": "End of Q4"}
                ]
                
                st.subheader("Propuesta de OKRs SMART")
                st.table(results)
                
                # Exportación
                excel_file = export_to_excel(results)
                st.download_button(
                    label="Exportar a Excel (.xlsx)",
                    data=excel_file,
                    file_name=f"OKRs_Rappi_{quarter}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

st.sidebar.markdown("---")
st.sidebar.info("Esta herramienta procesa datos bajo la política de privacidad de Rappi. No compartas información sensible fuera del dominio @rappi.com.")
