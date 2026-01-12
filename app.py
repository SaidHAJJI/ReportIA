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
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "last_sujet" not in st.session_state:
    st.session_state.last_sujet = "rapport"

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

# --- CONFIGURATION DES MODES ---
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"

with st.sidebar:
    st.header("⚙️ Paramètres")
    mode_elite = st.toggle("💎 Mode Élite", value=False)
    
    active_scout_model = MODEL_FLASH
    if mode_elite:
        active_expert_model = MODEL_PRO
        active_editor_model = MODEL_PRO
    else:
        active_expert_model = MODEL_FLASH
        active_editor_model = MODEL_FLASH

    st.divider()
    st.header("📂 Archives Récentes")
    if st.session_state.archives:
        for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
            if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
                st.session_state.current_report = arc['contenu']
                st.session_state.last_sujet = arc['sujet']
                st.rerun()
    
    st.divider()
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.archives = []
        st.session_state.current_report = None
        st.rerun()

search_tool = types.Tool(google_search=types.GoogleSearch())

# --- MOTEUR D'AGENTS ---
def ask_agent(role_name, instr, prompt, model, langue, use_search=False):
    detail_instr = (
        "Fournis une réponse riche, structurée et approfondie. "
        "Développe chaque point avec précision et nuance."
    )
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role_name}. {detail_instr} {instr} RÉPONDS EN {langue.upper()}.",
        tools=[search_tool] if use_search else []
    )
    try:
        response = client.models.generate_content(model=model, config=config, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erreur : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("💠 Intelligence Terminal")

sujet = st.text_input("", placeholder="Sujet stratégique...", label_visibility="collapsed")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Orchestration...", expanded=True) as status:
        intel = ask_agent("Scout", "Faits exhaustifs.", f"Infos sur {sujet}", active_scout_model, langue, True)
        d1 = ask_agent("Expert", "Analyse détaillée.", f"Context: {intel}", active_expert_model, langue)
        
        st.write("⏳ Temporisation de sécurité (1 min)...")
        p_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.6)
            p_bar.progress(i + 1)
            
        report = ask_agent("Éditeur", "Éditorial complet.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {d1}", active_editor_model, langue)
        
        st.session_state.archives.append({"sujet": sujet, "contenu": report})
        st.session_state.current_report = report
        st.session_state.last_sujet = sujet
        status.update(label="Terminé", state="complete")

# --- AFFICHAGE ET EXPORT ---
if st.session_state.current_report:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    
    # Nom de fichier dynamique pour faciliter le rangement sur Drive
    clean_name = "".join([c for c in st.session_state.last_sujet if c.isalnum() or c==' ']).rstrip()
    filename = f"INTEL_{clean_name}_{datetime.now().strftime('%d-%m-%y')}.md"
    
    st.download_button(
        label="📥 CHOISIR EMPLACEMENT & SAUVEGARDER",
        data=st.session_state.current_report,
        file_name=filename,
        mime="text/markdown",
        help="Cliquez pour ouvrir la fenêtre de sélection de dossier de votre système."
    )