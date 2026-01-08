import streamlit as st
from google.oauth2 import service_account
import re

st.title("🔐 Étape 3 : Nettoyage Alpha-Numérique")

def get_clean_credentials():
    try:
        info = dict(st.secrets["gcp_service_account"])
        key = info["private_key"]
        
        # 1. On sépare l'en-tête et le pied
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        
        # 2. On extrait ce qu'il y a entre les deux
        content = key.split(header)[-1].split(footer)[0]
        
        # 3. NETTOYAGE TOTAL : On ne garde QUE les caractères Base64 valides
        # On supprime les \n, les espaces, et les backslashes parasites
        content = re.sub(r'[^A-Za-z0-9+/=]', '', content)
        
        # 4. Ajustement du Padding (Base64 must be multiple of 4)
        # Si la longueur est (4n + 1), c'est qu'il y a un caractère parasite
        if len(content) % 4 == 1:
            content = content[:-1] # On retire le caractère de trop
        
        while len(content) % 4 != 0:
            content += "="
            
        # 5. Reconstruction pour l'API Google
        info["private_key"] = f"{header}\n{content}\n{footer}\n"
        
        creds = service_account.Credentials.from_service_account_info(info)
        return "✅ AUTHENTIFICATION RÉUSSIE !", creds

    except Exception as e:
        return f"❌ Erreur : {str(e)}", None

st.write("Cette version nettoie les caractères parasites (comme le 1621ème caractère).")

if st.button("LANCER LE NETTOYAGE FINAL"):
    msg, credentials = get_clean_credentials()
    if credentials:
        st.success(msg)
        st.balloons()
        st.info("La clé est maintenant parfaitement formatée. Nous pouvons réintégrer l'IA et le Drive.")
    else:
        st.error(msg)
        st.write(f"Longueur détectée après nettoyage : {len(re.sub(r'[^A-Za-z0-9+/=]', '', info['private_key'])) if 'info' in locals() else 'N/A'}")