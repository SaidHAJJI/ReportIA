import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

# --- FONCTION DE SAUVEGARDE DRIVE ---
def upload_to_drive(content, filename):
    try:
        # On récupère les infos du compte de service depuis les Secrets
        drive_creds = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(drive_creds)
        service = build('drive', 'v3', credentials=credentials)

        # ID du dossier partagé (à mettre dans vos secrets)
        folder_id = st.secrets["DRIVE_FOLDER_ID"]

        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'text/markdown'
        }
        media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/markdown')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.error(f"Erreur Drive : {str(e)}")
        return None

# --- DANS VOTRE BLOC D'EXÉCUTION (après la génération du rapport) ---
if launch and sujet:
    # ... (votre logique d'agents existante) ...
    
    # Sauvegarde automatique sur Drive
    filename = f"INTEL_{sujet.replace(' ', '_')[:15]}_{datetime.now().strftime('%Y%m%d')}.md"
    drive_id = upload_to_drive(report, filename)
    
    if drive_id:
        st.success(f"✅ Rapport archivé sur Google Drive (ID: {drive_id})")