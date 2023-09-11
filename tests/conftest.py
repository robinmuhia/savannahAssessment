from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config import settings
from app.database import get_db
from app.database import Base
from app import schemas
from app import models
from itsdangerous import TimestampSigner
import json
from base64 import b64encode


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    ("Session started")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# fake session token


def create_session_cookie(data) -> str:
    signer = TimestampSigner(str(settings.session_secret_key))

    return signer.sign(
        b64encode(json.dumps(data).encode('utf-8')),
    ).decode('utf-8')

# create two users for testing


@pytest.fixture
def authorized_client(client, session):
    new_user_data = schemas.UserCreate(
        email="robin@gmail.com", name="robin")
    other_user_data = schemas.UserCreate(
        email="robi@gmail.com", name="robi")
    user_no_phone_data = schemas.UserCreate(
        email="mike@gmail.com", name="mike")
    new_user = models.Customer(**new_user_data.dict())
    other_user = models.Customer(**other_user_data.dict())
    user_no_phone = models.Customer(**user_no_phone_data.dict())
    new_user.phone_number = "0712345678"
    other_user.phone_number = "0713014882"
    session.add(new_user)
    session.add(other_user)
    session.add(user_no_phone)
    session.commit()
    client.headers = {
        **client.headers,
        "session": create_session_cookie({"user": {"name": "robin", "email": "robin@gmail.com"}})
    }

    return client
