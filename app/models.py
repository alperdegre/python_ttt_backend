import datetime
from typing import List 
from pydantic import BaseModel, Field

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    token: str
    user_id: int
    expiry: int
    username: str

class JWTClaims(BaseModel):
    user_id: int
    username: str
    exp: int = Field(default_factory=lambda: int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)).timestamp()))

class LobbyUser(BaseModel):
    id: str
    username: str

class ListedLobby(BaseModel):
    code: str
    owner: str
    players: List[LobbyUser]