import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types
import streamlit.components.v1 as components

# --- CONFIGURATION PRE-REQUIS ---
st.set_page_config(
    page_title="Elite Intelligence Terminal",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- STYLE CSS AVANCÉ ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .report-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 25px;
        border-left: 5px solid #00d4ff;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
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
    .tts-container {
        padding: 10px;
        background: #1a1c24;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- COMPOSANT TTS AMÉLIORÉ ---
def tts_component(text, langue):
    lang_code = {"Français": "fr-FR", "Anglais": "en-US", "Arabe": "ar-SA"}.get(langue, "fr-FR")
    clean_text = text.replace("'", "\\'").replace("\n", " ").replace('"', '\\"')
    
    # Bouton HTML natif pour forcer l'interaction utilisateur
    html_code = f"""
    <div style="display: flex; gap: 10px; justify-content: center; align-items: center; background: #1a1c24; padding: 15px; border-radius: 15px;">
        <button onclick="speak()" style="background: linear-gradient(45deg, #28a745, #20c997); border: none; color: white; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-weight: bold;">▶ ÉCOUTER</button>
        <button onclick="stop()" style="background: linear-gradient(45deg, #dc3545, #f8d7da); border: none; color: #721c24; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-weight: bold;">⏹ STOP</button>
    </div>

    <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = "{clean_text}";
        msg.lang = "{lang_code}";
        msg.rate = 1.0;

        function speak() {{
            window.speechSynthesis.cancel(); // Arrête toute lecture en cours
            window.speechSynthesis.speak(msg);
        }}

        function stop() {{
            window.speechSynthesis.cancel();
        }}
    </script>
    """
    components.html(html_code, height=80)

# --- INITIALISATION ---
if "archives" not in st.session_state:
    st.session_state.archives = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "last_sujet" not in st.session_state:
    st.session_state.last_sujet = "rapport"

# --- GESTION DES SECRETS ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("🔑 API KEY", type="password")

if not api_key:
    st.title("💠 Elite Intelligence")
    st.info("Système en attente de clé API...")
    st.stop()

client = genai.Client(api_key=api_key)

# --- CONFIGURATION MODES ---
MODEL_FLASH = "models/gemini-flash-latest"
MODEL_PRO = "models/gemini-pro-latest"

with st.sidebar:
    st.header("⚙️ Paramètres")
    mode_elite = st.toggle("💎 Mode Élite", value=False)
    
    active_scout_model = MODEL_FLASH
    if mode_elite:
        active_expert_model = MODEL_PRO
        active_editor_model = MODEL_PRO
    else:
        active_expert_model = MODEL_FLASH
        active_editor_model = MODEL_FLASH

    st.divider()
    st.header("📂 Archives Récentes")
    if st.session_state.archives:
        for i, arc in enumerate(reversed(st.session_state.archives[-5:])):
            if st.button(f"📄 {arc['sujet'][:20]}...", key=f"arc_{i}"):
                st.session_state.current_report = arc['contenu']
                st.session_state.last_sujet = arc['sujet']
                st.rerun()
    
    langue = st.selectbox("Langue", ["Français", "Anglais", "Arabe"])
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.archives = []
        st.session_state.current_report = None
        st.rerun()

search_tool = types.Tool(google_search=types.GoogleSearch())

def ask_agent(role_name, instr, prompt, model, langue, use_search=False):
    detail_instr = "Fournis une réponse riche, structurée et approfondie."
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role_name}. {detail_instr} {instr} RÉPONDS EN {langue.upper()}.",
        tools=[search_tool] if use_search else []
    )
    try:
        response = client.models.generate_content(model=model, config=config, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erreur : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("💠 Intelligence Terminal")

sujet = st.text_input("", placeholder="Sujet stratégique...", label_visibility="collapsed")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Orchestration...", expanded=True) as status:
        intel = ask_agent("Scout", "Faits exhaustifs.", f"Infos sur {sujet}", active_scout_model, langue, True)
        d1 = ask_agent("Expert", "Analyse détaillée.", f"Context: {intel}", active_expert_model, langue)
        
        st.write("⏳ Temporisation (1 min)...")
        p_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.6)
            p_bar.progress(i + 1)
            
        report = ask_agent("Éditeur", "Éditorial complet.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {d1}", active_editor_model, langue)
        
        st.session_state.archives.append({"sujet": sujet, "contenu": report})
        st.session_state.current_report = report
        st.session_state.last_sujet = sujet
        status.update(label="Terminé", state="complete")

# --- AFFICHAGE ET EXPORT ---
if st.session_state.current_report:
    # 1. Barre d'outils vocale (Nouveau composant interactif)
    tts_component(st.session_state.current_report, langue)
    
    # 2. Bouton de sauvegarde
    clean_name = "".join([c for c in st.session_state.last_sujet if c.isalnum() or c==' ']).rstrip()
    st.download_button("📥 SAUVEGARDER LE RAPPORT", st.session_state.current_report, file_name=f"INTEL_{clean_name}.md")

    # 3. Rapport
    st.markdown(f'<div class="report-card">{st.session_state.current_report}</div>', unsafe_allow_html=True)