import datetime 
from pydantic import BaseModel, Field


class JWTClaims(BaseModel):
    user_id: int
    username: str
    exp: int = Field(default_factory=lambda: int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)).timestamp()))