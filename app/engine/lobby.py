from typing import Dict
from fastapi import WebSocket

from app.engine.events import LobbyStartingEvent, StateSyncEvent
from app.models import LobbyUser


class Lobby():
    def __init__(self, owner:str, code:str) -> None:
        self.owner = owner
        self.websockets: Dict[str, WebSocket] = {}
        self.users: Dict[str, LobbyUser] = {}
        self.code = code
        self.turn = owner
        self.starting = False

    async def join(self, user: LobbyUser, websocket:WebSocket):
        if len(self.users) < 2 and self.starting == False:
            self.websockets[user.id] = websocket
            self.users[user.id] = user
            await self.state_sync()
            return True
        else:
            return False
    
    async def state_sync(self):
        state_sync_event = StateSyncEvent(data={"owner":self.owner,"code":self.code, "users":self.users.values()})
        for ws in self.websockets.values():
            await ws.send_json(state_sync_event.serialize_event())

    async def leave(self, user: LobbyUser):
        del self.websockets[user.id]
        del self.users[user.id]
        await self.state_sync()
        return len(self.users)

    async def start(self, code:str):
        if len(self.users) < 2:
            return False
        else:
            self.starting = True
            start_event = LobbyStartingEvent(data={'code':code, 'starting':True})
            for ws in self.websockets.values():
                await ws.send_json(start_event.serialize_event())
            return True
   