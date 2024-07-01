from api.models import User, PasswordResetToken

def test_password_recovery(register_users_for_login):
    client = register_users_for_login
    response = client.get("/password-recovery/johndoe@email.com")

    assert response.status_code == 200
    assert response.json()["msg"] == "The link to reset your password has been sent, please check your email."


def test_password_recovery_fail_1(register_users_for_login):
    client = register_users_for_login
    response = client.get("/password-recovery/emailnotregistered@email.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "The user doesn't exist."


def test_password_recovery_fail_2(register_users_for_login):
    client = register_users_for_login
    for i in range(6):
        response = client.get("/password-recovery/invalidemail")
        if i < 5:
            assert response.status_code == 404
            assert response.json()["detail"] == "The user doesn't exist."
        else:
            assert response.status_code == 429
            assert response.json()["detail"] == "Rate limit exceeded, please try again later."


def test_reset_password(register_users_for_login, db_session):
    client = register_users_for_login
    response = client.get("/password-recovery/janesmith@email.com")
    
    user: User = db_session.query(User).filter(User.email == "janesmith@email.com").first()
    token: PasswordResetToken = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == user.id, PasswordResetToken.is_used == False)
        .first()
    )

    reset_data = {
        "token": token.token,
        "new_password": "janesmithdifferentpassword",
        "new_password_confirm": "janesmithdifferentpassword"
    } 
    response = client.patch("/reset-password", json=reset_data)

    assert response.status_code == 200
    assert response.json()["msg"] == "The password has been updated succesfully"


def test_reset_password_fail_1(register_users_for_login, db_session):
    client = register_users_for_login
    response = client.get("/password-recovery/janesmith@email.com")

    user: User = db_session.query(User).filter(User.email == "janesmith@email.com").first()
    token: PasswordResetToken = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == user.id, PasswordResetToken.is_used == False)
        .first()
    )

    reset_data = {
        "token": token.token,
        "new_password": "passwordsarenotmatching",
        "new_password_confirm": "passwordsdontmatch"
    }
    response = client.patch("/reset-password", json=reset_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords don't match."


def test_reset_password_fail_2(register_users_for_login, db_session):
    client = register_users_for_login
    response = client.get("/password-recovery/janesmith@email.com")

    user: User = db_session.query(User).filter(User.email == "janesmith@email.com").first()
    token: PasswordResetToken = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == user.id, PasswordResetToken.is_used == False)
        .first()
    )

    reset_data = {
        "token": token.token,
        "new_password": "short",
        "new_password_confirm": "short"
    }
    response = client.patch("/reset-password", json=reset_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 7 characters long"


def test_reset_password_fail_3(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "token": "invalid_token",
        "new_password": "short",
        "new_password_confirm": "short"
    }
    response = client.patch("/reset-password", json=reset_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_reset_password_fail_4(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "new_password": "short",
        "new_password_confirm": "short"
    }
    response = client.patch("/reset-password", json=reset_data)

    assert response.status_code == 422
    assert "token" in response.json()["detail"][0]["loc"] 


def test_reset_password_fail_5(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "token": "invalid_token",
        "new_password_confirm": "short"
    }
    response = client.patch("/reset-password", json=reset_data)

    assert response.status_code == 422
    assert "new_password" in response.json()["detail"][0]["loc"] 


def test_reset_password_fail_6(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "token": "invalid_token",
        "new_password": "short"
    }
    response = client.patch("/reset-password", json=reset_data)
    assert response.status_code == 422
    assert "new_password_confirm" in response.json()["detail"][0]["loc"] 


def test_reset_password_fail_6(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "token": 534633,
        "new_password": "short",
        "new_password_confirm": "short"
    }
    response = client.patch("/reset-password", json=reset_data)
    assert response.status_code == 422
    assert "token" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"


def test_reset_password_fail_6(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "token": "invalid_token",
        "new_password": 43532,
        "new_password_confirm": "newpasswordjane"
    }
    response = client.patch("/reset-password", json=reset_data)
    assert response.status_code == 422
    assert "new_password" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"


def test_reset_password_fail_6(register_users_for_login):
    client = register_users_for_login
    reset_data = {
        "token": "invalid_token",
        "new_password": "newpasswordjane",
        "new_password_confirm": 43532
    }
    response = client.patch("/reset-password", json=reset_data)
    assert response.status_code == 422
    assert "new_password_confirm" in response.json()["detail"][0]["loc"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"