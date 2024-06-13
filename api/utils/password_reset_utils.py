from fastapi_mail import MessageSchema, FastMail
from .email_utils import conf

async def send_reset_password_email(email_to: str, token: str):
    message = MessageSchema(
        subject="Recuperación de contraseña",
        recipients=[email_to],
        body=f'''Hola, sigue este enlace para restablecer tu contraseña: 
        <a href="http://127.0.0.1:5500/recover.html?token={token}">Aquí</a>''',
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)