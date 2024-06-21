from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..config.exceptions import PatchMeetingError, DeleteMeetingError, CreateMeetingError
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
    """
    A service class for managing Zoom meetings and their database interactions.

    Attributes:
        db (Session): The database session.
        ZOOM_CLIENT_ID (str): Zoom client ID from environment variables.
        ZOOM_CLIENT_SECRET (str): Zoom client secret from environment variables.
        ZOOM_ACCOUNT_ID (str): Zoom account ID from environment variables.
    """

    def __init__(self, db: Session):
        """
        Initialize the MeetingService with a database session.

        Args:
            db (Session): The database session.
        """
        self.db : Session = db
        self.ZOOM_CLIENT_ID: str = os.getenv('ZOOM_CLIENT_ID')
        self.ZOOM_CLIENT_SECRET= os.getenv('ZOOM_CLIENT_SECRET')
        self.ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')


    def get_meeting_by_zoom_id(self, meeting_id: int) -> models.Meeting:
        """
        Retrieve a meeting from the database by its Zoom meeting ID.

        Args:
            meeting_id (int): The Zoom meeting ID.

        Returns:
            models.Meeting: The meeting with the given Zoom meeting ID.
        """
        return self.db.query(models.Meeting).filter(models.Meeting.zoom_meeting_id == meeting_id).first()


    def get_meeting_access_token(self) -> str:
        """
        Retrieve an access token for the Zoom API.

        Returns:
            str: The access token for the Zoom API.
        """
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


    def create_meeting(self, start_time: datetime, topic: str, user_id: int, advisor_id: int) -> (models.Meeting, dict):
        """
        Create a new Zoom meeting and save it to the database.

        Args:
            start_time (datetime): The start time of the meeting.
            topic (str): The topic of the meeting.
            user_id (int): The ID of the user scheduling the meeting.
            advisor_id (int): The ID of the advisor assigned to the meeting.

        Returns:
            tuple: The new meeting and meeting information from Zoom.

        Raises:
            CreateMeetingError: If the meeting could not be created.
        """
        
        access_token = self.get_meeting_access_token()
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

        if response.status_code == 201:
            meeting_info = response.json()
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
            return (new_meeting, meeting_info)
        
        raise CreateMeetingError

    
    def update_meeting(self, meeting_id: str, meeting_update: schemas.MeetingUpdate) -> models.Meeting | None:
        """
        Update an existing Zoom meeting and its database record.

        Args:
            meeting_id (str): The ID of the meeting to update.
            meeting_update (schemas.MeetingUpdate): The updated meeting details.

        Returns:
            models.Meeting: The updated meeting.

        Raises:
            HTTPException: If the meeting ID is not found.
            PatchMeetingError: If the meeting could not be updated.
        """

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
        """
        Delete a Zoom meeting and its database record.

        Args:
            meeting_id (str): The ID of the meeting to delete.

        Returns:
            models.Meeting: The deleted meeting.

        Raises:
            DeleteMeetingError: If the meeting could not be deleted.
        """

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
