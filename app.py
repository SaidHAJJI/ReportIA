import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Elite Editorial Engine", page_icon="⚖️", layout="centered")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Elite Editorial Engine")
st.caption("Analyse stratégique multi-agents (FR / EN / AR)")

# --- GESTION DES SECRETS / API KEY ---
# Priorité au secret Streamlit, sinon demande saisie utilisateur
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if not api_key:
    st.info("Veuillez configurer la GOOGLE_API_KEY dans les Secrets ou la saisir à gauche.")
    st.stop()

# Initialisation du client
client = genai.Client(api_key=api_key)
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"
search_tool = types.Tool(google_search=types.GoogleSearch())

# --- DICTIONNAIRE DES AGENTS ---
PERSONNALITES = {
    "scout": {"role": "Le Scout", "model": MODEL_FLASH, "instr": "Cherche les faits récents via Google Search."},
    "expert_legal": {"role": "L'Expert Juridique", "model": MODEL_PRO, "instr": "Analyse le cadre réglementaire."},
    "expert_eco": {"role": "L'Économiste", "model": MODEL_PRO, "instr": "Analyse les impacts financiers."},
    "optimist": {"role": "Le Visionnaire", "model": MODEL_FLASH, "instr": "Défends l'innovation."},
    "skeptic": {"role": "Le Critique", "model": MODEL_FLASH, "instr": "Souligne les risques."},
    "provocateur": {"role": "Le Rédacteur en Chef", "model": MODEL_PRO, "instr": "Identifie une faille logique."},
    "analyst": {"role": "L'Analyste", "model": MODEL_FLASH, "instr": "Calcule la tension du débat (-10 à +10)."},
    "editor": {"role": "Grand Éditorialiste", "model": MODEL_PRO, "instr": "Rédige une enquête premium type Le Monde/NYT/Al Jazeera."}
}

def ask_agent(agent_key, prompt, langue, use_search=False):
    p = PERSONNALITES[agent_key]
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {p['role']}. {p['instr']} RÉPONDS EXCLUSIVEMENT EN {langue.upper()}.",
        tools=[search_tool] if use_search else []
    )
    return client.models.generate_content(model=p["model"], config=config, contents=prompt).text

# --- INTERFACE UTILISATEUR ---
with st.sidebar:
    st.header("🌍 Options")
    langue_choisie = st.selectbox("Langue du rapport", ["Français", "Anglais", "Arabe"])
    st.divider()

sujet = st.text_input("📝 Sujet de l'analyse :", placeholder="ex: La crise de l'eau au Moyen-Orient...")

if st.button("🚀 Lancer l'Analyse Élite"):
    if not sujet:
        st.error("Veuillez entrer un sujet.")
    else:
        with st.status("🧠 Les agents collaborent...", expanded=True) as status:
            st.write("🔎 Recherche d'informations...")
            intel = ask_agent("scout", f"Donne les faits récents sur {sujet}", langue_choisie, use_search=True)
            
            st.write("⚖️ Expertise Légale & Éco...")
            leg = ask_agent("expert_legal", f"Enjeux réglementaires : {intel}", langue_choisie)
            eco = ask_agent("expert_eco", f"Impact financier : {intel}", langue_choisie)
            
            st.write("⚔️ Duel et Provocation...")
            o1 = ask_agent("optimist", f"Opportunités : {intel}", langue_choisie)
            s1 = ask_agent("skeptic", f"Risques : {o1}", langue_choisie)
            angle = ask_agent("provocateur", f"Angle mort : {o1} vs {s1}", langue_choisie)
            
            st.write("📊 Analyse de tension...")
            tension = ask_agent("analyst", f"Score de tension : {o1} {s1}", langue_choisie)
            
            st.write("✍️ Rédaction de l'éditorial...")
            final_input = f"Sujet: {sujet}\nIntel: {intel}\nLégal: {leg}\nÉco: {eco}\nDébat: {o1} vs {s1}\nAngle: {angle}\nTension: {tension}"
            report = ask_agent("editor", f"Rédige l'éditorial final : {final_input}", langue_choisie)
            
            status.update(label="Analyse terminée !", state="complete")

        st.markdown("---")
        st.markdown(report)
        st.download_button("📥 Télécharger le rapport", report, file_name=f"rapport_{sujet}.md")