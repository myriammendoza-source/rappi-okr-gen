import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Rappi OKR Generator", page_icon="🧡")

# --- FUNCIONES DE EXPORTACIÓN ---
def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mis_OKRs')
    return output.getvalue()

# --- INTERFAZ ---
st.title("🧡 Rappi OKR Generator")

# Entrada para la API Key (Para que no la dejes fija en el código por seguridad)
api_key_input = st.text_input("Pega aquí tu Gemini API Key:", type="password")

is_leader = st.radio("¿Eres líder?", ("Sí", "No"))
uploaded_file = st.file_uploader("Sube tu 6Pager (PDF)", type=["pdf"])

if st.button("Generar OKRs"):
    if not api_key_input:
        st.error("Debes pegar la API Key que sacaste de Google AI Studio.")
    else:
        # Aquí conectamos con Gemini usando la llave que pegaste en la web
        genai.configure(api_key=api_key_input)
        
        # Simulación de respuesta (Esto se verá en tu pantalla)
        mis_okrs = [
            {"Objetivo": "Liderazgo en Mercado", "KR": "Crecer 20% en pedidos", "Métrica": "Órdenes", "Meta": "+20%", "Deadline": "Dic 2024"}
        ]
        
        st.table(mis_okrs)
        
        excel_file = export_to_excel(mis_okrs)
        st.download_button(label="Descargar Excel", data=excel_file, file_name="okrs.xlsx")
