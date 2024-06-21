from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..config.exceptions import PatchMeetingError, DeleteMeetingError
from datetime import datetime
from typing import Optional
from .. import models, schemas
import base64
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class MeetingService:

    def __init__(self, db: Session):
        self.db : Session = db
        self.ZOOM_CLIENT_ID: str = os.getenv('ZOOM_CLIENT_ID')
        self.ZOOM_CLIENT_SECRET= os.getenv('ZOOM_CLIENT_SECRET')
        self.ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')


    def get_meeting_by_zoom_id(self, meeting_id: int) -> models.Meeting:
        return self.db.query(models.Meeting).filter(models.Meeting.zoom_meeting_id == meeting_id).first()


    def get_meeting_access_token(self) -> str:
        url = 'https://zoom.us/oauth/token'
        credentials = f"{self.ZOOM_CLIENT_ID}:{self.ZOOM_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')  # Codifica las credenciales en base64
        auth_header = {
            'Authorization': f'Basic {encoded_credentials}',  # Usa las credenciales codificadas
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type': 'account_credentials',
            "account_id" : self.ZOOM_ACCOUNT_ID
        }
        response = requests.post(url, headers=auth_header, data=payload)
        return response.json().get('access_token')


    def create_meeting(self, access_token: str, start_time: datetime, topic: str) -> json:
        url = f"https://api.zoom.us/v2/users/me/meetings"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "topic": topic,
            "type": 2,
            "start_time": start_time.isoformat(),
            "duration": "30",  # Duration in minutes
            "timezone": "America/Bogota",
            "settings": {
                "join_before_host": True,
                "jbh_time": 5, 
                "registration_type": 2,
                "enforce_login": False,
                "waiting_room": False
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()

    
    def update_meeting(self, meeting_id: str, meeting_update: schemas.MeetingUpdate) -> models.Meeting | None:
        access_token = self.get_meeting_access_token()
        db_meeting: models.Meeting = self.get_meeting_by_zoom_id(meeting_id)
        if not db_meeting:
            raise HTTPException(status_code=404, detail="Meeting id not found")
        
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "topic": db_meeting.topic,
            "start_time": meeting_update.start_time.isoformat(),
            "duration": "30",
            "timezone": "America/Bogota",
            "settings": {
                "join_before_host": True,
                "jbh_time": 5,
                "registration_type": 2,
                "enforce_login": False,
                "waiting_room": False
            }
        }
        response = requests.patch(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 204:
            meeting_data = meeting_update.model_dump(exclude_unset=True)
            for key, value in meeting_data.items():
                setattr(db_meeting, key, value)
            
            self.db.commit()
            self.db.refresh(db_meeting)
            return db_meeting
        
        raise PatchMeetingError


    
    def delete_meeting(self, meeting_id: str) -> models.Meeting | None:
        access_token = self.get_meeting_access_token()
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            db_meeting= self.get_meeting_by_zoom_id(meeting_id)
            if db_meeting is None:
                return None
            
            self.db.delete(db_meeting)
            self.db.commit()
            return db_meeting

        raise DeleteMeetingError


    def save_meeting_to_db(self, user_id: int, advisor_id:int, meeting_info:dict) -> models.Meeting:
        new_meeting = models.Meeting(
            user_id=user_id,
            advisor_id=advisor_id,
            start_time=meeting_info['start_time'],
            topic= meeting_info["topic"],
            zoom_meeting_id=meeting_info['id'],
            join_url=meeting_info['join_url']
        )
        self.db.add(new_meeting)
        self.db.commit()
        self.db.refresh(new_meeting)
        return new_meeting
        

    def delete_scheduled_meetings_from_user(self, user_id: int) -> None:
        meetings_to_delete= self.db.query(models.Meeting).filter(models.Meeting.user_id == user_id).all()
        for meeting in meetings_to_delete:
            self.db.delete(meeting)
        self.db.commit()
