from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from dotenv import load_dotenv
import os
from ..config.constants import MAIL_FROM, MAIL_PASSWORD, MAIL_USERNAME


# ------------------------------------ FASTMAIL CONFIGURATION! ------------------------------------
conf = ConnectionConfig(
    MAIL_USERNAME= MAIL_USERNAME,
    MAIL_PASSWORD= MAIL_PASSWORD,
    MAIL_FROM= MAIL_FROM,
    MAIL_PORT= 587,
    MAIL_SERVER= "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

# ------------------------------------ MAIL FUNCTIONS! ------------------------------------
async def send_confirmation_account_message(email_to: str, token:str):
    message = MessageSchema(
        subject="Confirmación de tu cuenta",
        recipients=[email_to],
        body=f'''Hola, por favor sigue el siguiente enlace para confirmar tu cuenta: 
        <a href="http://127.0.0.1:5500/confirm-account.html?token={token}">Aquí</a>''',
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
