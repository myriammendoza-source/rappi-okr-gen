import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json
import re

# --- ESTILO COMPATIBLE CON GOOGLE SITES ---
st.set_page_config(page_title="Performance Tool", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; } /* Gris muy claro tipo Google */
    .main-title { 
        color: #1a1a1a; 
        font-size: 42px !important; 
        font-weight: 700 !important;
        border-bottom: 2px solid #FF441F;
        padding-bottom: 10px;
    }
    .stButton>button { 
        background-color: #FF441F; 
        color: white; 
        border-radius: 4px; /* Más cuadrado como G-Suite */
        font-weight: 600;
        height: 3em;
    }
    .sidebar-logo { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ... (Mantener la lógica de export_to_excel y Regex que ya tenemos) ...

# HEADER
st.markdown('<h1 class="main-title">Performance: OKR Builder</h1>', unsafe_allow_html=True)
st.write("Alinea tus metas de desarrollo para Turbo MX, Merchants y CPGs según la estrategia 2026.")

# El resto del código de entrada y Gemini (v2.4 robusta)
