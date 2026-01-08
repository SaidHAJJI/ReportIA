def check_auth():
    try:
        # 1. Chargement des secrets
        info = dict(st.secrets["gcp_service_account"])
        
        # 2. NETTOYAGE RENFORCÉ
        # On traite les deux cas possibles : les vrais \n et les textes "\\n"
        raw_key = info["private_key"]
        clean_key = raw_key.replace("\\n", "\n")
        
        # Si après le premier remplacement il reste des doubles backslashes, on nettoie encore
        info["private_key"] = clean_key.strip()
        
        # 3. Authentification
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        
        # 4. Test de lecture
        folder_id = st.secrets.get("DRIVE_FOLDER_ID")
        results = service.files().list(
            q=f"'{folder_id}' in parents", 
            pageSize=1
        ).execute()
        
        return "✅ Connexion réussie ! Le padding de la clé est maintenant correct."

    except Exception as e:
        # On affiche la clé brute (masquée partiellement) pour débugger visuellement
        if "padding" in str(e).lower():
            st.code(f"Début de clé détecté : {info['private_key'][:30]}...")
        return f"❌ Erreur d'authentification : {str(e)}"