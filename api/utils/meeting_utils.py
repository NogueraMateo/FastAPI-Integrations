from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from .email_utils import conf
from dateutil import parser
from ..models import Advisor, User
from pydantic import EmailStr


async def get_next_advisor(db: Session):
    # Encontramos el asesor que fue asignado hace más timpo
    advisor = db.query(Advisor).order_by(Advisor.last_assigned_time.asc()).first()
    if advisor:
        # Actualizamos el tiempo de asignación actual
        advisor.last_assigned_time = datetime.now(timezone.utc)
        db.commit()
        return advisor
        

async def send_meeting_invitations_to_users(email_to: EmailStr, meeting_info: dict):
    # Parsear la fecha y hora ISO 8601 a un objeto datetime
    utc_datetime = parser.parse(meeting_info["start_time"])

    local_datetime = utc_datetime - timedelta(hours=5)

    # Formatear datetime para la visualización
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


async def send_meeting_invitations_to_advisors(email_to: EmailStr, meeting_info: dict, current_user: User):
    # Parsear la fecha y hora ISO 8601 a un objeto datetime
    utc_datetime = parser.parse(meeting_info["start_time"])

    local_datetime = utc_datetime - timedelta(hours=5)

    # Formatear datetime para la visualización
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