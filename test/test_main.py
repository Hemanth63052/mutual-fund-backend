from dotenv import load_dotenv
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db.pg.sessions import get_db
from src.db.pg.sessions import Base

load_dotenv()

import pytest
from fastapi.testclient import TestClient
from main import app


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine, checkfirst=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "dummy.hemanth@gmail.com",
            "first_name": "Dummy",
            "last_name": "User",
            "password": "strongpassword123",
            "phone_number": "1234567890",
            "address": "123 Main St"
        }
    )
    assert response.status_code == 200

def test_login_user(client):
    # First, create a user to log in
    response = client.post(
        "/api/auth/login",
        json={
            "email": "dummy.hemanth@gmail.com",
            "password": "strongpassword123",
        })

    assert response.status_code == 200
