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
        "username" : "johnson@email.com"
    }
    client = register_users_for_login
    response = client.post("/login", data= user_data)

    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]


def test_login_user_fail_4(register_users_for_login):
    user_data = {
        "password" : "robertjohnsonpassword"
    }
    client = register_users_for_login
    response = client.post("/login", data= user_data)

    assert response.status_code == 422
    assert "username" in response.json()["detail"][0]["loc"]


def test_login_user_fail_5(register_users_for_login):
    user_data = {
        "username" : "", # Incorrect email
        "password" : "" # Correct password
    }
    client = register_users_for_login
    response = client.post("/login", data= user_data)

    assert response.status_code == 422
    assert "username" in response.json()["detail"][0]["loc"]
    assert "password" in response.json()["detail"][1]["loc"]



def test_login_user_fail_6(register_users_for_login):
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


def test_login_user_after_rate_limit(register_users_for_login):
    user_data = {
        "username" : "robertjohnson@email.com",
        "password" : "robertjohnsonpassword"
    }

    client = register_users_for_login
    for i in range(6):
        response = client.post("/login", data= {"username": "incorrectemail", "password": "incorrectpassword"})
    
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many login attempts. Please try again later."

    # For tests I established 1 sec rate limiting period.
    time.sleep(1)

    response = client.post("/login", data= user_data)
    assert response.status_code == 200
    assert response.cookies.get("access_token") is not None