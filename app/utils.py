import jwt
import os
import bcrypt
from app.models import JWTClaims
from Crypto.Hash import SHA256

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
    
def hash_password(password:str):
    encoded = password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(encoded, salt)

    return hashed

def compare_password(hashed:str, normal:str) -> bool:
    hash_encoded = hashed.encode('utf-8')
    normal_encoded = normal.encode('utf-8')
    result = bcrypt.checkpw(normal_encoded, hash_encoded)

    return result

def create_lobby_code():
    random_bytes = os.urandom(32)
    hash_object = SHA256.new(data=random_bytes)
    random_hash = hash_object.hexdigest()
    lobby_code = random_hash[:5].upper()

    return lobby_code

def create_game_code():
    random_bytes = os.urandom(32)
    hash_object = SHA256.new(data=random_bytes)
    random_hash = hash_object.hexdigest()
    game_code = random_hash[:10]

    return game_code