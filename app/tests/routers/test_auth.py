
from unittest.mock import patch
import bcrypt
from fastapi import status

def test_signup_success(client):
    username = "signup_success_user"
    password = "signup_success_pw"

    response = client.post("/auth/signup", json={"username":username, "password":password})

    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert 'token' in json_response
    assert 'user_id' in json_response
    assert 'expiry' in json_response
    assert 'username' in json_response

def test_signup_existing_user(client):
    username = "signup_success_user"
    password = "signup_success_pw"


    with patch('app.routers.auth.get_user_by_username', return_value=True):
        response = client.post("/auth/signup", json={"username":username, "password":password})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        json_response = response.json()
        assert json_response == {"detail":"User already exists"}

def test_login_success(client):
    username = "signup_success_user"
    password = "signup_success_pw"

    with patch('app.routers.auth.get_user_by_username', return_value={"id":"1", "password":password}), patch('app.routers.auth.compare_password', return_value=True):
        response = client.post("/auth/login", json={"username":username, "password":password})

        json_response = response.json()

        assert 'token' in json_response
        assert 'user_id' in json_response
        assert 'expiry' in json_response
        assert 'username' in json_response


def test_login_user_does_not_exist(client):
    username = "signup_user_does_not_exist_user"
    password = "signup_user_does_not_exist_pw"

    response = client.post("/auth/login", json={"username":username, "password":password})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_response = response.json()
    assert json_response == {"detail":"User does not exist"}


def test_login_pw_error(client):
    username = "signup_user_user"
    password = "signup_user_pw"
    encoded = password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(encoded, salt).decode('utf-8')

    wrong_pw = "wrong_pw"

    with patch('app.routers.auth.get_user_by_username', return_value={"id":"1", "password":hashed}):
        response = client.post("/auth/login", json={"username":username, "password":wrong_pw})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        json_response = response.json()
        assert json_response == {"detail":"Incorrect username or password"}
