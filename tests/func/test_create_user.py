from api.services.email_service import EmailService
from api.services.user_service import UserService
from api.schemas import UserCreate


def test_register_user(client):
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


def test_register_user_fail_1(register_users_to_fail):
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

    client = register_users_to_fail
    expected_message = "Email alredy registered"
    response = client.post("/register", json= user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_register_user_fail_2(register_users_to_fail):
    """
    Given a database session which has been used to insert a user, the function tries to add another new
    user with a phone number alredy being used.
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "example@email.com",
        "plain_password": "janesmithpassword",
        "phone_number" : "+573102345670"
    }

    client = register_users_to_fail
    expected_message = "Phone number alredy registered"
    response = client.post("/register", json= user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_register_user_fail_3(register_users_to_fail):
    """
    Given a database session which has been used to insert a user, the function tries to add another new
    user with a document alredy being used.
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "example@email.com",
        "plain_password": "janesmithpassword",
        "document" : "100482456"   
    }

    client = register_users_to_fail
    expected_message = "Document alredy registered"
    response = client.post("/register", json= user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_register_user_fail_4(client):
    """
    Given a database session, the function tries to register a user with a password not permitted
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "example@email.com",
        "plain_password": "janes"
    }

    expected_message = "Password must be at least 7 characters long."
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_register_user_fail_5(client):
    """
    Given a database session, the function tries to register a user with missing fields (In this case 'email')
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "plain_password": "janesstarlett"
    }

    response = client.post("/register", json=user_data)

    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]


def test_register_user_fail_6(client):
    """
    Given a database session, the function tries to register a user with missing fields (In this case 'first_name')
    """
    user_data = {
        "lastname": "Smith",
        "plain_password": "janesstarlett",
        "email": "example@email.com",
    }

    response = client.post("/register", json=user_data)

    assert response.status_code == 422
    assert "first_name" in response.json()["detail"][0]["loc"]


def test_register_user_fail_7(client):
    """
    Given a database session, the function tries to register a user with missing fields (In this case 'lastname')
    """
    user_data = {
        "first_name": "Jane",
        "plain_password": "janesstarlett",
        "email": "example@email.com",
    }

    response = client.post("/register", json=user_data)

    assert response.status_code == 422
    assert "lastname" in response.json()["detail"][0]["loc"]


def test_register_user_fail_8(client):
    """
    Given a database session, the function tries to register a user with missing fields (In this case 'plain_password')
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "example@email.com",
    }

    response = client.post("/register", json=user_data)

    assert response.status_code == 422
    assert "plain_password" in response.json()["detail"][0]["loc"]


def test_register_user_fail_9(client):
    """
    Given a database sesion, the function tries to register a user with a not valid email address
    """
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "exampleemail.com",
        "plain_password": "mathewwisnotdoe"
    }

    expected_message = "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."
    response = client.post("/register", json=user_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == expected_message


def test_register_user_fail_10(client):
    """
    Given a database session, the function tries to register a user with a not valid email address.
    """
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "unvalidemail@educo",
        "plain_password": "anypassordisok"
    }

    response = client.post("/register", json= user_data)
    expected_message = "value is not a valid email address: The part after the @-sign is not valid. It should have a period."
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == expected_message    