

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.repository import CreateUserRequest, create_user, get_user_by_username
from app.models import AuthRequest, AuthResponse, JWTClaims
from app.utils import compare_password, create_jwt, hash_password


router = APIRouter(
    prefix="/auth"
)

@router.post("/signup")
async def signup(req: AuthRequest, db:Session = Depends(get_db)):
    body = req.model_dump()
    username = body['username']

    existing_user = get_user_by_username(username, db)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    password = body['password']
    
    hashed = hash_password(password)

    user = create_user(CreateUserRequest(username=username, password=hashed), db)

    jwt_claims = JWTClaims(user_id=user['id'], username=username)

    jwt = create_jwt(jwt_claims)

    expiry = jwt_claims.model_dump()['exp']

    response = AuthResponse(token=jwt, user_id=user['id'], username=username, expiry=expiry)

    return response

    
@router.post("/login")
async def login(req: AuthRequest, db:Session = Depends(get_db)):
    body = req.model_dump()
    username = body['username']
    password = body['password']

    existing_user = get_user_by_username(username, db)

    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    
    is_correct_pw = compare_password(existing_user['password'], password) 

    if is_correct_pw is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    jwt_claims = JWTClaims(user_id=existing_user['id'], username=username)

    jwt = create_jwt(jwt_claims)

    expiry = jwt_claims.model_dump()['exp']

    response = AuthResponse(token=jwt, user_id=existing_user['id'], username=username, expiry=expiry)

    return response

@app.get("/hello-world")
async def root():
    return {"message":"Hello World"}