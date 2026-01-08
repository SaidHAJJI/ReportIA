import streamlit as st
from datetime import datetime
from google import genai
from google.genai import types

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- STYLE CSS (Le look Pro que vous aimiez) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .report-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 25px;
        border-left: 5px solid #00d4ff;
        margin-bottom: 20px;
        color: #e0e0e0;
        line-height: 1.6;
    }
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        border: none;
        color: white;
        padding: 12px;
        border-radius: 25px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
# On récupère uniquement la clé Gemini des Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("🔑 Clé GOOGLE_API_KEY manquante dans les Secrets.")
    st.stop()

# Initialisation du client
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Erreur d'initialisation : {e}")
    st.stop()

# --- INTERFACE ---
st.title("💠 Intelligence Terminal")
st.caption("Version de Diagnostic (Sans Drive)")

with st.sidebar:
    st.header("⚙️ Configuration")
    langue = st.selectbox("Langue du rapport", ["Français", "Anglais", "Arabe"])
    # Option pour changer de modèle si le quota Pro est saturé
    model_version = st.radio("Modèle Gemini", ["1.5 Flash (Rapide/Stable)", "1.5 Pro (Puissant/Limité)"])
    model_id = "models/gemini-1.5-flash" if "Flash" in model_version else "models/gemini-1.5-pro"

sujet = st.text_input("📝 Sujet de l'analyse :", placeholder="Entrez votre sujet...")
launch = st.button("DÉCRYPTER")

# --- EXÉCUTION ---
if launch and sujet:
    with st.status("⚡ Analyse en cours...", expanded=True) as status:
        try:
            # Un seul appel simple pour tester le quota
            prompt = f"Rédige un éditorial de prestige sur le sujet suivant : {sujet}. RÉPONDS EXCLUSIVEMENT EN {langue.upper()}."
            
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            
            report = response.text
            status.update(label="Analyse terminée !", state="complete")
            
            # Affichage du résultat
            st.markdown(f'<div class="report-card">{report}</div>', unsafe_allow_html=True)
            
            # Bouton de secours pour récupérer le texte
            st.download_button("📥 Télécharger le rapport", report, file_name=f"rapport_{datetime.now().strftime('%Y%m%d')}.md")

        except Exception as e:
            status.update(label="Échec de l'analyse", state="error")
            st.error(f"🛑 Erreur API : {e}")
            if "429" in str(e):
                st.warning("Diagnostic : Quota dépassé. Essayez de passer sur le modèle '1.5 Flash' dans la barre latérale.")

elif launch:
    st.warning("Veuillez saisir un sujet avant de lancer l'analyse.")