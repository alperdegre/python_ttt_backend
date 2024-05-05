from typing import Dict
from fastapi import WebSocket

class Lobby():
    def __init__(self, owner:str, code:str) -> None:
        self.owner = owner
        self.users: Dict[str, WebSocket] = {}
        self.code = code
        self.turn = owner

    def join(self, user_id:str, websocket:WebSocket):
        if len(self.users) < 2:
            self.users[user_id] = websocket
        else:
            return
    
    async def broadcast(self):
        for user in self.users.values():
            await user.send_json({'owner':self.owner, 'code':self.code})

    async def bong(self, client_id):
        if self.turn == client_id:
            new_turn = self.turn
            for user_id, user_ws in self.users.items():
                await user_ws.send_json({'user':client_id})
                if user_id != self.turn:
                    new_turn = user_id
            
            self.turn = new_turn
            for user_ws in self.users.values():
                await user_ws.send_json({'turn':self.turn})
                 
    def start(self):
        if len(self.users) == 2:
            return self.users
        else:
            return
   