from fastapi import HTTPException
import pytest
from app.dependencies import get_user_id, validate_authorization
from unittest.mock import patch
from starlette.status import HTTP_401_UNAUTHORIZED

def test_validate_authorization_success():
    with patch('app.dependencies.decode_jwt', return_value=({'user_id': 1, 'username': 'TEST_USER', 'exp': 1715273978}, None)):
        validated, error = validate_authorization("test_auth_header")
        assert error is None
        assert validated['user_id'] is 1
        assert validated['username'] is "TEST_USER"

def test_validate_authorization_failure():
    with patch('app.dependencies.decode_jwt', return_value=(None, Exception)):
        validated, error = validate_authorization("test_auth_header")
        assert error is Exception
        assert validated is None

@pytest.mark.anyio
async def test_get_user_id_authorization_doesnt_exist():
    try:
        await get_user_id(None)
    except HTTPException as e:
        assert e.status_code == HTTP_401_UNAUTHORIZED
        assert 'error' in e.detail
        assert e.detail['error'] == "Authorization Missing"

@pytest.mark.anyio
async def test_get_user_id_authorization_wrong_jwt():
    try:
        await get_user_id({'authorization':"WRONG_JWT"})
    except HTTPException as e:
        assert e.status_code == HTTP_401_UNAUTHORIZED
        assert 'error' in e.detail
        assert e.detail['error'] == "Unauthorized"

@pytest.mark.anyio
async def test_get_user_id_success():
    with patch('app.dependencies.decode_jwt', return_value=({'user_id': 1, 'username': 'TEST_USER', 'exp': 1715273978}, None)):
        result = await get_user_id({'authorization':"WRONG_JWT"})

        assert result == "1"
        assert isinstance(result, str)