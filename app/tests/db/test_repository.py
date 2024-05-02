
from app.db.repository import create_user, CreateUserRequest, get_user_by_username


def test_create_user(session):
    user = create_user(CreateUserRequest(username="alper", password="test"), session)

    assert user['username'] == "alper"
    assert 'password' not in user
    assert 'created_at' not in user
    
def test_get_user_by_username(session):
    user = get_user_by_username('test', session)

    assert user is None

    username = 'test_get_user'

    create_user(CreateUserRequest(username=username, password="test"), session)

    existing_user = get_user_by_username(username,session)

    assert existing_user is not None
    assert existing_user.username == username