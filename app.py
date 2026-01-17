import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json
import re

# --- CONFIGURACIÓN ESTILO "PERFORMANCE PORTAL" ---
st.set_page_config(page_title="Performance Management | Rappi", layout="wide")

st.markdown("""
    <style>
    /* Importar fuente profesional */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF;
    }

    /* Título Estilo Google Sites (Limpio y sobrio) */
    .performance-title {
        color: #1F1F1F;
        font-size: 42px;
        font-weight: 600;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
        padding-top: 20px;
    }

    .performance-subtitle {
        color: #70757a;
        font-size: 16px;
        margin-bottom: 40px;
    }

    /* Botón Naranja Rappi (Estilizado) */
    .stButton>button {
        background-color: #FF441F;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #E63D1C;
        box-shadow: 0 4px 12px rgba(255, 68, 31, 0.3);
    }

    /* Inputs Limpios */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #DADCE0 !important;
    }
    
    /* Sidebar minimalista */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def export_to_excel(okr_list):
    df = pd.DataFrame(okr_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OKRs')
    return output.getvalue()

# --- INTERFAZ ---
st.markdown('<h1 class="performance-title">Performance Management</h1>', unsafe_allow_html=True)
st.markdown('<p class="performance-subtitle">OKR Generation Tool for 2026 Strategy Cycle</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown("### Draft your goals")
    user_draft = st.text_area(
        "Borrador de OKR", 
        placeholder="Ej: Asegurar el desarrollo del Talent Pool en Turbo MX...",
        height=300,
        label_visibility="collapsed"
    )

with col_right:
    st.markdown("### Configuration")
    role = st.selectbox("Job Level", ["Assistant", "Analyst", "Specialist", "Lead", "Manager", "Head", "Director", "VP"])
    st.markdown("---")
    generate_btn = st.button("Generate SMART Proposal")

st.divider()

if generate_btn:
    if not user_draft:
        st.warning("Please provide a draft to analyze.")
    else:
        with st.spinner('Processing with Gemini Pro...'):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Act as a Rappi Performance Expert. 
                Refine this draft: "{user_draft}" for a {role} level.
                Return 3 SMART OKRs in a JSON list with: 
                Objective, KR, Metric, Target, Deadline, SMART_Reasoning.
                """
                
                response = model.generate_content(prompt)
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                
                if match:
                    okr_data = json.loads(match.group())
                    st.markdown("### 🚀 Strategic Recommendations")
                    st.table(okr_data)
                    
                    excel_file = export_to_excel(okr_data)
                    st.download_button("📥 Download Excel Report", excel_file, "OKRs_Performance.xlsx")
                else:
                    st.error("Format error. Please try again.")
            except Exception as e:
                st.error("API Connection error.")

# --- SIDEBAR (LOGO AL FINAL) ---
st.sidebar.caption("v2.5 | Confidential & Internal")
st.sidebar.markdown('---')
st.sidebar.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/0/06/Rappi_logo.svg" width="100" style="opacity: 0.8;">', unsafe_allow_html=True)
