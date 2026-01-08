import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

# --- CONFIGURATION PAGE ---
st.set_page_config(
    page_title="Elite Intelligence Terminal",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- FONCTION SAUVEGARDE DRIVE ---
def upload_to_drive(content, filename):
    try:
        # On récupère les secrets
        info = dict(st.secrets["gcp_service_account"])
        
        # NETTOYAGE CRUCIAL DU PADDING : 
        # On remplace les doubles backslashes que TOML peut ajouter par des vrais sauts de ligne
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)

        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")

        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else [],
            'mimeType': 'text/markdown'
        }
        media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/markdown')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.sidebar.error(f"❌ Erreur Drive : {str(e)}")
        return None

# --- STYLE CSS ---
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

# --- INITIALISATION ---
if "archives" not in st.session_state:
    st.session_state.archives = []

api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("🔑 Clé API manquante.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"
search_tool = types.Tool(google_search=types.GoogleSearch())

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

# --- INTERFACE ---
st.title("💠 Intelligence Terminal")

with st.sidebar:
    st.header("📂 Archives")
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    if st.session_state.archives:
        for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
            if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
                st.session_state.current_report = arc['contenu']
    if st.button("🗑️ Effacer"):
        st.session_state.archives = []
        st.rerun()

sujet = st.text_input("", placeholder="Entrez le sujet stratégique...", label_visibility="collapsed")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Analyse et Archivage...", expanded=True) as status:
        st.write("🔎 Scan des données...")
        intel = ask_agent("Scout", "Cherche des faits.", f"Dernières infos sur {sujet}", MODEL_FLASH, langue, True)
        
        st.write("⚖️ Analyse croisée...")
        d1 = ask_agent("Expert", "Analyse stratégique.", f"Analyse ce contexte: {intel}", MODEL_PRO, langue)
        
        st.write("✍️ Rédaction de l'éditorial...")
        report = ask_agent("Éditeur", "Rédige un éditorial de prestige.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {d1}", MODEL_PRO, langue)
        
        # SAUVEGARDE DRIVE
        st.write("💾 Archivage sur Google Drive...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"INTEL_{sujet.replace(' ', '_')[:15]}_{timestamp}.md"
        drive_id = upload_to_drive(report, filename)

        st.session_state.archives.append({"sujet": sujet, "contenu": report})
        st.session_state.current_report = report
        
        if drive_id:
            status.update(label=f"✅ Rapport archivé sur Drive", state="complete")
        else:
            status.update(label="⚠️ Rapport généré mais échec Drive", state="error")

if "current_report" in st.session_state:
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    st.download_button("📥 EXPORTER", st.session_state.current_report, file_name=f"report.md")