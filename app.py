import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

st.set_page_config(page_title="Debug Drive", page_icon="🛠️")

st.title("🛠️ Test de Connexion Google Drive")

def test_upload():
    try:
        # 1. Récupération brute des secrets
        info = dict(st.secrets["gcp_service_account"])
        
        # 2. Correction manuelle du padding / sauts de ligne
        # C'est ici que l'erreur "Incorrect Padding" se joue
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        # 3. Tentative d'authentification
        st.write("🔄 Tentative d'authentification...")
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        
        # 4. Préparation d'un fichier bidon
        folder_id = st.secrets.get("DRIVE_FOLDER_ID", "")
        file_metadata = {
            'name': 'TEST_CONNEXION.txt',
            'parents': [folder_id] if folder_id else []
        }
        media = MediaInMemoryUpload("Connexion réussie depuis Streamlit !", mimetype='text/plain')
        
        # 5. Envoi
        st.write("📤 Envoi du fichier de test...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        return f"✅ SUCCÈS ! Fichier créé avec l'ID : {file.get('id')}"
    
    except Exception as e:
        return f"❌ ÉCHEC : {str(e)}"

# Interface de test
st.info(f"Dossier cible : `{st.secrets.get('DRIVE_FOLDER_ID')}`")
st.write(f"Email du compte de service : `{st.secrets['gcp_service_account']['client_email']}`")

if st.button("LANCER LE TEST D'ENVOI"):
    resultat = test_upload()
    st.markdown(f"### Résultat du diagnostic :\n{resultat}")

if "ÉCHEC" in locals() or "resultat" in locals() and "Incorrect padding" in resultat:
    st.error("L'erreur 'Incorrect padding' persiste.")
    st.write("""
    **Vérifications à faire :**
    1. Dans vos Secrets, assurez-vous que la clé commence par `'-----BEGIN PRIVATE KEY-----\\n` et finit par `\\n-----END PRIVATE KEY-----\\n'`.
    2. Vérifiez qu'il n'y a pas d'espace caché à la fin de la chaîne de caractères dans l'interface Streamlit.
    """)