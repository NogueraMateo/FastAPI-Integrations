from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from ..utils.email_utils import conf
from dateutil import parser
from ..models import Advisor, User
from pydantic import EmailStr, BaseModel
from typing import Optional
from ..services.token_service import EmailConfirmationTokenService, PasswordResetTokenService

class EmailService:

    async def send_meeting_invitations_to_users(self, email_to: EmailStr, meeting_info: dict) -> None:
        """
        Send a Zoom meeting invitation to a user.

        Args:
            email_to (EmailStr): The email address of the user.
            meeting_info (dict): A dictionary containing meeting details such as 'start_time' and 'join_url'.

        Returns:
            None
        """

        # Parse ISO 8601 date and time to a datetime object
        utc_datetime = parser.parse(meeting_info["start_time"])
        local_datetime = utc_datetime - timedelta(hours=5)

        # Format datetime for display
        formatted_time = local_datetime.strftime('%Y-%m-%d %H:%M %Z')
        message = MessageSchema(
            subject= "Invitación a Reunión de Zoom",
            recipients= [email_to],
            body= f"""
            <h3>¡Hola!, agendaste una reunión de Zoom para asesoría.</h3><br><br>
            <h4>Fecha y hora: {formatted_time}</h4><br><br>
            <p>Únete a la reunión Zoom haciendo clic en el siguiente enlace: {meeting_info['join_url']}</p>""",
            subtype= "html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)


    async def send_meeting_invitations_to_advisors(self, email_to: EmailStr, meeting_info: dict, current_user: User) -> None:
        """
        Send a Zoom meeting invitation to an advisor.

        Args:
            email_to (EmailStr): The email address of the advisor.
            meeting_info (dict): A dictionary containing meeting details such as 'start_time', 'join_url', and 'topic'.
            current_user (User): The user who scheduled the meeting.

        Returns:
            None
        """

        # Parse ISO 8601 date and time to a datetime object
        utc_datetime = parser.parse(meeting_info["start_time"])

        local_datetime = utc_datetime - timedelta(hours=5)

        # Format datetime for display
        formatted_time = local_datetime.strftime('%Y-%m-%d %H:%M %Z')
        message = MessageSchema(
            subject= "Nueva reunión de Zoom agendadada",
            recipients= [email_to],
            body= f"""
            <h3>¡Hola!, el usuario {current_user.first_name} {current_user.lastname} ha agendado una reunión de zoom contigo.</h3><br><br>
            <h4>Fecha y hora: {formatted_time}</h4><br><br>
            <h4>Motivo: {meeting_info["topic"]} </h4>
            <p>Únete a la reunión Zoom haciendo clic en el siguiente enlace: {meeting_info['join_url']}</p>""",
            subtype= "html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)

    
    async def send_confirmation_account_message(self, email_to: EmailStr, token: str) -> None:
        """
        Send a confirmation email to the user with a token to confirm their account.

        Args:
            email_to (str): The email address of the user.
            token (str): The confirmation token to be included in the email.

        Returns:
            None
        """

        message = MessageSchema(
            subject="Confirmación de tu cuenta",
            recipients=[email_to],
            body=f'''Hola, por favor sigue el siguiente enlace para confirmar tu cuenta: 
            <a href="http://127.0.0.1:5500/confirm-account.html?token={token}">Aquí</a>''',
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)


    async def send_reset_password_email(self, email_to: str, token: str):
        """
        Send a password reset email to the user with a token to reset their password.

        Args:
            email_to (str): The email address of the user.
            token (str): The reset token to be included in the email.

        Returns:
            None
        """
        message = MessageSchema(
            subject="Recuperación de contraseña",
            recipients=[email_to],
            body=f'''Hola, sigue este enlace para restablecer tu contraseña: 
            <a href="http://127.0.0.1:5500/recover.html?token={token}">Aquí</a>''',
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)