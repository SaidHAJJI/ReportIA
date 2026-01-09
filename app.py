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
    /* Style pour le toggle */
    .stCheckbox { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES ARCHIVES ---
if "archives" not in st.session_state:
    st.session_state.archives = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None

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

# --- CONFIGURATION DYNAMIQUE (OPTIMISATION COÛTS) ---
with st.sidebar:
    st.header("⚙️ Paramètres Système")
    
    # Objectif 1 : Toggle Mode Standard vs Élite
    mode_elite = st.toggle("💎 Mode Élite", value=False, help="Désactivé: Flash (Économique) | Activé: Pro (Analytique)")
    
    MODEL_SCOUT = "gemini-1.5-flash"
    if mode_elite:
        MODEL_EXPERT = "gemini-1.5-pro"
        MODEL_EDITOR = "gemini-1.5-pro"
        status_msg = "Performance Maximale (Pro)"
    else:
        MODEL_EXPERT = "gemini-1.5-flash"
        MODEL_EDITOR = "gemini-1.5-flash"
        status_msg = "Économie de Tokens (Flash)"
    
    st.caption(f"Mode actuel : **{status_msg}**")
    st.divider()
    
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
        st.session_state.current_report = None
        st.rerun()

search_tool = types.Tool(google_search=types.GoogleSearch())

# --- MOTEUR D'AGENTS ---
def ask_agent(role_name, instr, prompt, model, langue, use_search=False):
    # Objectif 2 : Directives de concision intégrées systématiquement
    system_prompt = (
        f"Tu es {role_name}. {instr} "
        f"CONSIGNE STRICTE : Sois extrêmement concis et factuel. "
        f"Évite les formules de politesse et le bavardage. "
        f"Utilise des listes à puces. RÉPONDS EN {langue.upper()}."
    )
    
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[search_tool] if use_search else []
    )
    try:
        response = client.models.generate_content(model=model, config=config, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erreur : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("💠 Intelligence Terminal")

# Formulaire de saisie
sujet = st.text_input("", placeholder="Entrez le sujet stratégique...", label_visibility="collapsed")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Orchestration des agents...", expanded=True) as status:
        
        # Agent 1 : Scout (Toujours Flash pour la recherche)
        st.write("🔎 Scan des données sources...")
        intel = ask_agent("Scout", "Cherche des faits récents.", f"Dernières infos sur {sujet}", MODEL_SCOUT, langue, True)
        
        # Agent 2 : Expert (Flash ou Pro selon le Toggle)
        st.write("⚖️ Analyse stratégique...")
        d1 = ask_agent("Expert", "Analyse les implications et risques.", f"Contexte : {intel}", MODEL_EXPERT, langue)
        
        # Agent 3 : Éditeur (Flash ou Pro selon le Toggle)
        st.write("✍️ Génération de l'éditorial...")
        report = ask_agent("Éditeur", "Rédige une synthèse de haut niveau.", f"Sujet: {sujet}\nDonnées: {intel}\nAnalyse: {d1}", MODEL_EDITOR, langue)
        
        # Sauvegarde
        st.session_state.archives.append({"sujet": sujet, "contenu": report, "date": datetime.now()})
        st.session_state.current_report = report
        status.update(label="Analyse terminée", state="complete")

# --- AFFICHAGE DU RAPPORT ACTIF ---
if st.session_state.current_report:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    st.download_button(
        label="📥 EXPORTER LE RAPPORT",
        data=st.session_state.current_report,
        file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )