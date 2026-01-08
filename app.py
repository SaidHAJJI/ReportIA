import streamlit as st
from google.oauth2 import service_account

st.title("🔐 Étape 2 : Réparation du Padding")

def get_clean_credentials():
    try:
        # 1. Récupération
        info = dict(st.secrets["gcp_service_account"])
        key = info["private_key"]
        
        # 2. Nettoyage des sauts de ligne
        key = key.replace("\\n", "\n")
        
        # 3. Correction du Padding Base64 (Le secret est ici)
        # On extrait la partie base64 entre les balises BEGIN et END
        if "-----BEGIN PRIVATE KEY-----" in key:
            header = "-----BEGIN PRIVATE KEY-----\n"
            footer = "\n-----END PRIVATE KEY-----"
            content = key.replace(header, "").replace(footer, "").replace("\n", "").strip()
            
            # On répare le padding si nécessaire (doit être multiple de 4)
            missing_padding = len(content) % 4
            if missing_padding:
                content += "=" * (4 - missing_padding)
            
            # On reconstruit la clé propre
            info["private_key"] = header + content + footer
        
        # 4. Tentative d'authentification
        creds = service_account.Credentials.from_service_account_info(info)
        return "✅ Credentials créés avec succès !", creds

    except Exception as e:
        return f"❌ Erreur : {str(e)}", None

# Interface
st.write("Vérifions si on peut transformer le texte des secrets en objet Google utilisable.")

if st.button("TENTER L'AUTHENTIFICATION"):
    msg, credentials = get_clean_credentials()
    if credentials:
        st.success(msg)
        st.balloons()
        st.info("Succès ! La clé est maintenant techniquement parfaite pour Google.")
        st.session_state.creds_ok = True
    else:
        st.error(msg)