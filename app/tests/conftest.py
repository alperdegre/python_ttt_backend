from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.db import Base, get_db
from app.dependencies import get_user_id
from app.engine.engine import GameEngine, get_engine
from app.models import LobbyUser
from app.main import app

DATABASE_URL = "sqlite:///"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
test_game_engine = GameEngine()

@pytest.fixture()
def session():
    """
    Creates a new database session for testing. Sets up a fresh database everytime tests are run.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def game_engine():
    return test_game_engine

@pytest.fixture()
def client(session):
    """
    Creates a TestClient for route testing. Overrides every dependency to work with tests
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    def override_get_engine():
        return test_game_engine
    
    def override_get_user_id():
        return "TEST_USER"
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_engine] = override_get_engine
    app.dependency_overrides[get_user_id] = override_get_user_id
    
    yield TestClient(app)

@pytest.fixture()
def user_id_client(session):
    """
    Creates a TestClient for auth middleware testing.
    """
    def override_get_engine():
        return test_game_engine
    
    app.dependency_overrides[get_engine] = override_get_engine
    yield TestClient(app)

@pytest.fixture()
def async_client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    def override_get_engine():
        return test_game_engine
    
    def override_get_user_id():
        return "TEST_USER"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_engine] = override_get_engine
    app.dependency_overrides[get_user_id] = override_get_user_id

    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.fixture
def lobby_user():
    return LobbyUser(id="test_user", username="Test_User")

@pytest.fixture
def mock_websocket():
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    return ws