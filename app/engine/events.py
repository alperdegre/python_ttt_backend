from typing import List, Literal
from pydantic import BaseModel, Field
from enum import Enum

class EventTypeEnum(str, Enum):
    CREATE_LOBBY = 'CREATE_LOBBY'
    JOIN_LOBBY = 'JOIN_LOBBY'
    STATE_SYNC = 'STATE_SYNC'
    LOBBY_NOT_FOUND = 'LOBBY_NOT_FOUND'
    LOBBY_FULL = 'LOBBY_FULL'

class LobbyUser(BaseModel):
    id: str
    username: str

class Event(BaseModel):
    type: EventTypeEnum
    data: str

class CreateLobbyData(BaseModel):
    code: str

class JoinLobbyData(BaseModel):
    player_id: str

class StateSyncData(BaseModel):
    users: List[LobbyUser]

class ErrorData(BaseModel):
    error: str

class Event(BaseModel):
    type: EventTypeEnum
    data: dict

    def serialize_event(self) -> dict:
        return self.model_dump()
    
class CreateLobbyEvent(Event):
    type: EventTypeEnum = EventTypeEnum.CREATE_LOBBY
    data: CreateLobbyData

class StateSyncEvent(Event):
    type: EventTypeEnum = EventTypeEnum.STATE_SYNC
    data: StateSyncData

class LobbyNotFoundEvent(Event):
    type: EventTypeEnum = EventTypeEnum.LOBBY_NOT_FOUND
    data: ErrorData = ErrorData(error="Lobby Not Found")

class LobbyFullEvent(Event):
    type: EventTypeEnum = EventTypeEnum.LOBBY_FULL
    data: ErrorData = ErrorData(error="Lobby Full")

class JoinLobbyEvent(Event):
    type: EventTypeEnum = EventTypeEnum.JOIN_LOBBY
    data: JoinLobbyData
