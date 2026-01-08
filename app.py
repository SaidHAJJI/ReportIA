import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- FONCTION SAUVEGARDE DRIVE ---
def upload_to_drive(content, filename):
    try:
        # Récupération des secrets TOML
        if "gcp_service_account" not in st.secrets:
            st.error("Secret 'gcp_service_account' manquant.")
            return None
            
        drive_creds = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(drive_creds)
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
        st.error(f"Erreur Drive : {str(e)}")
        return None

# --- STYLE CSS PRO ---
st.markdown("""
    <style>
    .report-card { background-color: #1a1c24; border-radius: 15px; padding: 25px; border-left: 5px solid #00d4ff; margin-bottom: 20px; color: #e0e0e0; }
    div.stButton > button:first-child { background: linear-gradient(45deg, #007bff, #00d4ff); border: none; color: white; border-radius: 25px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTIFICATION GEMINI ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.warning("Clé API manquante dans les Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"
search_tool = types.Tool(google_search=types.GoogleSearch())

# --- INTERFACE ---
st.title("💠 Intelligence Terminal")
langue = st.sidebar.selectbox("Langue", ["Français", "Anglais", "Arabe"])
sujet = st.text_input("Sujet stratégique", placeholder="Entrez votre sujet ici...", label_visibility="collapsed")
launch = st.button("DÉCRYPTER")

# --- LOGIQUE D'EXÉCUTION ---
if launch and sujet:
    with st.status("⚡ Analyse en cours...", expanded=True) as status:
        # 1. Scout
        st.write("🔎 Recherche d'infos...")
        config_scout = types.GenerateContentConfig(system_instruction="Tu es un Scout. Trouve des faits.", tools=[search_tool])
        intel = client.models.generate_content(model=MODEL_FLASH, config=config_scout, contents=f"Dernières infos sur {sujet}").text
        
        # 2. Editor
        st.write("✍️ Rédaction de l'éditorial...")
        config_edito = types.GenerateContentConfig(system_instruction=f"Tu es un Éditorialiste de prestige. RÉPONDS EN {langue.upper()}.")
        report = client.models.generate_content(model=MODEL_PRO, config=config_edito, contents=f"Sujet: {sujet}\nIntel: {intel}").text
        
        # 3. Sauvegarde Drive
        st.write("💾 Archivage sur Google Drive...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"INTEL_{sujet.replace(' ', '_')[:15]}_{timestamp}.md"
        drive_id = upload_to_drive(report, filename)
        
        status.update(label="Analyse terminée !", state="complete")

    # Affichage
    st.markdown(f'<div class="report-card">{report}</div>', unsafe_allow_html=True)
    if drive_id:
        st.success(f"✅ Archivé sur Drive (ID: {drive_id})")
    
    st.download_button("📥 Télécharger", report, file_name=filename)
elif launch:
    st.error("Veuillez saisir un sujet.")