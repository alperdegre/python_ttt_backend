from json import JSONDecodeError
from typing import cast
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.dependencies import get_user_id
from app.engine.engine import GameEngine, get_engine
from app.engine.events import CreateLobbyEvent, EventTypeEnum, InvalidEvent, JoinLobbyEvent, LobbyFullEvent, parse_event
from app.models import LobbyUser

router = APIRouter(
    prefix="/lobby",
)


# async def create_lobby(user_id: int = Depends(get_user_id), engine:GameEngine = Depends(get_engine)):
@router.post("/create-lobby/{user_id}")
async def create_lobby(user_id: str, engine:GameEngine = Depends(get_engine)):
    code = engine.create_lobby(user_id)

    return CreateLobbyEvent(data={"code":code}).serialize_event()

@router.get("/get-lobby")
async def get_test(lobby_id:str, engine:GameEngine = Depends(get_engine)):
    lobby = engine.get_lobby(lobby_id)

    if lobby is "not_found":
        return {"error":"Not found"}
    
    return {"owner":lobby.owner, "users":lobby.users, "code":lobby.code}

# async def join_lobby(user_id: int = Depends(get_user_id)):
@router.websocket("/join-lobby/{lobby_code}")
async def join_lobby(websocket: WebSocket, lobby_code:str, engine:GameEngine = Depends(get_engine)):
    await websocket.accept()

    # Check user's initial join event
    try:
        init_request = await websocket.receive_json()
    except WebSocketDisconnect or JSONDecodeError:
        await websocket.close()
        return

    # Parse the event
    join_event = parse_event(init_request)
    if join_event is None or join_event.__class__ is not JoinLobbyEvent:
        await websocket.send_json(InvalidEvent().serialize_event())
        await websocket.close()
        return
    
    lobby_user = cast(LobbyUser, join_event.data)

    # Get the lobby
    lobby = engine.get_lobby(lobby_code)

    # If the request is into a non-existent lobby, disconnect
    if lobby is None:
        await websocket.close()
        return
    else:
        # Join the lobby if its not full
        result = await lobby.join(lobby_user, websocket)
        if result is False:
            await websocket.send_json(LobbyFullEvent().serialize_event())
            await websocket.close()
            return
        
    try:
        while True:
            # Receive and parse events
            data = await websocket.receive_json()
            event = parse_event(data)

            # Invalid event state
            if event is None:
                await websocket.send_json(InvalidEvent().serialize_event())

            # Start lobby event, start a game and broadcast the game_code to redirect users
            if event.type == EventTypeEnum.START_LOBBY and lobby_user.id == lobby.owner:
                game_code = await engine.start_lobby(lobby_code)
                if game_code is None:
                    await websocket.send_json(InvalidEvent().serialize_event())
                else:
                    await lobby.start(code=game_code)

    except WebSocketDisconnect:
        # In case of disconnect check how many users left on the lobby
        users_in_lobby = await lobby.leave(lobby_user)
        # If no one left, close the lobby to free up memory
        if users_in_lobby == 0:
            engine.close_lobby(lobby.code)
        return
    except JSONDecodeError:
        # In case of invalid event bodies, send an invalid event response
        await websocket.send_json(InvalidEvent().serialize_event())
        return