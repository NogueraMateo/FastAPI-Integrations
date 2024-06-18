from ..utils.meeting_utils import get_next_advisor
from ..services.meeting_service import MeetingService
from ..services.user_service import UserService
from ..services.email_service import EmailService

from fastapi import APIRouter, HTTPException, Depends
from ..utils.auth_utils import get_current_user

from datetime import datetime, timezone
from ..schemas import MeetingCreate, UserUpdate
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User


router = APIRouter(tags=["Meeting scheduling"])

# ------------------------------------------ ROUTE FOR SCHEDULING MEETINGS ------------------------------------------
@router.post("/schedule-meeting/")
async def schedule_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_service = MeetingService(db)
    user_service = UserService(db)
    email_service = EmailService()

    if not current_user:
        raise HTTPException(status_code=401, detail= "Unauthorized")

    if not current_user.can_schedule_meeting():
        raise HTTPException(status_code=400, detail= "It has not been 7 days since you last scheduled a meeting") 

    # Nos aseguramos de que hay advisors dispoibles 
    advisor = await get_next_advisor(db)
    if not advisor:
        raise HTTPException(status_code=404, detail="No advisors available")
    
    # Obtener el access token para la API de Zoom
    access_token = meeting_service.get_meeting_access_token()

    # Crear la reunión en Zoom
    meeting_info = meeting_service.create_meeting(access_token, meeting_data.start_time, meeting_data.topic)

    # Guardar la reunión en la base de datos
    new_meeting = meeting_service.save_meeting_to_db(current_user.id, advisor.id, meeting_info)

    user_update = UserUpdate(last_meeting_scheduled= datetime.now(timezone.utc))
    user_service.update_user(user_id=current_user.id, user_update= user_update)

    await email_service.send_meeting_invitations_to_users(current_user.email, meeting_info)
    await email_service.send_meeting_invitations_to_advisors(advisor.email, meeting_info, current_user)

    return {
        "message": "Meeting scheduled successfully",
        "meeting_id": new_meeting.id,
        "join_url": meeting_info.get('join_url')
    }