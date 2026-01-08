import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types

# --- CONFIGURATION PRE-REQUIS ---
st.set_page_config(
    page_title="Elite Intelligence Terminal",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DESIGN "PRO" (CSS INJECTÉ) ---
st.markdown("""
    <style>
    /* Fond et conteneur principal */
    .main { background-color: #0e1117; }
    
    /* Cartes de rapport */
    .report-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 25px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Bouton personnalisé */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        border: none;
        color: white;
        padding: 15px 30px;
        border-radius: 30px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,212,255,0.4);
    }
    
    /* Titres */
    h1 { color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; }
    h3 { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE BACKEND ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("🔑 API KEY", type="password")

if not api_key:
    st.title("💠 Elite Intelligence")
    st.info("Système en attente de clé API...")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"
search_tool = types.Tool(google_search=types.GoogleSearch())

PERSONNALITES = {
    "scout": {"role": "Intelligence Unit", "model": MODEL_FLASH, "instr": "Recherche de données factuelles."},
    "neocon": {"role": "Strategic Hawk", "model": MODEL_PRO, "instr": "Analyse de puissance et souveraineté."},
    "liberal": {"role": "Diplomatic Unit", "model": MODEL_PRO, "instr": "Analyse éthique et multilatérale."},
    "realpolitik": {"role": "Realpolitik Analyst", "model": MODEL_PRO, "instr": "Analyse froide des flux et forces."},
    "editor": {"role": "Chief Editor", "model": MODEL_PRO, "instr": "Éditorialiste de prestige."}
}

def ask_agent(agent_key, prompt, langue):
    p = PERSONNALITES[agent_key]
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {p['role']}. {p['instr']} RÉPONDS EXCLUSIVEMENT EN {langue.upper()}.",
        tools=[search_tool] if agent_key == "scout" else []
    )
    try:
        response = client.models.generate_content(model=p["model"], config=config, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erreur Agent {agent_key}: {str(e)}"

# --- INTERFACE UTILISATEUR MOBILE ---
st.title("💠 Intelligence Terminal")
st.caption("Système multi-agents de haute précision")

with st.container():
    sujet = st.text_input("", placeholder="Entrez le sujet stratégique...", label_visibility="collapsed")
    langue = st.selectbox("Langue cible", ["Français", "Anglais", "Arabe"], label_visibility="collapsed")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        launch = st.button("DÉCRYPTER")

if launch and sujet:
    with st.status("⚡ Acquisition & Analyse...", expanded=True) as status:
        st.write("🛰️ Scan satellite des données...")
        intel = ask_agent("scout", f"Dernières dépêches critiques sur : {sujet}", langue)
        
        st.write("⚔️ Confrontation des doctrines...")
        d1 = ask_agent("neocon", f"Contexte : {intel}", langue)
        d2 = ask_agent("liberal", f"Contexte : {intel}", langue)
        d3 = ask_agent("realpolitik", f"Contexte : {intel}", langue)
        
        st.write("✍️ Synthèse éditoriale...")
        final_input = f"Sujet: {sujet}\nIntel: {intel}\nDébats: {d1}, {d2}, {d3}"
        report = ask_agent("editor", f"Rédige un éditorial magistral : {final_input}", langue)
        
        status.update(label="Rapport Final Prêt", state="complete")

    # Affichage façon "App Pro"
    st.markdown(f'<div class="report-card">{report}</div>', unsafe_allow_html=True)
    
    # Bouton de téléchargement
    st.download_button("📥 EXPORTER LE DOSSIER", report, file_name=f"intel_{datetime.now().strftime('%Y%m%d')}.md")

elif launch:
    st.error("Veuillez saisir un sujet valide.")