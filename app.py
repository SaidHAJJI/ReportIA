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

# --- STYLE CSS AVANCÉ ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .report-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 25px;
        border-left: 5px solid #00d4ff;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        color: #e0e0e0;
        line-height: 1.6;
    }
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        border: none;
        color: white;
        padding: 12px;
        border-radius: 25px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES ARCHIVES ---
if "archives" not in st.session_state:
    st.session_state.archives = []

# --- GESTION DES SECRETS ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("🔑 API KEY", type="password")

if not api_key:
    st.title("💠 Elite Intelligence")
    st.info("Système en attente de clé API...")
    st.stop()

client = genai.Client(api_key=api_key)

# --- MOTEUR D'AGENTS ---
search_tool = types.Tool(google_search=types.GoogleSearch())

def ask_agent(role_name, instr, prompt, model, langue, use_search=False):
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role_name}. {instr} RÉPONDS EN {langue.upper()}.",
        tools=[search_tool] if use_search else []
    )
    try:
        # Tentative d'appel direct
        response = client.models.generate_content(model=model, config=config, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erreur : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("💠 Intelligence Terminal")

with st.sidebar:
    st.header("⚙️ Optimisation")
    mode_elite = st.toggle("🚀 Mode Élite (Gemini Pro)", value=False)
    
    # --- CORRECTION DES IDENTIFIANTS ICI ---
    # Utilisation des strings exactes attendues par le SDK genai
    CURRENT_PRO = "gemini-1.5-pro" if mode_elite else "gemini-1.5-flash"
    CURRENT_FLASH = "gemini-1.5-flash"

    st.divider()
    st.header("📂 Archives Récentes")
    if not st.session_state.archives:
        st.write("Aucun rapport en mémoire.")
    else:
        for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
            if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
                st.session_state.current_report = arc['contenu']
    
    st.divider()
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.archives = []
        st.rerun()

# --- FORMULAIRE DE RECHERCHE ---
sujet = st.text_input("", placeholder="Entrez le sujet stratégique...", label_visibility="collapsed")
if st.button("DÉCRYPTER") and sujet:
    with st.status(f"⚡ Analyse {'Elite' if mode_elite else 'Standard'}...", expanded=True) as status:
        st.write("🔎 Scout : Scan des données...")
        intel = ask_agent("Scout", "Cherche des faits.", f"Dernières infos sur {sujet}", CURRENT_FLASH, langue, True)
        
        st.write("⚖️ Expert : Analyse croisée...")
        d1 = ask_agent("Expert", "Analyse stratégique.", f"Analyse ce contexte: {intel}", CURRENT_PRO, langue)
        
        st.write("✍️ Éditeur : Rédaction...")
        report = ask_agent("Éditeur", "Rédige un éditorial de prestige.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {d1}", CURRENT_PRO, langue)
        
        st.session_state.archives.append({"sujet": sujet, "contenu": report, "date": datetime.now()})
        st.session_state.current_report = report
        status.update(label="Rapport Final Prêt", state="complete")

# --- AFFICHAGE ---
if "current_report" in st.session_state:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    st.download_button("📥 EXPORTER", st.session_state.current_report, file_name=f"report.md")