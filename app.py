import streamlit as st
from datetime import datetime
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

# --- CONFIGURATION ---
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- FONCTION DRIVE ---
def upload_to_drive(content, filename):
    try:
        info = dict(st.secrets["gcp_service_account"])
        # On ne touche pas à la clé si elle est déjà au bon format avec les triple guillemets
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)
        
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")
        file_metadata = {'name': filename, 'parents': [folder_id] if folder_id else []}
        media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/markdown')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.error(f"❌ Erreur Drive : {str(e)}")
        return None

# --- INITIALISATION IA ---
api_key = st.secrets.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# --- INTERFACE ---
st.title("💠 Intelligence Terminal")
langue = st.sidebar.selectbox("Langue", ["Français", "Anglais", "Arabe"])
sujet = st.text_input("Sujet stratégique", placeholder="Entrez votre sujet...")

if st.button("DÉCRYPTER") and sujet:
    with st.status("🧠 Analyse et Archivage...", expanded=True) as status:
        st.write("✍️ Rédaction de l'éditorial...")
        # Appel Gemini (Modèle Flash pour la stabilité)
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Rédige un éditorial de prestige sur : {sujet}. RÉPONDS EN {langue.upper()}."
        )
        report = response.text
        
        st.write("💾 Archivage sur Google Drive...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"REPORT_{timestamp}.md"
        drive_id = upload_to_drive(report, filename)
        
        status.update(label="Opération terminée", state="complete")

    st.markdown(f"--- \n {report}")
    if drive_id:
        st.success(f"✅ Archivé dans Drive ! ID : {drive_id}")