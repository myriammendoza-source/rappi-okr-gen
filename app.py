import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import re

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Builder", layout="wide")

# CSS para look corporativo (Naranja Rappi #FF441F)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button {
        background-color: #FF441F;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA INTERNA ---
def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKR_Export')
    return output.getvalue()

# --- INTERFAZ ---
st.title("Rappi OKR Builder")
st.write("Herramienta interna para la alineación de objetivos estratégicos.")

col1, col2 = st.columns([2, 1])

with col1:
    drive_url = st.text_input("Enlace de Google Drive (6Pager)", 
                               placeholder="Pega el link de tu documento aquí...")
    
with col2:
    role = st.selectbox("Tu Rol", ["Individual Contributor", "Manager", "Head / Director", "VP"])

st.divider()

# Solo cuando el usuario hace clic, validamos la API Key
if st.button("Generar OKRs SMART"):
    if not drive_url:
        st.warning("Por favor, introduce un enlace de Google Drive.")
    else:
        # Validación silenciosa de la llave
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Error de configuración interna. Contacta al administrador (Falta API Key en Secrets).")
        else:
            with st.spinner('Procesando estrategia...'):
                try:
                    # Configuración bajo demanda
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    # Simulación de IA (Aquí conectaremos la lectura del Drive)
                    results = [
                        {"Objetivo": "Maximizar eficiencia en Turbo", "KR": "Reducir picking time a <90s", "Métrica": "Segundos", "Meta": "90", "Deadline": "Q4 2024"},
                        {"Objetivo": "Crecimiento Prime", "KR": "Incrementar conversión en checkout", "Métrica": "%", "Meta": "+5%", "Deadline": "Q4 2024"}
                    ]
                    
                    st.subheader("Propuesta de OKRs")
                    st.table(results)
                    
                    excel_file = export_to_excel(results)
                    st.download_button("📥 Descargar Reporte Excel", excel_file, "okrs_rappi.xlsx")
                except Exception as e:
                    st.error(f"Hubo un problema al procesar el archivo. Revisa los permisos del link.")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=100)
st.sidebar.markdown("---")
st.sidebar.caption("Versión 1.2.0 | Internal Strategy")
