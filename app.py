import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="Elite Archiver", page_icon="📨")

st.title("📨 Test d'Archivage Hybride")

# --- SIMULATION DE CONTENU ---
dummy_report = f"""# RAPPORT DE TEST E-MAIL
Généré le : {datetime.now().strftime("%d/%m/%Y à %H:%M")}

Ceci est un test pour valider l'archivage par email et le téléchargement local.
L'archivage par email permet de garder une trace permanente dans votre boîte aux lettres.
"""

def send_email(content):
    try:
        sender = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        receiver = st.secrets["EMAIL_RECEIVER"]

        # Configuration du message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"💠 ARCHIVE ELITE - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        msg.attach(MIMEText(content, 'plain'))

        # Connexion au serveur Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True, "✅ Email envoyé avec succès !"
    except Exception as e:
        return False, f"❌ Erreur Email : {str(e)}"

# --- INTERFACE ---
st.subheader("Options d'exportation")

col1, col2 = st.columns(2)

with col1:
    st.write("📂 **Option 1 : Local**")
    st.download_button(
        label="TÉLÉCHARGER LE RAPPORT",
        data=dummy_report,
        file_name="rapport_test.md",
        mime="text/markdown"
    )

with col2:
    st.write("📧 **Option 2 : Cloud**")
    if st.button("ENVOYER PAR EMAIL"):
        with st.spinner("Envoi en cours..."):
            success, message = send_email(dummy_report)
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)
                st.info("Avez-vous bien configuré le 'Mot de passe d'application' dans vos secrets ?")

st.markdown("---")
st.write("Aperçu du contenu test :")
st.code(dummy_report, language="markdown")