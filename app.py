import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from google import genai
from google.genai import types

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .report-card { background-color: #1a1c24; border-radius: 15px; padding: 25px; border-left: 5px solid #00d4ff; color: #e0e0e0; margin-top: 20px; }
    div.stButton > button { border-radius: 25px; font-weight: bold; width: 100%; }
    .btn-run { background: linear-gradient(45deg, #007bff, #00d4ff) !important; color: white !important; border: none !important; padding: 10px !important; }
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
        st.error(f"Erreur d'envoi Email : {e}")
        return False

# --- CONFIGURATION IA ---
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_FLASH = "gemini-1.5-flash"
MODEL_PRO = "gemini-1.5-pro"

def ask_agent(role, instr, prompt, model, langue, search=False):
    # La fonction reste identique, on ne la touche pas.
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

if st.button("DÉCRYPTER", key="run_btn") and sujet:
    with st.status("⚡ Analyse multi-agents en cours...", expanded=True) as status:
        st.write("🔎 Scout : Analyse des données...")
        
        # 'search' à False pour la stabilité
        intel = ask_agent("Scout", "Cherche des faits précis.", sujet, MODEL_FLASH, langue, False)
        
        st.write("⚖️ Expert : Analyse stratégique...")
        analyse = ask_agent("Expert", "Analyse le contexte.", intel, MODEL_PRO, langue)
        
        st.write("✍️ Éditeur : Synthèse de prestige...")
        report = ask_agent("Éditeur", "Rédige l'éditorial final.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {analyse}", MODEL_PRO, langue)
        
        st.session_state.last_report = report
        st.session_state.last_subject = sujet
        status.update(label="Analyse terminée", state="complete")

# --- ZONE D'EXPORTATION ---
if "last_report" in st.session_state:
    st.markdown(f'<div class="report-card">{st.session_state.last_report}</div>', unsafe_allow_html=True)
    st.write("---")
    st.subheader("📥 Archivage du rapport")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("💾 TÉLÉCHARGER (.MD)", data=st.session_state.last_report, file_name="Elite_Report.md", mime="text/markdown")
    with col2:
        if st.button("📨 ENVOYER PAR EMAIL"):
            if send_email(st.session_state.last_report, st.session_state.last_subject):
                st.success("Rapport envoyé !")
                st.balloons()