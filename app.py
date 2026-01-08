import streamlit as st
from google.oauth2 import service_account

st.set_page_config(page_title="Auth Tester", page_icon="🔑")
st.title("🔑 Testeur de Configuration")

def verify_secrets():
    try:
        # 1. On récupère le dictionnaire des secrets
        if "gcp_service_account" not in st.secrets:
            return "❌ Erreur : La section [gcp_service_account] est absente de vos Secrets Streamlit.", False
            
        info = dict(st.secrets["gcp_service_account"])
        
        # 2. Tentative d'initialisation de l'objet Credentials
        # Si le padding ou le format RSA est mauvais, l'erreur sautera ici
        creds = service_account.Credentials.from_service_account_info(info)
        
        return "✅ Parfait ! Votre clé est valide et reconnue par Python.", True

    except Exception as e:
        return f"❌ Erreur détectée : {str(e)}", False

# Affichage des informations de base (sans montrer la clé privée)
if "gcp_service_account" in st.secrets:
    st.write(f"**Projet détecté :** `{st.secrets['gcp_service_account'].get('project_id')}`")
    st.write(f"**Email détecté :** `{st.secrets['gcp_service_account'].get('client_email')}`")
else:
    st.warning("Aucun secret trouvé. Veuillez configurer les Secrets sur Streamlit Cloud.")

if st.button("VÉRIFIER LA CLÉ MAINTENANT"):
    message, success = verify_secrets()
    if success:
        st.success(message)
        st.balloons()
        st.info("💡 Vous pouvez maintenant réintégrer les fonctions Drive et Gemini en toute confiance.")
    else:
        st.error(message)
        st.warning("Conseil : Assurez-vous d'avoir utilisé les triple guillemets pour la 'private_key' dans les Secrets.")