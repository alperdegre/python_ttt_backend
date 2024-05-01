import datetime 
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.db import User

class CreateUserRequest(BaseModel):
    username: str
    password: str

def create_user(user_req:CreateUserRequest,db:Session):
    db_user = User(**user_req.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.__dict__