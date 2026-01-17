import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Builder", layout="wide")

# CSS para restaurar el Look & Feel corporativo
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
        height: 3em;
    }
    .main-title { color: #FF441F; font-size: 40px; font-weight: bold; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    .privacy-tag { color: #888888; font-size: 12px; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKR_Export')
    return output.getvalue()

# --- INTERFAZ ---
st.markdown('<p class="main-title">Rappi OKR Builder</p>', unsafe_allow_html=True)
st.write("Herramienta estratégica para la definición de objetivos de alto impacto.")

col1, col2 = st.columns([2, 1])

with col1:
    context_text = st.text_area("Contenido del 6Pager / Estrategia", 
                               placeholder="Pega aquí el texto de tu documento confidencial...",
                               height=350)
    st.markdown('<p class="privacy-tag">🔒 Los datos se procesan en memoria y no se almacenan.</p>', unsafe_allow_html=True)

with col2:
    st.subheader("Parámetros")
    role = st.selectbox("Nivel del Rol", ["Individual Contributor", "Manager", "Head / Director", "VP"])
    quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"])
    
    st.markdown("---")
    generate_btn = st.button("GENERAR OKRs ESTRATÉGICOS")

st.divider()

if generate_btn:
    if not context_text:
        st.warning("El campo de contenido no puede estar vacío.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Error: Configura la GEMINI_API_KEY en los Secrets de Streamlit.")
    else:
        with st.spinner('Analizando con Gemini Pro...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                is_leader = role in ["Manager", "Head / Director", "VP"]
                
                prompt = f"""
                Actúa como un Senior PM de Rappi. Basado en este texto: {context_text[:4000]}
                Genera entre 3 y 5 OKRs SMART.
                Reglas Obligatorias:
                1. Uno de AI/Eficiencia.
                2. Uno de prioridades Rappi (Growth/Profit/UX).
                3. {'Uno de eNPS de equipo' if is_leader else 'Uno de desarrollo profesional personal'}.
                
                Devuelve la respuesta EXCLUSIVAMENTE en formato JSON plano (lista de objetos) con llaves: 
                "Objetivo", "KR", "Métrica", "Meta", "Deadline". Sin texto adicional.
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                st.subheader(f"Propuesta de OKRs - {quarter}")
                st.table(okr_data)
                
                excel_file = export_to_excel(okr_data)
                st.download_button(
                    label="📥 DESCARGAR EXCEL",
                    data=excel_file,
                    file_name=f"OKRs_Rappi_{role}_{quarter}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error("Hubo un error al procesar el texto. Intenta pegar una sección más corta o clara.")

# Sidebar limpia
st.sidebar.title("Rappi Tech")
st.sidebar.info("Esta herramienta usa la API de Gemini para procesamiento seguro de lenguaje natural.")
