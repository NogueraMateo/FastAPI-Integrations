import time


def test_login_user(register_users_for_login):
    user_data = {
        "username" : "robertjohnson@email.com",
        "password" : "robertjohnsonpassword"
    }

    client = register_users_for_login
    response = client.post("/login", data= user_data)

    assert response.status_code == 200
    assert response.cookies.get("access_token") is not None


def test_login_user_fail_1(register_users_for_login):
    user_data = {
        "username" : "robertjohnson@email.com", # Correct email
        "password" : "robertjohnson" # Incorrect password
    }

    client = register_users_for_login
    response = client.post("/login", data= user_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_user_fail_2(register_users_for_login):
    user_data = {
        "username" : "johnson@email.com", # Incorrect email
        "password" : "robertjohnsonpassword" # Correct password
    }

    client = register_users_for_login
    response = client.post("/login", data= user_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_user_fail_3(register_users_for_login):
    user_data = {
        "username" : "incorrectemail",
        "password" : "incorrectpassword"
    }

    client = register_users_for_login
    for i in range(6):
        response = client.post("/login", data= user_data)
        if i < 5:
            assert response.status_code == 401
            assert response.json()["detail"] == "Incorrect email or password"
        else:
            assert response.status_code == 429
            assert response.json()["detail"] == "Too many login attempts. Please try again later."