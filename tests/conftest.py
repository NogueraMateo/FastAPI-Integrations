from dotenv import load_dotenv
import os

load_dotenv()

os.environ["RATE_LIMIT_PERIOD"] = "1"
os.environ["CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES"] = "0.2"


import pytest 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.database import Base, get_db
from api.services.token_service import EmailConfirmationTokenService


SQLALCHEMY_TEST_DATABASE_URL=os.getenv("SQLALCHEMY_TEST_DATABASE_URL")

engine_test = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.create_all(bind=engine_test)

@pytest.fixture(scope="module")
def db_session():
    """
    Fixture to set up a test database session.

    This fixture creates a connection to the test database and a session bound to it.
    A transaction is started at the beginning and rolled back at the end to ensure
    that each test runs in isolation without affecting the database state.

    Yields:
        session: The SQLAlchemy session object.
    """
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(db_session):
    """
    Fixture to set up a FastAPI test client with a test database session.

    This fixture overrides the FastAPI dependency for the database session with a test session.
    It creates a TestClient instance for sending requests to the FastAPI app.

    Args:
        db_session: The test database session fixture.

    Yields:
        client: The FastAPI TestClient instance.
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = _get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def register_users_for_login(client):
    """
    Fixture to register a set of users for login tests.

    This fixture registers multiple users in the test database by sending POST requests to the 
    /register endpoint. These users are used in login tests to verify the authentication flow.

    Args:
        client: The FastAPI TestClient instance.

    Yields:
        client: The FastAPI TestClient instance with registered users.
    """
    users_to_add = [
        {
            "first_name" : "John",
            "lastname":"Doe",
            "email" : "johndoe@email.com",
            "plain_password" : "johndoepassword"
        },
        {
            "first_name": "Jane",
            "lastname": "Smith",
            "email": "janesmith@email.com",
            "plain_password": "janesmithpassword",
            "phone_number" : "+573102345670"

        },
        {
            "first_name": "Robert",
            "lastname": "Johnson",
            "email": "robertjohnson@email.com",
            "document" : "100482456",
            "plain_password": "robertjohnsonpassword"
        }
    ]
    for user in users_to_add:
        response = client.post("/register", json=user)

    return client


@pytest.fixture(scope="module")
async def invalid_token_for_confirmation(db_session):
    """
    Fixture to generate an invalid token for email confirmation.

    This fixture creates an invalid email confirmation token to be used in tests 
    that verify the handling of invalid tokens.

    Args:
        db_session: The test database session fixture.

    Yields:
        str: The invalid token string.
    """
    service = EmailConfirmationTokenService(db_session)
    token_data = {"sub" : "robertjohnson@email.com", "aud" : "email-confirmation"}
    token, ex = await service.create_token(token_data, secret_key= "invalid_string_tosign_token")
    return token


# docker-compose exec web pytest tests/func/test_confirm_user.py