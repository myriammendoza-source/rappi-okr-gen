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
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; font-weight: bold; height: 3em; }
    .main-title { color: #FF441F; font-size: 35px; font-weight: bold; }
    .draft-box { border: 1px solid #FF441F; padding: 15px; border-radius: 10px; background-color: #FFF9F8; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Propuesta_OKRs')
    return output.getvalue()

# --- HEADER ---
st.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="100">', unsafe_allow_html=True)
st.markdown('<p class="main-title">Rappi OKR Generator</p>', unsafe_allow_html=True)
st.write("Optimiza tus OKRs basados en documentación estratégica y tu rol actual.")

# --- INTERFAZ DE ENTRADA ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("1. Contexto Estratégico")
    context_text = st.text_area(
        "Pega aquí 6Pagers, Estrategia Rappi o OKRs de tu Jefe:", 
        height=250, 
        placeholder="Ej: El objetivo del Q3 es reducir el CPO en un 15% mediante optimización de rutas..."
    )
    
    st.subheader("2. Tu Borrador de OKR")
    user_draft = st.text_area(
        "¿Qué tienes en mente?", 
        placeholder="Ej: Quiero mejorar el tiempo de entrega en la ciudad de Bogotá.",
        height=100
    )

with col2:
    st.subheader("Configuración")
    role = st.selectbox("Nivel del Rol", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    
    st.info("""
    **Instrucciones:**
    1. Define tu rol.
    2. Pega el contexto de Rappi.
    3. Escribe una idea general (Borrador).
    4. Haz clic en 'Optimizar OKR'.
    """)
    
    generate_btn = st.button("OPTIMIZAR HACIA SMART")

st.divider()

# --- LÓGICA DE IA ---
if generate_btn:
    if not user_draft:
        st.warning("Por favor, ingresa al menos un borrador para trabajar.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Configuración de API faltante.")
    else:
        with st.spinner('Analizando y refinando tus OKRs...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Eres un Senior Strategy Manager en Rappi. Tu tarea es convertir un borrador de OKR en una versión SMART de alto nivel.
                
                CONTEXTO ESTRATÉGICO: {context_text}
                BORRADOR DEL USUARIO: {user_draft}
                NIVEL DEL ROL: {role}
                
                INSTRUCCIONES:
                1. Analiza el borrador.
                2. Genera 3 sugerencias que sigan el formato SMART (Específico, Medible, Alcanzable, Relevante, Temporal).
                3. Asegúrate que las metas sean agresivas (estilo Rappi) pero realistas para un {role}.
                4. Incluye siempre una columna de 'Por qué es SMART' explicando la mejora.
                
                Responde EXCLUSIVAMENTE en formato JSON plano (lista de objetos) con estas llaves:
                "Objetivo", "KR", "Métrica", "Meta", "Deadline", "Explicacion_SMART".
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                okr_data = json.loads(clean_json)
                
                st.subheader("🚀 Sugerencias de OKRs SMART")
                st.table(okr_data)
                
                # Exportación
                excel_file = export_to_excel(okr_data)
                st.download_button("📥 Descargar Sugerencias en Excel", excel_file, "Sugerencias_OKRs_Rappi.xlsx")
                
            except Exception as e:
                st.error("Error al procesar. Verifica que el texto pegado no sea demasiado corto.")

st.sidebar.caption("v2.1 | Secure Internal Tool")
