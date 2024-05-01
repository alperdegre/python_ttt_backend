from typing import Annotated
from fastapi import Header, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from app.utils import decode_jwt

async def get_user_id(authorization: Annotated[str, Header()]):
    if authorization is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail={"error":"Unauthorized"})

    user_id, error = validate_authorization(authorization)

    if error:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail={"error":"Unauthorized"})

    return user_id
    
def validate_authorization(auth_header:str):
    decoded, error = decode_jwt(auth_header)

    if error:
        return None, error

    return decoded, None