import time

def test_successful_meeting_deletion(create_meeting_to_edit, create_admin_access_token):
    meeting_id, client = create_meeting_to_edit
    access_token = create_admin_access_token

    client.cookies.set("access_token", access_token)

    response = client.delete(f"/delete/meeting/{meeting_id}")
    client.cookies.delete("access_token")
    assert response.status_code == 200
    response_data = response.json()
    assert  "zoom_meeting_id" in response_data
    assert  response_data["zoom_meeting_id"] == meeting_id
    

def test_meeting_deletion_fail_1(client, inactive_admin_access_token):
    access_token = inactive_admin_access_token
    meeting_id = "23454624" # Fake meeting_id number
    
    client.cookies.set("access_token", access_token)
    response = client.delete(f"/delete/meeting/{meeting_id}")
    client.cookies.delete("access_token")
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"


def test_meeting_deletion_fail_2(client, create_access_token_with_wrong_signature):
    access_token = create_access_token_with_wrong_signature
    meeting_id = "23454624"
    client.cookies.set("access_token", access_token)
    response = client.delete(f"/delete/meeting/{meeting_id}")
    client.cookies.delete("access_token")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_meeting_deletion_fail_3(client, create_valid_access_token_3):
    access_token = create_valid_access_token_3
    meeting_id = "23454624"
    client.cookies.set("access_token", access_token)
    response = client.delete(f"/delete/meeting/{meeting_id}")
    client.cookies.delete("access_token")
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"

def test_meeting_deletion_fail_4(client, create_access_token_expired):
    access_token= create_access_token_expired
    meeting_id = "23454624"
    
    client.cookies.set("access_token", access_token)
    time.sleep(3)
    response = client.delete(f"/delete/meeting/{meeting_id}")
    client.cookies.delete("access_token")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"