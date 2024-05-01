from app.dependencies import validate_authorization
from unittest.mock import patch

def test_validate_authorization_success():
    with patch('app.dependencies.decode_jwt', return_value=("decoded", None)):
        validated, error = validate_authorization("test_auth_header")
        assert error is None
        assert validated is "decoded"


def test_validate_authorization_failure():
    with patch('app.dependencies.decode_jwt', return_value=(None, Exception)):
        validated, error = validate_authorization("test_auth_header")
        assert error is Exception
        assert validated is None

