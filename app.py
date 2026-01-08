import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Elite Intelligence Terminal", page_icon="💠", layout="centered")

# --- STYLE ---
st.markdown("""
    <style>
    .report-card { background-color: #1a1c24; border-radius: 15px; padding: 25px; border-left: 5px solid #00d4ff; color: #e0e0e0; margin-top: 20px; }
    div.stButton > button { background: linear-gradient(45deg, #007bff, #00d4ff); color: white; border-radius: 25px; border: none; padding: 10px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIG IA ---
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def ask_agent(role, instr, prompt, model, langue):
    # On supprime COMPLÈTEMENT l'argument 'tools' pour éviter l'erreur de schéma
    config = types.GenerateContentConfig(
        system_instruction=f"Tu es {role}. {instr} RÉPONDS EN {langue.upper()}."
    )
    # Appel direct sans outils
    response = client.models.generate_content(model=model, config=config, contents=prompt)
    return response.text

# --- INTERFACE ---
st.title("💠 Elite Intelligence Terminal")
langue = st.sidebar.selectbox("Langue", ["Français", "Anglais", "Arabe"])
sujet = st.text_input("Sujet stratégique", placeholder="Entrez votre sujet...")

if st.button("DÉCRYPTER") and sujet:
    with st.status("⚡ Analyse multi-agents...", expanded=True) as status:
        
        st.write("🔎 Scout : Analyse...")
        # On a retiré le paramètre search ici aussi
        intel = ask_agent("Scout", "Cherche des faits précis.", sujet, "gemini-1.5-flash", langue)
        
        st.write("⚖️ Expert : Analyse...")
        analyse = ask_agent("Expert", "Analyse le contexte.", intel, "gemini-1.5-pro", langue)
        
        st.write("✍️ Éditeur : Rédaction...")
        report = ask_agent("Éditeur", "Rédige l'éditorial final.", f"Sujet: {sujet}\nIntel: {intel}\nAnalyse: {analyse}", "gemini-1.5-pro", langue)
        
        status.update(label="Analyse terminée", state="complete")

    st.markdown(f'<div class="report-card">{report}</div>', unsafe_allow_html=True)