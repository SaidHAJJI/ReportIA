import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

st.set_page_config(page_title="Drive Upload Test", page_icon="📤")
st.title("📤 Test de dépôt Drive")

def test_upload():
    try:
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)
        
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")
        
        file_metadata = {
            'name': 'TEST_FINAL_QUOTA.txt',
            'parents': [folder_id] # C'est cette ligne qui utilise VOTRE quota
        }
        
        # On utilise un média très léger
        media = MediaInMemoryUpload("Test réussi !".encode('utf-8'), mimetype='text/plain')
        
        # IMPORTANT : On ajoute supportsAllDrives=True pour autoriser le compte de service
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True # Option de sécurité pour les comptes de service
        ).execute()
        
        return f"✅ ENFIN ! Fichier créé : {file.get('id')}", True
    except Exception as e:
        return f"❌ ERREUR : {str(e)}", False
# Interface
st.write("Ce test va créer un petit fichier texte dans votre dossier Drive.")

if st.button("LANCER LE TEST D'ÉCRITURE"):
    message, success = test_upload()
    if success:
        st.success(message)
        st.balloons()
        st.info("Tout est prêt ! Vous pouvez maintenant utiliser l'application Elite Intelligence complète.")
    else:
        st.error(message)
        if "404" in message:
            st.warning("Diagnostic : Le dossier est introuvable ou le compte de service n'a pas l'accès 'Éditeur'.")
        elif "permission" in message.lower():
            st.warning("Diagnostic : Problème de droits. Vérifiez le partage du dossier dans Google Drive.")