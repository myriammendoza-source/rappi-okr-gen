import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Rappi OKR Generator", layout="wide")

# Estilos corporativos de Rappi
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
        margin-top: 10px;
    }
    .main-title { color: #FF441F; font-size: 38px; font-weight: bold; margin-bottom: 0px; }
    .subtitle { color: #555555; font-size: 18px; margin-bottom: 20px; }
    .privacy-tag { color: #999999; font-size: 11px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKRs_Generados')
    return output.getvalue()

# --- HEADER CON LOGO ---
col_logo, col_empty = st.columns([1, 4])
with col_logo:
    # Método seguro para mostrar el logo sin errores de MediaFileStorage
    st.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="120">', unsafe_allow_html=True)

st.markdown('<p class="main-title">Rappi OKR Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Crea objetivos de alto impacto basados en tu rol y documentación estratégica (6Pagers, OKRs de Liderazgo o Estrategia Global).</p>', unsafe_allow_html=True)

# --- CUERPO DE LA APP ---
col_main, col_side = st.columns([2, 1])

with col_main:
    context_text = st.text_area(
        "Documentación Estratégica / Información Manual", 
        placeholder="Pega aquí el 6Pager, los OKRs de tu jefe o la estrategia de Rappi para dar contexto a la IA...",
        height=400
    )
    st.markdown('<p class="privacy-tag">🔒 Procesamiento seguro: La información no se almacena en bases de datos externas.</p>', unsafe_allow_html=True)

with col_side:
    st.subheader("Configuración")
    
    # Nuevos roles solicitados
    role_options = ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"]
    role = st.selectbox("Nivel del Rol", role_options)
    
    quarter = st.selectbox("Quarter de ejecución", ["Q1", "Q2", "Q3", "Q4"])
    
    st.markdown("---")
    if st.button("GENERAR OKRs SMART"):
        if not context_text:
            st.warning("Por favor, ingresa información estratégica para continuar.")
        elif "GEMINI_API_KEY" not in st.secrets:
            st.error("Error: GEMINI_API_KEY no encontrada en los Secrets.")
        else:
            with st.spinner('Analizando y alineando con la estrategia de Rappi...'):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Lógica para determinar si aplica eNPS
                    is_leader = role in ["Manager", "Head", "Director", "VP"]
                    
                    prompt = f"""
                    Actúa como un experto en estrategia de Rappi. 
                    Contexto proporcionado: {context_text[:5000]}
                    Nivel del colaborador: {role}
                    
                    Genera entre 3 y 5 OKRs SMART adecuados para un {role}.
                    
                    REGLAS DE NEGOCIO:
                    1. OKR de AI: Cómo este rol puede usar IA para ser más eficiente.
                    2. OKR de Prioridad Rappi: Alineado a Profitability, Growth o UX según el texto.
                    3. OKR de Personas: Si es {role} (Líder), incluir eNPS de equipo. Si no es líder, incluir desarrollo de Skills técnicos.
                    
                    Responde únicamente con un JSON (lista de objetos) con: "Objetivo", "KR", "Métrica", "Meta", "Deadline".
                    """
                    
                    response = model.generate_content(prompt)
                    clean_json = response.text.replace('```json', '').replace('```', '').strip()
                    okr_data = json.loads(clean_json)
                    
                    st.session_state['generated_okrs'] = okr_data
                except Exception as e:
                    st.error("Error al procesar los datos. Asegúrate de que el texto sea legible.")

st.divider()

# --- MOSTRAR RESULTADOS ---
if 'generated_okrs' in st.session_state:
    st.subheader(f"Propuesta de OKRs para {role} - {quarter}")
    st.table(st.session_state['generated_okrs'])
    
    excel_file = export_to_excel(st.session_state['generated_okrs'])
    st.download_button(
        label="📥 DESCARGAR EN EXCEL",
        data=excel_file,
        file_name=f"Rappi_OKRs_{role}_{quarter}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
