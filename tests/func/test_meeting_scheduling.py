from datetime import datetime, timezone, timedelta
from api.schemas import Meeting
from api.services.meeting_service import MeetingService
import time

def get_datetimes():
    # This is the actual date and time the meeting is going to be scheduled
    tomorrow_time = datetime.now(timezone.utc) + timedelta(days=1)
    # Since Zoom adds 5 hours to the actual date and time we want to schedule the meeting with, 
    # we substract 5 hours to the actual date and time and pass it within the data.
    start_time = (tomorrow_time - timedelta(hours=5)).replace(microsecond=0).isoformat()
    meeting_data = {"start_time": start_time,"topic" : "Testing meeting scheduling"}

    return (tomorrow_time, start_time, meeting_data)


def test_meeting_scheduling_fail(register_users_for_login, create_valid_access_token_1):
    """
    Test scheduling a meeting without available advisors.

    This test verifies that attempting to schedule a meeting when no advisors are available results in a 404 error.
    It includes:
    - Logging in as an existing user.
    - Attempting to schedule a meeting with a specified start time and topic.
    - Validating that the response returns a 404 status and the appropriate error message.

    Args:
        register_users_for_login (fixture): Fixture to register and login users.
        create_valid_access_token_1 (fixture): Fixture to create a valid access token.
        db_session (fixture): Database session fixture.
    """
    access_token = create_valid_access_token_1
    client = register_users_for_login
    tomorrow_time, start_time, meeting_data = get_datetimes()

    client.cookies.set("access_token", access_token)
    response = client.post("/schedule-meeting/", json=meeting_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "No advisors available"


def test_successful_meeting_scheduling(register_users_for_login, insert_advisors_for_meeting_scheduling, create_valid_access_token_1,db_session):
    """
    Test successful scheduling of a meeting.

    This test verifies that a user can successfully schedule a meeting with the correct details.
    It includes:
    - Logging in as an existing user.
    - Scheduling a meeting with a specified start time and topic.
    - Validating the response data from the API.
    - Verifying the meeting details with Zoom's API.

    Args:
        register_users_for_login (fixture): Fixture to register and login users.
        insert_advisors_for_meeting_scheduling (fixture): Fixture to insert advisors for meeting scheduling.
        create_valid_access_token_1 (fixture): Fixture to create a valid access token.
        db_session (fixture): Database session fixture.
    """
    access_token = create_valid_access_token_1
    client = register_users_for_login
    tomorrow_time, start_time, meeting_data = get_datetimes()
    
    client.cookies.set("access_token", access_token)
    response = client.post("/schedule-meeting/", json=meeting_data)
    assert response.status_code == 200

    response_data = response.json()
    
    assert "start_time" in response_data
    assert "zoom_meeting_id" in response_data
    assert "join_url" in response_data
    assert "id" in response_data
    assert "user_id" in response_data
    assert "advisor_id" in response_data
    assert "topic" in response_data

    response_start_time = datetime.fromisoformat(response_data["start_time"]).astimezone(timezone.utc)
    expected_start_time = tomorrow_time.replace(microsecond=0)

    assert response_start_time == expected_start_time
    assert response_data["topic"] == "Testing meeting scheduling"

    service = MeetingService(db_session)
    zoom_meeting_info = service.get_meeting(response_data["zoom_meeting_id"])

    assert str(zoom_meeting_info.get("id")) == response_data.get("zoom_meeting_id")
    assert zoom_meeting_info.get("join_url") == response_data.get("join_url")
    assert zoom_meeting_info.get("topic") == response_data.get("topic")


def test_meeting_scheduling_fail_1(client, db_session):
    """
    Test scheduling a meeting without authentication.

    This test verifies that attempting to schedule a meeting without providing authentication headers results in a 401 error.
    It includes:
    - Attempting to schedule a meeting with a specified start time and topic without authentication.
    - Validating that the response returns a 401 status and the appropriate error message.

    Args:
        client (fixture): Fixture to provide the test client.
        db_session (fixture): Database session fixture.
    """
    tomorrow_time, start_time, meeting_data = get_datetimes()
    client.cookies.delete("access_token")
    # Send the request without headers (user not authenticated)
    response = client.post("/schedule-meeting/", json=meeting_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_meeting_scheduling_fail_2(create_access_token_with_wrong_signature, client):
    """
    Test scheduling a meeting with an invalid token signature.

    This test verifies that attempting to schedule a meeting with an access token
    having a wrong signature results in a 401 Unauthorized response with the correct error message.

    Args:
        create_access_token_with_wrong_signature (fixture): Fixture to create a token with a wrong signature.
        client (TestClient): The test client to send requests to the API.
    """
    tomorrow_time, start_time, meeting_data = get_datetimes()

    access_token = create_access_token_with_wrong_signature
    client.cookies.set("access_token", access_token)
    response = client.post("/schedule-meeting/", json=meeting_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_meeting_scheduling_fail_3(register_users_for_login, create_access_token_expired):
    """
    Test scheduling a meeting with an expired token.

    This test verifies that attempting to schedule a meeting with an expired access token
    results in a 401 Unauthorized response with the correct error message.

    Args:
        register_users_for_login (fixture): Fixture to register users for login.
        create_access_token_expired (fixture): Fixture to create an expired token.
    """
    tomorrow_time, start_time, meeting_data = get_datetimes()


    access_token = create_access_token_expired
    client = register_users_for_login
    client.cookies.delete("access_token")
    client.cookies.set("access_token", access_token)
    # Wait for the token to expire
    time.sleep(3)
    response = client.post("/schedule-meeting/", json=meeting_data)
    print(response.json())
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


def test_meeting_scheduling_5(create_valid_access_token_2, register_users_for_login):
    access_token = create_valid_access_token_2
    client = register_users_for_login
    client.cookies.set("access_token", access_token)

    meeting_data = {
        "start_time": "2024/06/09T23:00", # Invalid datetime
        "topic" : "Testing meeting scheduling"
    }

    response = client.post("/schedule-meeting/", json=meeting_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be a valid datetime or date, invalid date separator, expected `-`"


def test_meeting_scheduling_fail_4(create_valid_access_token_2, register_users_for_login):
    """
    Test scheduling a meeting more than once within 7 days.

    This test verifies that attempting to schedule a meeting more than once within 7 days
    results in a 400 Bad Request response with the correct error message.

    Args:
        create_valid_access_token (fixture): Fixture to create a valid access token.
        register_users_for_login (fixture): Fixture to register users for login.
    """
    access_token = create_valid_access_token_2
    client = register_users_for_login
    client.cookies.set("access_token", access_token)

    for i in range(2):
        tomorrow_time, start_time, meeting_data = get_datetimes()
        response = client.post("/schedule-meeting/", json=meeting_data)
        if i == 0:
            assert response.status_code == 200

            response_data = response.json()
            
            assert "start_time" in response_data
            assert "zoom_meeting_id" in response_data
            assert "join_url" in response_data
            assert "id" in response_data
            assert "user_id" in response_data
            assert "advisor_id" in response_data
            assert "topic" in response_data
        else:
            assert response.status_code == 400
            assert response.json()["detail"] == "It has not been 7 days since you last scheduled a meeting"


