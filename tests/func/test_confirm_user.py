from api.models import User, EmailConfirmationToken
import time
import pytest

def test_confirm_user_account_1(client, db_session):
    """
    Test that a user account can be successfully confirmed with a valid token.

    Steps:
    - Register a new user.
    - Retrieve the user and their email confirmation token from the database.
    - Confirm the user's account using the token.
    - Check that the user's account is activated.

    Args:
    - client: Test client.
    - db_session: Database session fixture.
    """

    user_data = {
        "first_name": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "plain_password": "testpassword"
    }

    response = client.post("/register", json=user_data)
    assert  response.status_code == 201

    db: TestingSessionLocal = db_session
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None

    token_entry = db.query(EmailConfirmationToken).filter(EmailConfirmationToken.user_id == user.id).first()
    assert token_entry is not None  
    token = token_entry.token

    confirm_data = {"token" : token}
    response = client.patch("/confirm-user-account", json=confirm_data)
    assert response.status_code == 200
    assert response.json()["message"] == "User account activated successfully"

    updated_user = db.query(User).filter(User.email == user_data["email"]).first()
    assert updated_user.is_active


def test_confirm_user_account_2(register_users_for_login, db_session):
    """
    Test that confirming an account with a valid token twice results in an error.

    Steps:
    - Register multiple users.
    - Retrieve one user and their email confirmation token from the database.
    - Confirm the user's account using the token.
    - Attempt to confirm the user's account again with the same token.
    - Check that the second confirmation attempt fails.

    Args:
    - register_users_for_login: Fixture to register multiple users.
    - db_session: Database session fixture.
    """
    client = register_users_for_login
    db: TestingSessionLocal = db_session

    user = db.query(User).filter(User.email == "janesmith@email.com").first()
    assert user is not None

    token_entry = db.query(EmailConfirmationToken).filter(EmailConfirmationToken.user_id == user.id).first()
    assert token_entry is not None  
    token = token_entry.token

    confirm_data = {"token" : token}
    response = client.patch("/confirm-user-account", json=confirm_data)

    assert response.status_code == 200
    assert response.json()["message"] == "User account activated successfully"

    updated_user = db.query(User).filter(User.email == "janesmith@email.com").first()
    assert updated_user.is_active

    response = client.patch("/confirm-user-account", json=confirm_data)
    updated_token_entry: EmailConfirmationToken = db.query(EmailConfirmationToken).filter(EmailConfirmationToken.token == token).first()

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"
    assert updated_token_entry.is_used


@pytest.mark.asyncio
async def test_confirm_user_account_fail_1(invalid_token_for_confirmation, client):
    """
    Test that confirming an account with an invalid token results in an error.

    Steps:
    - Generate an invalid token.
    - Attempt to confirm a user account using the invalid token.
    - Check that the confirmation attempt fails.

    Args:
    - invalid_token_for_confirmation: Fixture to generate an invalid token.
    - client: Test client.
    """
    token = await invalid_token_for_confirmation
    confirm_data = {"token" : token}
    response = client.patch("/confirm-user-account", json=confirm_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_confirm_user_account_fail_2(register_users_for_login, db_session):
    """
    Test that confirming an account with an expired token results in an error.

    Steps:
    - Register multiple users.
    - Retrieve one user and their email confirmation token from the database.
    - Wait for the token to expire.
    - Attempt to confirm the user's account using the expired token.
    - Check that the confirmation attempt fails.

    Args:
    - register_users_for_login: Fixture to register multiple users.
    - db_session: Database session fixture.
    """
    client = register_users_for_login
    db: TestingSessionLocal = db_session

    user = db.query(User).filter(User.email == "johndoe@email.com").first()
    assert user is not None

    token_entry = db.query(EmailConfirmationToken).filter(EmailConfirmationToken.user_id == user.id).first()
    assert token_entry is not None  
    token = token_entry.token

    confirm_data = {"token" : token}
    time.sleep(7)

    response = client.patch("/confirm-user-account", json=confirm_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"

    updated_user = db.query(User).filter(User.email == "johndoe@email.com").first()
    assert not updated_user.is_active


def test_confirm_user_account_fail_3(client):
    invalid_token_data = {"token" : "invalidtoken", "extra_field" : "extra_field_not_permitted"}
    response = client.patch("/confirm-user-account", json=invalid_token_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"


def test_confirm_user_account_fail_4(client):
    invalid_token_data = {"token" : ""}
    response = client.patch("/confirm-user-account")

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"

