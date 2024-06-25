import pytest 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.database import Base, get_db

from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_TEST_DATABASE_URL=os.getenv("SQLALCHEMY_TEST_DATABASE_URL")

engine_test = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.create_all(bind=engine_test)

@pytest.fixture()
def db_session():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def _get_test_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = _get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_users_to_fail(client):
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
