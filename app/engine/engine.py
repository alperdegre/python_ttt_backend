
from typing import Dict, Optional
from app.engine.game import Game
from app.engine.lobby import Lobby
from app.utils import create_game_code, create_lobby_code


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
        self.games: Dict[str, Game] = {}
        self.lobbies: Dict[str, Lobby] = {}

    def create_lobby(self, owner:str):
        code = self.get_unique_lobby_code()
        new_lobby = Lobby(owner, code)
        self.lobbies[code] = new_lobby
        return code
    
    def get_lobby(self, lobby_code:str) -> Optional[Lobby]:
        if lobby_code in self.lobbies:
            return self.lobbies[lobby_code]
        else:
            return None

    def close_lobby(self, lobby_code:str):
        if lobby_code in self.lobbies:
            del self.lobbies[lobby_code]
        else:
            return None
    
    def get_unique_lobby_code(self):
        code = create_lobby_code()
        while code in self.lobbies:
            code = create_lobby_code()
        return code
    
    def get_unique_game_code(self):
        code = create_game_code()
        while code in self.games:
            code = create_game_code()
        return code
    
    def start_lobby(self, lobby_code:str):
        lobby = self.get_lobby(lobby_code)
        
        if lobby is None:
            return
        elif len(lobby.users) != 2:
            return
        
        game_code = self.get_unique_game_code()
        game = Game(websockets=lobby.websockets, users=lobby.users)

        self.games[game_code] = game
        return game_code

     
game_engine = GameEngine()

def get_engine():
    return game_engine