from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.db import Base, get_db
from app.engine.engine import GameEngine, get_engine
from app.models import LobbyUser
from ..main import app

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
def client(session):
    """
    Creates a TestClient for route testing. Overrides db creation with a test database
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)

@pytest.fixture()
def game_engine():
    """
    Creates a test game engine
    """
    def override_get_engine():
        return test_game_engine
    
    app.dependency_overrides[get_engine] = override_get_engine
    
    yield test_game_engine

@pytest.fixture
def lobby_user():
    return LobbyUser(id="test_user", username="Test_User")

@pytest.fixture
def mock_websocket():
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    return ws