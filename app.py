import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

st.set_page_config(page_title="Test Final Drive", page_icon="💾")
st.title("💾 Test de Sauvegarde (Sans Agents)")

def upload_test_file():
    try:
        # 1. Authentification
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)
        
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")
        
        # 2. Métadonnées du fichier
        file_metadata = {
            'name': 'TEST_QUOTA_REUSSI.txt',
            'parents': [folder_id] if folder_id else []
        }
        
        # 3. Contenu
        content = "Si ce fichier est là, le problème de quota est résolu !"
        media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')
        
        # 4. Envoi avec les options de forçage de quota
        st.write(f"Tentative d'envoi vers : `{folder_id}`")
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True  # Autorise l'utilisation du stockage partagé
        ).execute()
        
        return f"✅ SUCCÈS ! ID du fichier : {file.get('id')}", True

    except Exception as e:
        return f"❌ ERREUR : {str(e)}", False

# --- Interface ---
st.write("Ce bouton teste uniquement la connexion et le quota du dossier Drive.")

if st.button("TESTER LA SAUVEGARDE"):
    message, success = upload_test_file()
    if success:
        st.success(message)
        st.balloons()
    else:
        st.error(message)
        st.info("""
        **Si l'erreur de quota persiste :**
        Allez sur Google Drive, faites un clic droit sur votre dossier, et vérifiez que l'email du compte de service est bien 'Éditeur'. 
        Si c'est déjà le cas, essayez de créer un **nouveau dossier vide** et de changer l'ID dans vos Secrets.
        """)