from api.services.meeting_service import MeetingService
from api.schemas import MeetingUpdate
from datetime import datetime, timezone, timedelta
import time

def get_next_datetimes():
    # Updating the meeting datetime to one day after the actual datetime scheduled
    next_day_datetime = datetime.now(timezone.utc) + timedelta(days=2)
    
    # Since Zoom adds 5 hours to the actual date and time we want to schedule the meeting with, 
    # we substract 5 hours to the actual date and time and pass it within the data.
    new_start_time = (next_day_datetime - timedelta(hours=5)).replace(microsecond=0).isoformat()
    meeting_data = {"start_time" : new_start_time}

    return (next_day_datetime, new_start_time, meeting_data)


def test_edit_meeting(create_admin_access_token, create_meeting_to_edit):
    meeting_id, client = create_meeting_to_edit
    access_token = create_admin_access_token
    next_day_datetime, new_start_time, meeting_data = get_next_datetimes()

    client.cookies.set("access_token", access_token)

    response = client.patch(f"/edit/meeting/{meeting_id}", json=meeting_data)
    response_data = response.json()

    assert "start_time" in response_data
    assert "zoom_meeting_id" in response_data
    assert "join_url" in response_data
    assert "id" in response_data
    assert "user_id" in response_data
    assert "advisor_id" in response_data
    assert "topic" in response_data

    response_start_time = datetime.fromisoformat(response_data["start_time"]).astimezone(timezone.utc)
    expected_start_time = next_day_datetime.replace(microsecond=0) - timedelta(hours=5)

    assert response_start_time == expected_start_time
    assert response_data["topic"] == "Testing meeting scheduling"


def test_edit_meeting_fail_1(inactive_admin_access_token, create_meeting_to_edit):
    meeting_id, client = create_meeting_to_edit
    access_token = inactive_admin_access_token
    client.cookies.set("access_token", access_token)
    next_day_datetime, new_start_time, meeting_data = get_next_datetimes()

    response = client.patch(f"/edit/meeting/{meeting_id}", json=meeting_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"


def test_edit_meeting_fail_2(create_meeting_to_edit, create_valid_access_token_3):
    meeting_id, client = create_meeting_to_edit
    access_token = create_valid_access_token_3
    next_day_datetime, new_start_time, meeting_data = get_next_datetimes()
    
    client.cookies.set("access_token", access_token)
    response = client.patch(f"/edit/meeting/{meeting_id}", json=meeting_data)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"


def test_edit_meeting_fail_3(create_meeting_to_edit, create_access_token_expired):
    meeting_id, client = create_meeting_to_edit
    access_token = create_access_token_expired
    next_day_datetime, new_start_time, meeting_data = get_next_datetimes()

    client.cookies.delete("access_token")
    client.cookies.set("access_token", access_token)
    time.sleep(3)
    response = client.patch(f"/edit/meeting/{meeting_id}", json=meeting_data)
    client.cookies.delete("access_token")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


def test_edit_meeting_fail_4(create_meeting_to_edit):
    meeting_id, client = create_meeting_to_edit
    next_day_datetime, new_start_time, meeting_data = get_next_datetimes()
    
    response = client.patch(f"/edit/meeting/{meeting_id}", json=meeting_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"