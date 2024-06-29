from dotenv import load_dotenv
import os
load_dotenv()

os.environ["RATE_LIMIT_PERIOD"] = "1"
os.environ["CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES"] = "0.1"


import pytest 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError


from api.main import app
from api.database import Base, get_db
from api.services.token_service import EmailConfirmationTokenService
from api.models import Advisor, User
from api.config.constants import ACCESS_TOKEN_SECRET_KEY, ALGORITHM, EMAIL_CONFIRMATION_SECRET_KEY
from api.models import crypt
from .func.test_meeting_scheduling import get_datetimes


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
async def invalid_token_for_confirmation():
    """
    Fixture to generate an invalid token for email confirmation.

    This fixture creates an invalid email confirmation token to be used in tests 
    that verify the handling of invalid tokens.

    Args:
        db_session: The test database session fixture.

    Yields:
        str: The invalid token string.
    """
    token_data = {"sub" : "robertjohnson@email.com", "aud" : "email-confirmation"}
    return generate_jwt(token_data, "invalid_string_tosign_token", ALGORITHM, timedelta(minutes=3))


@pytest.fixture(scope="module")
def insert_advisors_for_meeting_scheduling(db_session):
    db: TestingSessionLocal = db_session
    advisors_to_add = [
        Advisor(name= "John Doe", email= "johndoeadvisor1@email.com"),
        Advisor(name= "Alexa Jhonson", email= "alexajhonsonadvisor2@email.com")
    ]
    
    for advisor in advisors_to_add:
        db.add(advisor)
    
    db.commit()
        

@pytest.fixture(scope="module")
def create_access_token_with_wrong_signature():
    data = {"sub" : "janesmith@email.com"}
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=3)
    to_encode.update({'exp' : expire})

    try:
        encoded_jwt = jwt.encode(to_encode, "invalid_secret_key", algorithm="HS256")
        return encoded_jwt
    except Exception as e:
        raise Exception(f"Error encoding JWT: {str(e)}")


@pytest.fixture(scope="module")
def create_access_token_expired():
    data = {"sub" : "robertjohnson@email.com"}
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=2)
    to_encode.update({'exp' : expire})

    try:
        encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise Exception(f"Error encoding JWT: {str(e)}")


def generate_jwt(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expire})

    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt
    except Exception as e:
        raise Exception(f"Error encoding JWT: {str(e)}")


@pytest.fixture(scope="module")
def create_valid_access_token_1():
    data = {"sub" : "robertjohnson@email.com"}
    yield generate_jwt(data, ACCESS_TOKEN_SECRET_KEY, ALGORITHM, timedelta(minutes=3))


@pytest.fixture(scope="module")
def create_valid_access_token_2():
    data = {"sub" : "janesmith@email.com"}
    yield generate_jwt(data, ACCESS_TOKEN_SECRET_KEY, ALGORITHM, timedelta(minutes=3))


@pytest.fixture(scope="module")
def create_admin_access_token(db_session):
    db: TestingSessionLocal = db_session
    admin_password = crypt.hash("admin123")
    admin_user = User(
        first_name= "Admin",
        lastname="API", 
        email= "adminuser@email.com", 
        password_hash= admin_password,
        is_active = True,
        role= "ADMIN")
    
    db.add(admin_user)
    db.commit()

    data = {"sub" : "adminuser@email.com"}
    yield generate_jwt(data, ACCESS_TOKEN_SECRET_KEY, ALGORITHM, timedelta(minutes=3))


@pytest.fixture(scope="module")
def create_meeting_to_edit(register_users_for_login, create_valid_access_token_2, insert_advisors_for_meeting_scheduling):
    client = register_users_for_login
    access_token = create_valid_access_token_2
    tomorrow_time, start_time, meeting_data = get_datetimes()

    client.cookies.set("access_token", access_token)
    response = client.post("/schedule-meeting/", json=meeting_data)
    return (response.json()["zoom_meeting_id"], client)


@pytest.fixture(scope="module")
def inactive_admin_access_token(db_session):
    db: TestingSessionLocal = db_session
    admin_password = crypt.hash("admin123")
    admin_user = User(
        first_name= "Admin",
        lastname="API", 
        email= "adminuser2@email.com", 
        password_hash= admin_password,
        is_active = False,
        role= "ADMIN")
    
    db.add(admin_user)
    db.commit()

    data = {"sub" : "adminuser2@email.com"}
    yield generate_jwt(data, ACCESS_TOKEN_SECRET_KEY, ALGORITHM, timedelta(minutes=3))


@pytest.fixture(scope="module")
def create_valid_access_token_3(db_session):
    db: TestingSessionLocal = db_session
    user: User= db.query(User).filter(User.email == "janesmith@email.com").first()
    user.is_active = True
    db.commit()

    data = {"sub" : "janesmith@email.com"}
    yield generate_jwt(data, ACCESS_TOKEN_SECRET_KEY, ALGORITHM, timedelta(minutes=3))
# docker-compose exec web pytest tests/func/test_confirm_user.py