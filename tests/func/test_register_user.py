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


def test_register_user_fail_1(register_users_for_login):
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

    client = register_users_for_login
    expected_message = "Email alredy registered"
    response = client.post("/register", json= user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_register_user_fail_2(register_users_for_login):
    """
    Given a database session which has been used to insert a user, the function tries to add another new
    user with a phone number alredy being used.
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "example2@email.com",
        "plain_password": "janesmithpassword",
        "phone_number" : "+573102345670"
    }

    client = register_users_for_login
    expected_message = "Phone number alredy registered"
    response = client.post("/register", json= user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == expected_message


def test_register_user_fail_3(register_users_for_login):
    """
    Given a database session which has been used to insert a user, the function tries to add another new
    user with a document alredy being used.
    """
    user_data = {
        "first_name": "Jane",
        "lastname": "Smith",
        "email": "example2@email.com",
        "plain_password": "janesmithpassword",
        "document" : "100482456"   
    }

    client = register_users_for_login
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
        "email": "example2@email.com",
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
    response = client.post("/register", json=user_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."


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
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid email address: The part after the @-sign is not valid. It should have a period."


def test_register_user_fail_11(client):
    """
    Given a database session, the function tries to register a user with an unexpected field in the data
    """
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "email@example.com",
        "plain_password": "anypassordisok",
        "incorrect_field": "not_supposed_to_pass"
    }
    response = client.post("/register", json= user_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"


def test_register_user_fail_12(client):
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "email@example.com",
        "plain_password": "anypassordisok",
        "phone_number" : "3184526541"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid phone number"


def test_register_user_fail_13(client):
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "email@example.com",
        "plain_password": "anypassordisok",
        "phone_number" : "318243"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at least 7 characters"

def test_register_user_fail_14(client):
    user_data = {
        "first_name": 5,
        "lastname": "Doe",
        "email": "email@example.com",
        "plain_password": "anypassordisok",
        "phone_number" : "318243"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "first_name" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"


def test_register_user_fail_15(client):
    user_data = {
        "first_name": "Matheww",
        "lastname": 534343,
        "email": "email@example.com",
        "plain_password": "anypassordisok",
        "phone_number" : "318243"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "lastname" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"


def test_register_user_fail_16(client):
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": 243654.33,
        "plain_password": "anypassordisok",
        "phone_number" : "318243"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"


def test_register_user_fail_17(client):
    user_data = {
        "first_name": "Matheww",
        "lastname": "Doe",
        "email": "email@example.com",
        "plain_password": 2324221,
        "phone_number" : "+573113291234"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "plain_password" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"