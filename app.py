import streamlit as st

st.title("🛠️ Diagnostic d'Interface")

# 1. Vérification des Imports de base
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    st.success("✅ Bibliothèques Google installées.")
except ImportError as e:
    st.error(f"❌ Bibliothèques manquantes : {e}")
    st.info("Vérifiez que 'google-api-python-client' et 'google-auth' sont dans requirements.txt")

# 2. Vérification de la lecture des Secrets
st.write("---")
st.subheader("Lecture des Secrets")

if "gcp_service_account" in st.secrets:
    st.success("✅ Section [gcp_service_account] trouvée.")
    try:
        key = st.secrets["gcp_service_account"]["private_key"]
        st.write(f"Aperçu de la clé : `{key[:20]}...`")
        
        # Test du padding manuel
        if "\\n" in key:
            st.info("Note : La clé contient des '\\n' textuels (format attendu).")
        else:
            st.warning("Note : La clé ne contient pas de '\\n'.")
            
    except Exception as e:
        st.error(f"Erreur de lecture de la clé : {e}")
else:
    st.error("❌ Section [gcp_service_account] INTROUVABLE dans les Secrets.")

# 3. Bouton de test simple
if st.button("Lancer un test de texte brut"):
    st.write("Le bouton fonctionne, l'interface n'est pas figée.")