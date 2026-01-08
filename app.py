import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

st.set_page_config(page_title="Drive Upload Test", page_icon="📤")
st.title("📤 Test de dépôt Drive")

def test_upload():
    try:
        # 1. Chargement des credentials depuis les Secrets
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials)
        
        # 2. Récupération de l'ID du dossier
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")
        
        # 3. Métadonnées du fichier bidon
        file_metadata = {
            'name': 'TEST_PARTAGE_OK.txt',
            'parents': [folder_id] if folder_id else []
        }
        
        # 4. Contenu du fichier
        content = "Bravo ! Le partage du dossier fonctionne. L'application peut maintenant écrire des rapports."
        media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')
        
        # 5. Exécution de l'upload
        st.write(f"🔄 Tentative d'envoi vers le dossier : `{folder_id}`...")
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        
        return f"✅ SUCCÈS ! Fichier créé avec l'ID : {file.get('id')}", True

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