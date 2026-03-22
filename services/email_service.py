import smtplib
from email.message import EmailMessage

class EmailService:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def envoyer_email(self, destinataire, sujet, contenu):
        msg = EmailMessage()
        msg['Subject'] = sujet
        msg['From'] = self.username
        msg['To'] = destinataire
        msg.set_content(contenu)

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
            smtp.login(self.username, self.password)
            smtp.send_message(msg)
        print(f"Email envoyé à {destinataire}")