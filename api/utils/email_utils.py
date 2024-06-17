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
