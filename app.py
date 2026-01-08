import streamlit as st
from google import genai
from google.genai import types

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .report-card { 
        background-color: #1a1c24; 
        border-radius: 15px; 
        padding: 25px; 
        border-left: 5px solid #00d4ff; 
        color: #e0e0e0; 
        margin-top: 20px;
        font-family: 'Inter', sans-serif;
    }
    div.stButton > button { 
        background: linear-gradient(45deg, #007bff, #00d4ff); 
        color: white; 
        border-radius: 25px; 
        font-weight: bold; 
        width: 100%;
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION IA ---
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_FLASH = "gemini-1.5-flash"
MODEL_PRO = "gemini-1.5-pro"

def ask_agent(role, instr, prompt, model, langue, search=False):
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role}. {instr} RÉPONDS EN {langue.upper()}.",
        tools=[types.Tool(google_search=types.GoogleSearch())] if search else []
    )
    response = client.models.generate_content(model=model, config=config, contents=prompt)
    return response.text

# --- INTERFACE ---
st.title("💠 Elite Intelligence Terminal")
langue = st.sidebar.selectbox("Langue", ["Français", "Anglais", "Arabe"])
sujet = st.text_input("Sujet stratégique", placeholder="Entrez votre sujet...")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Analyse multi-agents...", expanded=True) as status:
        st.write("🔎 Scout : Analyse des données...")
        # On force search=False pour garantir la stabilité sur Streamlit Cloud
        intel = ask_agent("Scout", "Cherche des faits précis.", sujet, MODEL_FLASH, langue, False)
        
        st.write("⚖️ Expert : Analyse stratégique...")
        analyse = ask_agent("Expert", "Analyse le contexte.", intel, MODEL_PRO, langue)
        
        st.write("✍️ Éditeur : Synthèse de prestige...")
        report = ask_agent("Éditeur", "Rédige l'éditorial final.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {analyse}", MODEL_PRO, langue)
        
        status.update(label="Analyse terminée", state="complete")

    st.markdown(f'<div class="report-card">{report}</div>', unsafe_allow_html=True)