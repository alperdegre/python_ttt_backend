from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.dependencies import get_user_id
from app.engine.engine import GameEngine, get_engine

router = APIRouter(
    prefix="/game",
)


@router.post("/create-lobby/{player_id}")
async def create_lobby(player_id: str, engine:GameEngine = Depends(get_engine)):
    code = engine.create_lobby(player_id)

    return { "code" : code }

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

    try:
        id_req = await websocket.receive_json()
    except WebSocketDisconnect:
        await websocket.close()
        return

    client_id = id_req['playerId']

    print(f"Client ID received: {client_id}")
    
    lobby = engine.get_lobby(lobby_code)

    if lobby is None:
        websocket.close()
    else:
        lobby.join(client_id, websocket)
        await lobby.broadcast()
        
    try:
        while True:
            data = await websocket.receive_json()
            await lobby.bong(client_id)
            # await lobby.send_personal_message(f"You wrote: {data}", websocket)
            # await lobby.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        return