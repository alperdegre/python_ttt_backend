
from typing import Dict
from app.engine.lobby import Lobby
from app.utils import create_lobby_code
from fastapi import WebSocket


"""
Create lobby happens on HTTP. Gets a WS url with lobby code
    - User sends back a ws response. gets s generic "Connection established if its succesful". Lobby screen is ws based.
    - Join lobby means getting access to that lobby's ws url. Join lobby function has to check if current lobby is full or not. 
    Return a HTTP response accordinglyor join the lobby.

Lobby features
    - Disconnect means losing the WS connection.
    - When start game gets pressed.It sends an event through frontend. Which should disconnect the ws connection. 
        - Connect to a new ws url where only 2 users for the game can join it.
        - Games have their own while true loop inside. Users always append game id + user id. That is how game proceeds.

Game features
    - Every turn keep track of whose turn it is. When you recieve an event from whose turn it is. Update turn variable and add the move after. This should solve duplicate requests.

"""



class GameEngine():
    def __init__(self):
        self.sockets = {}
        self.lobbies = {}

    def create_lobby(self, owner:str):
        code = self.get_unique_lobby_code()
        new_lobby = Lobby(owner, code)
        self.lobbies[code] = new_lobby
        return code
    
    def get_lobby(self, lobby_code:str):
        if lobby_code in self.lobbies:
            return self.lobbies[lobby_code]
        else:
            return None

    def get_unique_lobby_code(self):
        code = create_lobby_code()
        while code in self.lobbies:
            code = create_lobby_code()
        return code
    
    def start_lobby(self, lobby_id:str):
        lobby = self.lobbies[lobby_id]

        if lobby is None:
            return
        
        sockets = []

        for user in lobby.users:
            found_socket = self.sockets.find(user)

            if found_socket is None:
                break

            sockets.append(found_socket)
        
        self.games[lobby_id] = Game(sockets)




     
game_engine = GameEngine()

def get_engine():
    return game_engine