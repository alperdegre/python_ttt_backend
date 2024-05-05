from pydantic import BaseModel
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

    user_dict = db_user.__dict__
    del user_dict['password']
    del user_dict['created_at']
    return user_dict

def get_user_by_username(user_name:str, db:Session):
    db_user = db.query(User).filter(User.username == user_name).first()
    if db_user is None:
        return None
    else:
        return db_user.__dict__