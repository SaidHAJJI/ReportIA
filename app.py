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
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("🔑 API KEY", type="password")

if not api_key:
    st.title("💠 Elite Intelligence")
    st.info("Système en attente de clé API...")
    st.stop()

client = genai.Client(api_key=api_key)

# --- CONFIGURATION DES MODES (Objectif 1) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    mode_elite = st.toggle("Mode Élite (Gemini 1.5 Pro)", value=False, help="Activez pour une analyse plus profonde, désactivez pour économiser des tokens.")
    
    # Définition dynamique des modèles
    MODEL_SCOUT = "gemini-1.5-flash"
    if mode_elite:
        MODEL_EXPERT = "gemini-1.5-pro"
        MODEL_EDITOR = "gemini-1.5-pro"
        st.caption("⚡ Mode Élite : Performance maximale")
    else:
        MODEL_EXPERT = "gemini-1.5-flash"
        MODEL_EDITOR = "gemini-1.5-flash"
        st.caption("🔋 Mode Standard : Économie de tokens")

search_tool = types.Tool(google_search=types.GoogleSearch())

# --- MOTEUR D'AGENTS ---
def ask_agent(role_name, instr, prompt, model, langue, use_search=False):
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role_name}. {instr} RÉPONDS EN {langue.upper()}.",
        tools=[search_tool] if use_search else []
    )
    try:
        response = client.models.generate_content(model=model, config=config, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erreur : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("💠 Intelligence Terminal")

with st.sidebar:
    st.header("📂 Archives Récentes")
    if not st.session_state.archives:
        st.write("Aucun rapport.")
    else:
        for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
            if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
                st.session_state.current_report = arc['contenu']
                st.rerun()
    
    st.divider()
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.archives = []
        st.rerun()

# --- FORMULAIRE DE RECHERCHE ---
sujet = st.text_input("", placeholder="Entrez le sujet stratégique...", label_visibility="collapsed")

# Ajout des contraintes de concision (Objectif 2)
CONCISE_RULES = "Sois extrêmement concis, va droit au but, utilise des listes à puces. Évite le bavardage inutile."

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Analyse multi-agents...", expanded=True) as status:
        st.write("🔎 Scan des données...")
        # Scout : Toujours en Flash pour la rapidité
        intel = ask_agent("Scout", f"Cherche des faits. {CONCISE_RULES}", f"Dernières infos sur {sujet}", MODEL_SCOUT, langue, True)
        
        st.write("⚖️ Analyse croisée...")
        d1 = ask_agent("Expert", f"Analyse stratégique. {CONCISE_RULES}", f"Analyse ce contexte: {intel}", MODEL_EXPERT, langue)
        
        st.write("✍️ Rédaction de l'éditorial...")
        report = ask_agent("Éditeur", f"Rédige un éditorial de prestige. {CONCISE_RULES} Structure claire.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {d1}", MODEL_EDITOR, langue)
        
        st.session_state.archives.append({"sujet": sujet, "contenu": report, "date": datetime.now()})
        st.session_state.current_report = report
        status.update(label="Rapport Final Prêt", state="complete")

# --- AFFICHAGE DU RAPPORT ACTIF ---
if "current_report" in st.session_state:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    st.download_button("📥 EXPORTER", st.session_state.current_report, file_name=f"report.md")v