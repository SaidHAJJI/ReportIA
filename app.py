import streamlit as st
from datetime import datetime
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

# Configuration
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- FONCTION DRIVE AVEC NETTOYAGE DE PADDING ---
def upload_to_drive(content, filename):
    try:
        # 1. Extraction et Nettoyage de la clé
        info = dict(st.secrets["gcp_service_account"])
        # On force le remplacement des doubles backslash et on assure les sauts de ligne
        clean_key = info["private_key"].replace("\\n", "\n")
        info["private_key"] = clean_key
        
        # 2. Authentification
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)

        # 3. Métadonnées
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else [],
            'mimeType': 'text/markdown'
        }
        
        # 4. Upload
        media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/markdown')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.error(f"❌ Erreur Drive : {str(e)}")
        return None

# --- STYLE CSS ---
st.markdown("<style>.report-card { background-color: #1a1c24; border-radius: 15px; padding: 25px; border-left: 5px solid #00d4ff; margin-bottom: 20px; }</style>", unsafe_allow_html=True)

# --- LOGIQUE PRINCIPALE ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("Clé API Gemini manquante.")
    st.stop()

client = genai.Client(api_key=api_key)

st.title("💠 Intelligence Terminal")
langue = st.sidebar.selectbox("Langue", ["Français", "Anglais", "Arabe"])
sujet = st.text_input("Sujet stratégique", placeholder="Entrez votre sujet...")
launch = st.button("DÉCRYPTER")

if launch and sujet:
    with st.status("🧠 Analyse et Archivage...", expanded=True) as status:
        # Agent Gemini
        st.write("✍️ Rédaction de l'éditorial...")
        prompt = f"Rédige un éditorial de prestige sur : {sujet}. RÉPONDS EN {langue.upper()}."
        report = client.models.generate_content(model="models/gemini-1.5-pro-latest", contents=prompt).text
        
        # Archivage
        st.write("💾 Envoi vers Google Drive...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"REPORT_{timestamp}.md"
        drive_id = upload_to_drive(report, filename)
        
        status.update(label="Opération terminée", state="complete")

    st.markdown(f'<div class="report-card">{report}</div>', unsafe_allow_html=True)
    if drive_id:
        st.success(f"✅ Archivé dans Drive ! ID : {drive_id}")