from enum import Enum
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError

from app.models import LobbyUser


class GameStatusEnum(str, Enum):
    FORMING = "FORMING",
    STARTING = "STARTING", 
    STARTED = "STARTED",
    ENDED = "ENDED"
    
class GameEventTypeEnum(str, Enum):
    UNAUTHORIZED = "UNAUTHORIZED",
    INVALID_EVENT = "INVALID_EVENT"
    USER_DISCONNECTED = "USER_DISCONNECTED"
    USER_CONNECTED = "USER_CONNECTED"
    GAME_SYNC = "GAME_SYNC"
    FIRST_TURN = "FIRST_TURN"
    RESULT = "RESULT"
    USER_TURN = "USER_TURN"

class GameEvent(BaseModel):
    type: GameEventTypeEnum
    data: str

    def serialize_event(self) -> dict:
        return self.model_dump()
    
class ErrorData(BaseModel):
    error: str

class UserConnectedData(BaseModel):
    user_id: str

class StateSyncData(BaseModel):
    status: GameStatusEnum
    users: List[LobbyUser]
    board: List[str]
    turn: LobbyUser
    total_turns: int

class CheckWinResult(BaseModel):
    is_win: bool
    combination: Optional[List[int]]

class UserTurnData(BaseModel):
    tile_index: int

class GameResult(BaseModel):
    is_over: bool
    status: GameStatusEnum
    winner: Optional[LobbyUser]
    combination: Optional[List[int]]

class UnauthorizedEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.UNAUTHORIZED
    data: ErrorData = ErrorData(error="Unauthorized")

class UserDisconnectedEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.USER_DISCONNECTED
    data: ErrorData = ErrorData(error="User disconnected")

class InvalidEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.INVALID_EVENT
    data: ErrorData = ErrorData(error="Invalid Event")

class UserConnectedEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.USER_CONNECTED
    data: UserConnectedData

class GameSyncEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.GAME_SYNC
    data: StateSyncData

class UserTurnEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.USER_TURN
    data: UserTurnData

class GameResultEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.RESULT
    data: GameResult

class FirstTurnEvent(GameEvent):
    type: GameEventTypeEnum = GameEventTypeEnum.FIRST_TURN
    data: LobbyUser

game_event_type_to_class: Dict[GameEventTypeEnum, Type[GameEvent]] = {
    GameEventTypeEnum.INVALID_EVENT: InvalidEvent,
    GameEventTypeEnum.UNAUTHORIZED: UnauthorizedEvent,
    GameEventTypeEnum.USER_CONNECTED: UserConnectedEvent,
    GameEventTypeEnum.GAME_SYNC: GameSyncEvent,
    GameEventTypeEnum.FIRST_TURN: FirstTurnEvent,
    GameEventTypeEnum.RESULT: GameResultEvent,
    GameEventTypeEnum.USER_TURN: UserTurnEvent,
    GameEventTypeEnum.USER_DISCONNECTED: UserDisconnectedEvent
}

"""
Tries to parse the event with provided type.
Either returns the parsed object, or None to indicate an error
"""
def parse_game_event(data:dict) -> Optional[GameEvent]:
    event_type = data.get('type')
    if event_type and event_type in game_event_type_to_class:
        event_class = game_event_type_to_class[event_type]
        try:
            event = event_class(**data)
            return event
        except ValidationError:
            return None
    else:
        return None