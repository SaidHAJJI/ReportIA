import streamlit as st
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# --- FONCTION EMAIL ---
def send_email(content, subject_text):
    try:
        sender = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        receiver = st.secrets["EMAIL_RECEIVER"]
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"💠 ARCHIVE ELITE : {subject_text}"
        msg.attach(MIMEText(content, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur Email : {e}")
        return False

# --- INITIALISATION DES ARCHIVES ---
if "archives" not in st.session_state:
    st.session_state.archives = []

# --- GESTION DES SECRETS ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.title("💠 Elite Intelligence")
    st.info("Système en attente de clé API...")
    st.stop()

client = genai.Client(api_key=api_key)
# Utilisation des noms de modèles standards pour éviter les erreurs de version
MODEL_FLASH = "gemini-1.5-flash"
MODEL_PRO = "gemini-1.5-pro"

# --- MOTEUR D'AGENTS ---
def ask_agent(role_name, instr, prompt, model, langue, use_search=False):
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role_name}. {instr} RÉPONDS EN {langue.upper()}.",
        tools=[types.Tool(google_search=types.GoogleSearch())] if use_search else []
    )
    response = client.models.generate_content(model=model, config=config, contents=prompt)
    return response.text

# --- INTERFACE PRINCIPALE ---
st.title("💠 Intelligence Terminal")

with st.sidebar:
    st.header("📂 Archives")
    for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
        if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
            st.session_state.current_report = arc['contenu']
            st.session_state.current_subject = arc['sujet']
    
    st.divider()
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    if st.button("🗑️ Effacer"):
        st.session_state.archives = []
        st.rerun()

sujet = st.text_input("", placeholder="Entrez le sujet stratégique...", label_visibility="collapsed")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Analyse multi-agents...", expanded=True) as status:
        st.write("🔎 Scout...")
        # Note: Garder search=False si Streamlit Cloud bloque encore la recherche
        intel = ask_agent("Scout", "Cherche des faits.", sujet, MODEL_FLASH, langue, False)
        st.write("⚖️ Expert...")
        d1 = ask_agent("Expert", "Analyse stratégique.", intel, MODEL_PRO, langue)
        st.write("✍️ Éditeur...")
        report = ask_agent("Éditeur", "Rédige un éditorial.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {d1}", MODEL_PRO, langue)
        
        st.session_state.archives.append({"sujet": sujet, "contenu": report})
        st.session_state.current_report = report
        st.session_state.current_subject = sujet
        status.update(label="Prêt", state="complete")

# --- AFFICHAGE ET EXPORT ---
if "current_report" in st.session_state:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 EXPORTER", st.session_state.current_report, file_name="report.md")
    with col2:
        if st.button("📧 ENVOYER PAR EMAIL"):
            if send_email(st.session_state.current_report, st.session_state.current_subject):
                st.success("Email envoyé !")