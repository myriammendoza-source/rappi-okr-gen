import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rappi OKR Builder", layout="wide")

# Estilo Corporativo
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button { background-color: #FF441F; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKR_Export')
    return output.getvalue()

# --- INTERFAZ ---
st.title("Rappi OKR Builder")
st.caption("Estrategia Impulsada por IA")

col1, col2 = st.columns([2, 1])
with col1:
    drive_url = st.text_input("Enlace de Google Drive (Asegúrate que sea público para lectura)", 
                               placeholder="https://docs.google.com/document/d/...")
with col2:
    role = st.selectbox("Tu Rol", ["Individual Contributor", "Manager", "Head / Director", "VP"])

st.divider()

if st.button("Generar OKRs Estratégicos"):
    if not drive_url:
        st.warning("Introduce el link del 6Pager.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Falta API Key en Secrets.")
    else:
        with st.spinner('Gemini está analizando la estrategia...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # EL PROMPT ESTRATÉGICO
                prompt = f"""
                Actúa como un Senior Product Manager en Rappi. Analiza el contenido de este documento: {drive_url}
                Genera entre 3 y 5 OKRs SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
                
                REGLAS OBLIGATORIAS:
                1. Incluye 1 OKR enfocado en Eficiencia mediante AI (Inteligencia Artificial).
                2. Incluye 1 OKR alineado a prioridades de Rappi (Crecimiento, Profitability o Experiencia de Usuario).
                3. Si el rol es '{role}' y es Manager o superior, incluye 1 OKR de eNPS (Employee Net Promoter Score) para el equipo.
                
                Responde EXCLUSIVAMENTE en formato de tabla con estas columnas: Objetivo, KR, Métrica, Meta, Deadline.
                """
                
                response = model.generate_content(prompt)
                
                # Nota: En un entorno productivo real, usaríamos una función para convertir 
                # la respuesta de texto de Gemini a un DataFrame de Pandas. 
                # Por ahora, mostraremos el resultado procesado:
                
                st.subheader("Tu Estrategia Generada")
                st.markdown(response.text)
                
                # Botón de descarga (Simulado con los datos de la respuesta)
                st.info("Copia los resultados anteriores a tu tracker de OKRs.")
                
            except Exception as e:
                st.error("No se pudo leer el documento. Verifica que el link de Drive permita acceso a 'Cualquier persona con el enlace'.")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg", width=100)
