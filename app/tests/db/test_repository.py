
from app.db.repository import create_user, CreateUserRequest


def test_create_user(session):
    user = create_user(CreateUserRequest(username="alper", password="test"), session)

    assert user['username'] == "alper"
    assert user['password'] == "test"
    