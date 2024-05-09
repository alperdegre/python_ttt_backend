from typing import Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError
from enum import Enum

from app.models import LobbyUser

class EventTypeEnum(str, Enum):
    CREATE_LOBBY = 'CREATE_LOBBY'
    JOIN_LOBBY = 'JOIN_LOBBY'
    STATE_SYNC = 'STATE_SYNC'
    LOBBY_NOT_FOUND = 'LOBBY_NOT_FOUND'
    LOBBY_FULL = 'LOBBY_FULL'
    INVALID_EVENT = 'INVALID_EVENT'
    LOBBY_STARTING = 'LOBBY_STARTING'
    START_LOBBY = 'START_LOBBY'


class CreateLobbyData(BaseModel):
    code: str

class LobbyStartingData(BaseModel):
    code: str
    starting: bool

class StartLobbyData(BaseModel):
    user_id: str

class StateSyncData(BaseModel):
    owner: str
    code: str
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
    data: LobbyUser

class LobbyStartingEvent(Event):
    type: EventTypeEnum = EventTypeEnum.LOBBY_STARTING
    data: LobbyStartingData

class StartLobbyEvent(Event):
    type: EventTypeEnum = EventTypeEnum.START_LOBBY
    data: StartLobbyData

class InvalidEvent(Event):
    type: EventTypeEnum = EventTypeEnum.INVALID_EVENT
    data: ErrorData = ErrorData(error="Invalid Event")


event_type_to_class: Dict[EventTypeEnum, Type[Event]] = {
    EventTypeEnum.CREATE_LOBBY: CreateLobbyEvent,
    EventTypeEnum.JOIN_LOBBY: JoinLobbyEvent,
    EventTypeEnum.STATE_SYNC: StateSyncEvent,
    EventTypeEnum.LOBBY_NOT_FOUND: LobbyNotFoundEvent,
    EventTypeEnum.LOBBY_FULL: LobbyFullEvent,
    EventTypeEnum.INVALID_EVENT: InvalidEvent,
    EventTypeEnum.LOBBY_STARTING: LobbyStartingEvent,
    EventTypeEnum.START_LOBBY: StartLobbyEvent
}

"""
Tries to parse the event with provided type.
Either returns the parsed object, or None to indicate an error
"""
def parse_lobby_event(data:dict) -> Optional[Event]:
    event_type = data.get('type')
    if event_type and event_type in event_type_to_class:
        event_class = event_type_to_class[event_type]
        try:
            event = event_class(**data)
            return event
        except ValidationError:
            return None
    else:
        return None