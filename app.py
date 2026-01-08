import streamlit as st
from google.oauth2 import service_account
import re

st.title("🔐 Étape 4 : Validation Structurelle RSA")

def get_clean_credentials():
    try:
        info = dict(st.secrets["gcp_service_account"])
        raw_key = info["private_key"]
        
        # 1. Extraction pure de la data (on vire tout ce qui n'est pas Base64)
        # On cherche uniquement les caractères de la clé
        content = re.sub(r'[^A-Za-z0-9+/]', '', raw_key)
        
        # 2. Correction du padding (doit être multiple de 4)
        # Si la longueur % 4 == 1, le copier-coller a ajouté un caractère parasite à la fin
        if len(content) % 4 == 1:
            content = content[:-1]
        while len(content) % 4 != 0:
            content += "="

        # 3. Reconstruction STRICTE au format PEM (Sauts de ligne tous les 64 caractères)
        # C'est ce format que la bibliothèque RSA attend
        formatted_key = "-----BEGIN PRIVATE KEY-----\n"
        for i in range(0, len(content), 64):
            formatted_key += content[i:i+64] + "\n"
        formatted_key += "-----END PRIVATE KEY-----\n"
        
        info["private_key"] = formatted_key
        
        # 4. Test final
        creds = service_account.Credentials.from_service_account_info(info)
        return "✅ CLÉ VALIDÉE ET RECONSTRUITE !", creds

    except Exception as e:
        return f"❌ Erreur structurelle : {str(e)}", None

st.write("Nous reconstruisons maintenant les sauts de ligne RSA officiels (64 chars).")

if st.button("RECONSTRUIRE ET VALIDER"):
    msg, credentials = get_clean_credentials()
    if credentials:
        st.success(msg)
        st.balloons()
        st.write("---")
        st.subheader("🚀 Code Final Prêt")
        st.info("La clé est valide. Vous pouvez maintenant remettre votre code complet (Agents + Drive) en utilisant cette logique de nettoyage.")
    else:
        st.error("La clé est toujours corrompue au niveau binaire.")
        st.warning("Si cette étape échoue, la seule solution est de générer une NOUVELLE CLÉ JSON dans la console Google Cloud, car celle-ci a perdu trop de données.")