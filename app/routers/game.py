


from json import JSONDecodeError
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.engine.engine import GameEngine, get_engine
from app.engine.game_events import GameStatusEnum, UnauthorizedEvent, UserConnectedEvent, parse_game_event


router = APIRouter(
    prefix="/game",
)

@router.websocket("/{game_code}")
async def join_lobby(websocket: WebSocket, game_code:str, engine:GameEngine = Depends(get_engine)):
    await websocket.accept()
    
    # Check if game exists
    game = engine.get_game(game_code=game_code)
    if game is None:
        await websocket.send_json(UnauthorizedEvent().serialize_event())
        await websocket.close()
        return

    # Users send a UserConnectedEvent when first connecting to server so game can wait for both users to connect
    try:
        connected_event = await websocket.receive_json()
    except WebSocketDisconnect or JSONDecodeError:
        await websocket.close()
        return
    
    connected_parsed = parse_game_event(connected_event)
    if connected_parsed is None or connected_parsed.__class__ is not UserConnectedEvent:
        await websocket.send_json(UnauthorizedEvent().serialize_event())
        await websocket.close()
        return
    
    # Get the user id, connect with it if the user id already exists in game object
    conn_user_id = connected_parsed.data.user_id
    conn_result = game.connect_user(conn_user_id, websocket)

    # If the user wasnt in the lobby, send an Unauthorized event and disconnect the user
    if conn_result is False:
        await websocket.send_json(UnauthorizedEvent().serialize_event())
        await websocket.close()
        return
    else:
    # Else game_sync so new user is broadcast to every user
        await game.game_sync()
    
    # If game has enough players, start the game
    if len(game.users) == 2:
        await game.broadcast_start()

    try:
        while True:
            # Parse and check events
            received_data = await websocket.receive_json()
            event = parse_game_event(received_data)
            if event is None:
                return

            # With every step check if game is over
            is_over = await game.game_loop(conn_user_id, event)

            # If its over, close the game and do cleanups
            if is_over is True:
                engine.close_game(game_code)
                return
    except WebSocketDisconnect:
        # If game isnt ended and a user Disconnects, disconnect the other user and close the game
        if game.status is not GameStatusEnum.ENDED:
            await game.handle_disconnect(conn_user_id)
            engine.close_game(game_code)
        return
    except JSONDecodeError:
        return