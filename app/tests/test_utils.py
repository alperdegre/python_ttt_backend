import pytest
from app.models import JWTClaims
from app.utils import compare_password, create_jwt, create_lobby_code, decode_jwt, hash_password
from unittest.mock import patch
import jwt

def test_create_and_decode_jwt_success():
    claims = JWTClaims(user_id=1, username="test")

    with patch('os.getenv', return_value="TEST_SECRET"):
        encoded = create_jwt(claims)
        assert isinstance(encoded, str), "Encoded token must be a string"

        decoded, error = decode_jwt(encoded)
        assert error is None
        assert decoded['user_id'] == 1
        assert decoded['username'] == "test"

@pytest.mark.parametrize('exception, expected_message', [
    (jwt.InvalidSignatureError, "Invalid secret key"),
    (jwt.DecodeError, "Error while decoding"),
    (jwt.ExpiredSignatureError, "JWT has expired"),
    (Exception, "An unexpected error has occured")
])
def test_decode_jwt_errors(exception, expected_message):
    invalid_token = "invalid_token"

    with patch('os.getenv', return_value="TEST_SECRET"), patch('jwt.decode', side_effect=exception):
        decoded, error = decode_jwt(invalid_token)
        assert decoded is None
        assert error == expected_message

def test_hash_and_compare_password():
    test_pw = 'test_pw'

    hashed = hash_password(test_pw)

    assert isinstance(hashed, bytes)
    
    result = compare_password(hashed.decode('utf-8'), test_pw)

    assert result is True

def test_wrong_password_compare():
    test_pw = 'test_pw'
    wrong_pw = 'wrong_pw'

    hashed_wrong = hash_password(wrong_pw).decode('utf-8')

    result = compare_password(hashed_wrong, test_pw)

    assert result is False

def test_create_lobby_code():
    code = create_lobby_code()

    assert code.isupper()
    assert len(code) == 5