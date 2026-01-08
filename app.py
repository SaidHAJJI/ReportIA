import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types

# Configuration de la page
st.set_page_config(page_title="Elite Editorial", page_icon="⚖️", layout="centered")

# --- STYLE CSS POUR MOBILE ---
st.markdown(\"\"\"
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    \"\"\", unsafe_allow_html=True)

st.title("⚖️ Elite Editorial Engine")
st.caption("Moteur d'analyse géopolitique et stratégique multi-agents")

# --- CONFIGURATION API ---
with st.sidebar:
    st.header("🔑 Paramètres")
    api_key = st.text_input("Clé API Gemini", type="password")
    langue = st.selectbox("Langue de rédaction", ["Français", "Anglais", "Arabe"])
    st.divider()
    st.info("Déployé via Streamlit Cloud pour Android.")

if not api_key:
    st.warning("Veuillez entrer votre clé API Gemini dans le menu latéral pour activer les agents.")
    st.stop()

# Initialisation Client
client = genai.Client(api_key=api_key)
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"
search_tool = types.Tool(google_search=types.GoogleSearch())

# --- DICTIONNAIRE DES 9 EXPERTS ---
PERSONNALITES = {
    "scout": {"role": "Le Scout", "model": MODEL_FLASH, "instr": "Cherche les faits récents via Google Search."},
    "expert_legal": {"role": "L'Expert Juridique", "model": MODEL_PRO, "instr": "Analyse le cadre réglementaire."},
    "expert_eco": {"role": "L'Économiste", "model": MODEL_PRO, "instr": "Analyse les impacts financiers."},
    "optimist": {"role": "Le Visionnaire", "model": MODEL_FLASH, "instr": "Défends l'innovation."},
    "skeptic": {"role": "Le Critique", "model": MODEL_FLASH, "instr": "Souligne les risques."},
    "provocateur": {"role": "Le Rédacteur en Chef", "model": MODEL_PRO, "instr": "Identifie une faille logique."},
    "analyst": {"role": "L'Analyste", "model": MODEL_FLASH, "instr": "Calcule la tension du débat (-10 à +10)."},
    "checker": {"role": "Le Fact-Checker", "model": MODEL_FLASH, "instr": "Vérifie les faits via Search."},
    "editor": {"role": "Grand Éditorialiste", "model": MODEL_PRO, "instr": "Rédige une enquête de prestige type Le Monde/NYT."}
}

def ask_agent(agent_key, prompt, use_search=False):
    p = PERSONNALITES[agent_key]
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {p['role']}. {p['instr']} RÉPONDS EXCLUSIVEMENT EN {langue.upper()}.",
        tools=[search_tool] if use_search else []
    )
    return client.models.generate_content(model=p["model"], config=config, contents=prompt).text

# --- INTERFACE DE SAISIE ---
sujet = st.text_input("📝 Sujet de l'analyse :", placeholder="ex: L'avenir de l'énergie nucléaire...")

if st.button("🚀 Lancer l'Analyse Élite"):
    if not sujet:
        st.error("Merci de saisir un sujet.")
    else:
        with st.status("🧠 Les agents collaborent...", expanded=True) as status:
            # Workflow
            st.write("🔎 Intelligence Unit en cours...")
            intel = ask_agent("scout", f"Donne les faits récents sur {sujet}", use_search=True)
            
            st.write("⚖️ Expertise Légale & Éco...")
            leg = ask_agent("expert_legal", f"Enjeux réglementaires : {intel}")
            eco = ask_agent("expert_eco", f"Impact financier : {intel}")
            
            st.write("⚔️ Débat et Provocation...")
            o1 = ask_agent("optimist", f"Opportunités : {intel} {leg} {eco}")
            s1 = ask_agent("skeptic", f"Risques : {o1}")
            angle = ask_agent("provocateur", f"Angle mort : {o1} vs {s1}")
            
            st.write("📊 Analyse de tension...")
            tension = ask_agent("analyst", f"Score de tension : {o1} {s1} {angle}")
            
            st.write("✍️ Rédaction finale...")
            report = ask_agent("editor", f"Rédige l'éditorial final sur {sujet} basé sur : {intel}, {o1}, {s1}, {angle}, {tension}")
            
            status.update(label="Analyse terminée !", state="complete")

        st.markdown("---")
        st.markdown(report)
        st.sidebar.download_button("📥 Télécharger (Markdown)", report, f"rapport_{sujet}.md")
\"\"\"

# --- CRÉATION PHYSIQUE DES FICHIERS (Si exécuté localement) ---
with open("requirements.txt", "w") as f: f.write(requirements)
with open("app.py", "w") as f: f.write(app_code)

print("✅ Fichiers 'app.py' et 'requirements.txt' générés avec succès pour votre dépôt GitHub.")