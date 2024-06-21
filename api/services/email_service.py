from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from ..utils.email_utils import conf
from dateutil import parser
from ..models import Advisor, User
from pydantic import EmailStr, BaseModel
from typing import Optional
from ..services.token_service import EmailConfirmationTokenService, PasswordResetTokenService
from ..config.email_messages import confirmation_message, reset_message, user_invitation_message, advisor_invitation_message, user_reschedule_message, advisor_reschedule_message


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
            subject= "Invitation to Zoom Meeting",
            recipients= [email_to],
            body= user_invitation_message(formatted_time, meeting_info.get("join_url")),
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
        utc_datetime = parser.parse(meeting_info.get("start_time"))

        local_datetime = utc_datetime - timedelta(hours=5)

        # Format datetime for display
        formatted_time = local_datetime.strftime('%Y-%m-%d %H:%M %Z')
        message = MessageSchema(
            subject= "New Zoom Meeting Scheduled",
            recipients= [email_to],
            body= advisor_invitation_message(formatted_time, meeting_info.get("join_url"), current_user.first_name, current_user.lastname, meeting_info.get("topic")),
            subtype= "html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)


    async def send_user_reschedule_message(self, email_to: EmailStr, new_start_time: datetime, join_url: str):
        local_datetime = new_start_time
        formatted_time = local_datetime.strftime('%Y-%m-%d %H:%M %Z')
        message = MessageSchema(
            subject= "Zoom Meeting Rescheduled",
            recipients= [email_to],
            body= user_reschedule_message(formatted_time, join_url),
            subtype='html'
        )
        fm = FastMail(conf)
        await fm.send_message(message)

    async def send_advisor_reschedule_message(self, email_to: EmailStr, new_start_time: datetime, join_url: str, user_first_name: str, user_last_name: str, topic: str):
        local_datetime = new_start_time
        formatted_time = local_datetime.strftime('%Y-%m-%d %H:%M %Z')
        message = MessageSchema(
            subject= "Zoom Meeting Rescheduled",
            recipients= [email_to],
            body= advisor_reschedule_message(formatted_time, join_url, topic, user_first_name, user_last_name),
            subtype='html'
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
            subject="Account Confirmation",
            recipients=[email_to],
            body=confirmation_message(token),
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
            subject="Password Reset",
            recipients=[email_to],
            body=reset_message(token),
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)