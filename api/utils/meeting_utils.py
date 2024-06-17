from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from dateutil import parser
from ..models import Advisor, User
from pydantic import EmailStr, BaseModel
from typing import Optional
from ..services.token_service import EmailConfirmationTokenService, PasswordResetTokenService


async def get_next_advisor(db: Session) -> Optional[Advisor] :
    """
    Retrieve the advisor who was assigned the longest time ago and update their last assigned time.

    Args:
        db (Session): The database session.

    Returns:
        Advisor: The advisor object with the updated last assigned time.
    """

    advisor = db.query(Advisor).order_by(Advisor.last_assigned_time.asc()).first()
    if advisor:
        advisor.last_assigned_time = datetime.now(timezone.utc)
        db.commit()
        return advisor