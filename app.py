import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from google import genai
from google.genai import types

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .report-card { background-color: #1a1c24; border-radius: 15px; padding: 25px; border-left: 5px solid #00d4ff; color: #e0e0e0; margin-top: 20px; line-height: 1.6; }
    .stButton > button { border-radius: 25px; font-weight: bold; transition: 0.3s; }
    .main-btn > div > button { background: linear-gradient(45deg, #007bff, #00d4ff); color: white; width: 100%; border: none; padding: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE D'ENVOI EMAIL ---
def send_report_email(content, subject_name):
    try:
        sender = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        receiver = st.secrets["EMAIL_RECEIVER"]

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"💠 ARCHIVE ELITE : {subject_name}"
        
        body = f"Veuillez trouver ci-joint votre rapport stratégique généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}.\n\n---\n\n{content}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur Email : {e}")
        return False

# --- CONFIGURATION AGENTS IA ---
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

# --- INTERFACE UTILISATEUR ---
st.title("💠 Elite Intelligence Terminal")
st.caption("Système d'analyse stratégique multi-agents")

langue = st.sidebar.selectbox("Langue de rédaction", ["Français", "Anglais", "Arabe"])
sujet = st.text_input("Sujet stratégique", placeholder="Ex: L'impact de l'IA sur le marché de l'énergie en 2026...")

if st.button("LANCER L'ANALYSE", key="run_btn", help="Cliquez pour activer les agents") and sujet:
    with st.status("⚡ Cycle d'intelligence en cours...", expanded=True) as status:
        
        st.write("🔎 **Scout** : Scan des données mondiales...")
        intel = ask_agent("Scout", "Cherche des faits précis et récents.", sujet, MODEL_FLASH, langue, True)
        
        st.write("⚖️ **Expert** : Analyse structurelle...")
        analyse = ask_agent("Expert", "Analyse les implications stratégiques de ces données.", intel, MODEL_PRO, langue)
        
        st.write("✍️ **Éditeur** : Synthèse de prestige...")
        report = ask_agent("Éditeur", "Rédige un éditorial de haut niveau (Markdown).", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {analyse}", MODEL_PRO, langue)
        
        status.update(label="Analyse terminée", state="complete")

    # Stockage en session pour l'export
    st.session_state.current_report = report
    st.session_state.current_subject = sujet

# --- AFFICHAGE ET EXPORT ---
if "current_report" in st.session_state:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📥 Options d'Archivage")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.download_button(
            label="💾 TÉLÉCHARGER (Markdown)",
            data=st.session_state.current_report,
            file_name=f"Elite_Report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with c2:
        if st.button("📨 ENVOYER PAR EMAIL", use_container_width=True):
            if send_report_email(st.session_state.current_report, st.session_state.current_subject):
                st.success("Rapport envoyé à votre adresse Gmail !")
                st.balloons()