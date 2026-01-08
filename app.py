import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account

st.set_page_config(page_title="Step 1: Auth Check", page_icon="🔑")

st.title("🔑 Étape 1 : Validation de l'accès Drive")

def check_auth():
    try:
        # 1. Chargement des secrets
        info = dict(st.secrets["gcp_service_account"])
        
        # 2. Nettoyage de la clé (Indispensable avec le format guillemets simples)
        # On transforme la chaîne '\n' en un vrai saut de ligne Python
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        # 3. Initialisation des identifiants
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        
        # 4. Test simple : Lister le contenu du dossier cible
        folder_id = st.secrets.get("DRIVE_FOLDER_ID")
        query = f"'{folder_id}' in parents and trashed = false"
        
        results = service.files().list(
            q=query, 
            fields="files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            return "✅ Connexion réussie, mais le dossier est vide."
        else:
            names = [f["name"] for f in items]
            return f"✅ Connexion réussie ! Fichiers trouvés : {', '.join(names)}"

    except Exception as e:
        return f"❌ Erreur d'authentification : {str(e)}"

# Interface de test
st.write("Cliquons sur le bouton pour vérifier si la clé est valide et si le dossier est accessible.")

if st.button("VÉRIFIER LA CONNEXION"):
    with st.spinner("Vérification en cours..."):
        message = check_auth()
        if "✅" in message:
            st.success(message)
            st.balloons()
            st.info("Prochaine étape : Nous allons réintégrer la fonction d'écriture (Upload).")
        else:
            st.error(message)
            st.write("**Conseils de dépannage :**")
            if "padding" in message.lower():
                st.write("- Le remplacement du `\\n` a échoué. Vérifiez la syntaxe dans `app.py`.")
            if "permission" in message.lower() or "404" in message.lower():
                st.write("- L'email du compte de service n'a pas accès au dossier. Vérifiez le partage dans Google Drive.")