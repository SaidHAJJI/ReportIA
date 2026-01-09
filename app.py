import streamlit as st
from datetime import datetime
from google import genai
from google.genai import types

st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- INITIALISATION ---
if "archives" not in st.session_state:
    st.session_state.archives = []

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# --- MOTEUR D'AGENTS (NETTOYÉ DE TOUT TOOL) ---
def ask_agent(role_name, instr, prompt, model, langue, max_tokens=1200):
    # On définit uniquement ce qui est nécessaire. Pas de paramètre 'tools'.
    config = types.GenerateContentConfig(
        system_instruction=f"{role_name}: {instr} EN {langue.upper()}.",
        max_output_tokens=max_tokens,
        temperature=0.7
    )
    # L'appel est maintenant ultra-basique pour éviter les ClientError
    response = client.models.generate_content(model=model, config=config, contents=prompt)
    return response.text

# --- INTERFACE ---
st.title("💠 Intelligence Terminal")

with st.sidebar:
    st.header("⚙️ Configuration")
    mode_puissance = st.radio(
        "Mode d'analyse :",
        ["Standard (Économique)", "Élite (Précision Pro)"],
        help="Standard utilise Flash (moins cher). Élite utilise Pro (plus analytique)."
    )
    
    model_choice = "gemini-1.5-pro" if "Élite" in mode_puissance else "gemini-1.5-flash"
    
    st.divider()
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    
    st.header("📂 Archives")
    for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
        if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
            st.session_state.current_report = arc['contenu']

sujet = st.text_input("", placeholder="Sujet stratégique...", label_visibility="collapsed")

if st.button("DÉCRYPTER") and sujet:
    with st.status(f"⚡ Analyse {mode_puissance}...", expanded=True) as status:
        
        st.write("🔎 Scout : Analyse...")
        # Scout est toujours en Flash pour économiser
        intel = ask_agent("Scout", "Extraits les faits clés.", f"Sujet: {sujet}", "gemini-1.5-flash", langue, max_tokens=600)
        
        st.write(f"⚖️ Expert : Analyse...")
        analyse = ask_agent("Expert", "Analyse l'impact stratégique.", intel, model_choice, langue, max_tokens=1000)
        
        st.write(f"✍️ Éditeur : Rédaction...")
        report = ask_agent("Éditeur", "Rédige l'éditorial final en Markdown.", f"Base: {intel}\nAnalyse: {analyse}", model_choice, langue, max_tokens=1500)
        
        st.session_state.archives.append({"sujet": sujet, "contenu": report})
        st.session_state.current_report = report
        status.update(label="Rapport terminé", state="complete")

# --- AFFICHAGE ---
if "current_report" in st.session_state:
    st.markdown(f'<div style="background-color: #1a1c24; border-radius: 15px; padding: 25px; border-left: 5px solid #00d4ff; color: #e0e0e0;">{st.session_state.current_report}</div>', unsafe_allow_html=True)
    st.download_button("📥 EXPORTER", st.session_state.current_report, file_name=f"report_{datetime.now().strftime('%d%m')}.md")