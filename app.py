import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rappi OKR Generator", page_icon="🧡")

# Intentamos sacar la API Key de los Secretos de la plataforma
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
except:
    st.error("⚠️ Configuración faltante: La API Key no está en los Secretos.")

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mis_OKRs')
    return output.getvalue()

# --- INTERFAZ ---
st.title("Generador Automático de OKRs")
st.info("Sube tu documento y el sistema extraerá los OKRs alineados a tu rol.")

is_leader = st.radio("¿Eres líder?", ("Sí", "No"))
uploaded_file = st.file_uploader("Sube tu 6Pager (PDF)", type=["pdf"])

if st.button("Generar OKRs SMART"):
    if uploaded_file:
        with st.spinner('Gemini está analizando tu documento...'):
            # Aquí simulamos la respuesta de la IA por ahora
            mis_okrs = [
                {"Objetivo": "Optimización Operativa", "KR": "Reducir tiempos de entrega", "Métrica": "Minutos", "Meta": "-10%", "Deadline": "Q4 2024"}
            ]
            st.table(mis_okrs)
            
            excel_file = export_to_excel(mis_okrs)
            st.download_button("📥 Descargar Excel", excel_file, "okrs_rappi.xlsx")
    else:
        st.warning("Por favor sube un archivo PDF primero.")
        st.table(mis_okrs)
        
        excel_file = export_to_excel(mis_okrs)
        st.download_button(label="Descargar Excel", data=excel_file, file_name="okrs.xlsx")
