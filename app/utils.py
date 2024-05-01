import jwt
import os

from app.models import JWTClaims


def create_jwt(data: JWTClaims):
    encoded = jwt.encode(data.model_dump(), os.getenv("JWT_SECRET", ""), algorithm="HS256")
    return encoded

def decode_jwt(token: str):
    try:
        decoded = jwt.decode(token, os.getenv("JWT_SECRET", ""), algorithms=["HS256"])
        return decoded, None
    except jwt.InvalidSignatureError:
        print("Invalid secret key")
        return None, "Invalid secret key"
    except jwt.DecodeError:
        print("Error decoding jwt")
        return None, "Error while decoding"
    except jwt.ExpiredSignatureError:
        print("JWT Expired")
        return None, "JWT has expired"
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None, "An unexpected error has occured"