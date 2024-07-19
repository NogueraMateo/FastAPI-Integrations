from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from ..models import Advisor
from typing import Optional


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