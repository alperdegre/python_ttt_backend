

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models import AuthRequest


router = APIRouter(
    prefix="/auth"
)

@router.post("/signup")
async def signup(req: AuthRequest, db:Session = Depends(get_db)):
    body = req.model_dump()
    pass

    # Need check user by username func

    
@router.post("/login")
async def login(req: AuthRequest, db:Session = Depends(get_db)):
    pass