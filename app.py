import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

st.title("💾 Test Drive : Solution Quota")

def upload_fix():
    try:
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)
        
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "").strip()
        
        # On crée un fichier SANS corps de texte d'abord pour tester
        file_metadata = {
            'name': 'SUCCES_QUOTA.txt',
            'parents': [folder_id]
        }
        
        # On utilise le média le plus simple possible
        media = MediaInMemoryUpload(b'OK', mimetype='text/plain')
        
        # Le secret : on ne demande QUE l'ID en retour
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            # On active ces deux options pour les comptes de service
            supportsAllDrives=True,
            ignoreDefaultVisibility=True 
        ).execute()
        
        return f"✅ ENFIN ! ID : {file.get('id')}"
    except Exception as e:
        return f"❌ {str(e)}"

if st.button("TENTER L'UPLOAD FINAL"):
    st.write(upload_fix())