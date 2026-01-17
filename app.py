import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rappi OKR Builder | Secure", layout="wide")

# Estilo Corporativo Minimalista
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; font-weight: bold; }
    .stTextArea>div>div>textarea { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mis_OKRs')
    return output.getvalue()

# --- INTERFAZ ---
st.title("Rappi OKR Builder")
st.warning("🔒 PRIVACIDAD: El contenido pegado se procesa en memoria y no se almacena en ninguna base de datos.")

col1, col2 = st.columns([2, 1])
with col1:
    # Cambiamos Link por Texto Directo para evitar exponer archivos
    context_text = st.text_area("Pega aquí el contenido de tu 6Pager o Estrategia:", height=300, 
                                placeholder="Copia el texto del documento de Drive y pégalo aquí...")
with col2:
    role = st.selectbox("Tu Rol", ["Individual Contributor", "Manager", "Head / Director", "VP"])
    is_leader = role in ["Manager", "Head / Director", "VP"]

st.divider()

if st.button("Generar OKRs Seguros"):
    if not context_text:
        st.warning("Por favor, pega el contenido de tu documento.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Error: API Key no configurada en los Secrets.")
    else:
        with st.spinner('Analizando información bajo protocolo de seguridad...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt estructurado para recibir una respuesta en formato JSON limpio
                prompt = f"""
                Actúa como un Senior PM en Rappi. Basado en este texto:
                ---
                {context_text}
                ---
                Genera entre 3 y 5 OKRs SMART. 
                REGLAS:
                1. Uno de AI.
                2. Uno de prioridades Rappi (Growth/Profit/UX).
                3. {'Uno de eNPS de equipo' if is_leader else 'Uno de desarrollo profesional personal'}.
                
                Devuelve la respuesta EXCLUSIVAMENTE como un JSON válido que sea una lista de objetos con estas llaves: 
                "Objetivo", "KR", "Métrica", "Meta", "Deadline". 
                No agregues texto extra antes o después del JSON.
                """
                
                response = model.generate_content(prompt)
                
                # Limpiar la respuesta de posibles marcas de código (```json ...)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                # Mostrar resultados
                st.subheader("Resultados Generados")
                st.table(okr_data)
                
                # Excel
                excel_file = export_to_excel(okr_data)
                st.download_button("📥 Descargar OKRs en Excel", excel_file, "okrs_rappi.xlsx")
                
            except Exception as e:
                st.error("Error al procesar. Asegúrate de que el texto sea suficiente para extraer objetivos.")

st.sidebar.image("[https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg](https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg)", width=100)
