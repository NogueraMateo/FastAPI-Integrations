from api.services.email_service import EmailService
from api.services.user_service import UserService
from api.schemas import UserCreate


def test_create_user(client):
    """
    Given a database session, a new user is registered
    """
    user_data = { 
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "example@email.com",
        "plain_password": "testpassword"
    }

    response = client.post("/register", json= user_data)
    expected_message = {"message" : "User registered successfully, please check your email to confirm your account."}

    assert response.status_code == 201
    assert response.json() == expected_message


def test_create_user_fail_1(created_users_to_fail_with_email):
    """
    Given a database session alredy with some users registered, the function tries to add a new user with
    an email alredy in use. 
    """
    user_data = {
        "first_name": "Julius",
        "lastname": "Dopas",
        "email": "janesmith@email.com",
        "plain_password": "juliusdopaspassword"
    }

    client = created_users_to_fail_with_email
    expected_message = "Email alredy registered"
    response = client.post("/register", json= user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_create_user_fail_2(create_user_to_fail_with_phone_number):
    """
    Given a database session which has been used to insert a user, the function tries to add another new
    user with a phone number alredy being used.
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "janesmith@email.com",
        "plain_password": "janesmithpassword",
        "phone_number" : "+573102345670"
    }

    client = create_user_to_fail_with_phone_number
    expected_message = "Phone number alredy registered"
    response = client.post("/register", json= user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == expected_message
