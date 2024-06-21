from ..utils.meeting_utils import get_next_advisor
from ..services.meeting_service import MeetingService
from ..services.user_service import UserService
from ..services.email_service import EmailService

from fastapi import APIRouter, HTTPException, Depends
from ..utils.auth_utils import get_current_user, get_current_admin_user

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas


router = APIRouter(tags=["Meeting scheduling"])

# ------------------------------------------ ROUTE FOR SCHEDULING MEETINGS ------------------------------------------
@router.post("/schedule-meeting/",response_model=schemas.Meeting)
async def schedule_meeting(
    meeting_data: schemas.MeetingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Schedule a new meeting with an advisor.
    
    This endpoint allows a user to schedule a new meeting with an available advisor. 
    The user must not have scheduled a meeting in the past 7 days. If successful, 
    the meeting details will be sent via email to both the user and the advisor.

    Args:
        meeting_data (schemas.MeetingCreate): Data required to create a new meeting.
            - start_time (str): The start time of the meeting in ISO 8601 format. Example: "2024-06-20T12:20"
            - topic (str): The topic of the meeting. Example: "Extra info about the services the company offers."
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (models.User, optional): The currently authenticated user. Defaults to Depends(get_current_user).

    Returns:
        dict: A dictionary containing the message, meeting ID, and join URL.

    Raises:
        HTTPException: If the user is not authenticated (status code 401).
        HTTPException: If the user has scheduled a meeting in the past 7 days (status code 400).
        HTTPException: If no advisors are available (status code 404).
    """
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

    user_update = schemas.UserUpdate(last_meeting_scheduled= datetime.now(timezone.utc))
    user_service.update_user(user_id=current_user.id, user_update= user_update)

    await email_service.send_meeting_invitations_to_users(current_user.email, meeting_info)
    await email_service.send_meeting_invitations_to_advisors(advisor.email, meeting_info, current_user)

    return new_meeting


@router.patch("/edit/meeting/{meeting_id}", response_model=schemas.Meeting)
async def edit_scheduled_meeting(meeting_id: str, meeting_update: schemas.MeetingUpdate, admin_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    meeting_service = MeetingService(db)
    try:
        updated_meeting: models.Meeting = meeting_service.update_meeting(meeting_id, meeting_update)
        
    except:
        raise HTTPException(status_code=400, detail= "Something went wrong while updating the meeting")

    email_service = EmailService()

    await email_service.send_user_reschedule_message(updated_meeting.user.email, updated_meeting.start_time, updated_meeting.join_url)
    await email_service.send_advisor_reschedule_message(updated_meeting.advisor.email, updated_meeting.start_time, updated_meeting.join_url, updated_meeting.user.first_name, updated_meeting.user.lastname, updated_meeting.topic)

    return updated_meeting


@router.delete("/delete/meeting/{meeting_id}")
async def delete_scheduled_meeting(meeting_id: str, admin_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    meeting_service = MeetingService(db)
    try:
        deleted_meeting = meeting_service.delete_meeting(meeting_id)
    except:
        raise HTTPException(status_code=400, detail="Something went wrong while deleting the meeting")
    
    return deleted_meeting