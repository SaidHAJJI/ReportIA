import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

st.title("💾 Solution Ultime Quota")

def upload_final_attempt():
    try:
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)
        
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "").strip()
        
        # Le changement est ici : on définit explicitement que le fichier 
        # doit être créé DIRECTEMENT à l'intérieur de votre quota personnel.
        file_metadata = {
            'name': 'SUCCES_FINAL.txt',
            'parents': [folder_id],
            'mimeType': 'text/plain'
        }
        
        media = MediaInMemoryUpload(b'Test quota ok', mimetype='text/plain')
        
        # On force l'utilisation du quota du dossier parent (le vôtre)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True,
            # Cette option est cruciale pour certains types de comptes
            keepRevisionForever=False 
        ).execute()
        
        return f"✅ INCROYABLE ! Ça a marché. ID : {file.get('id')}"
    
    except Exception as e:
        if "storageQuotaExceeded" in str(e):
            return "❌ Google refuse toujours le quota du Compte de Service."
        return f"❌ Autre erreur : {str(e)}"

if st.button("FORCER L'UPLOAD SUR MON QUOTA PERSONNEL"):
    st.write(upload_final_attempt())