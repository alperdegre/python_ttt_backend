from typing import Dict, Optional
from app.engine.game import Game
from app.engine.lobby import Lobby
from app.models import ListedLobby
from app.utils import create_game_code, create_lobby_code


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
        
    def get_lobbies(self):
        return [ListedLobby(code=lobby.code, owner=lobby.owner, players=lobby.users.values()) for lobby in self.lobbies.values()]

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
        game = Game(users={**lobby.users})

        self.games[game_code] = game
        return game_code
    
    def get_game(self, game_code:str) -> Optional[Game]:
        if game_code in self.games:
            return self.games[game_code]
        else:
            return None
        
    def close_game(self, game_code:str):
        if game_code in self.games:
            del self.games[game_code]
        else:
            return None
        
game_engine = GameEngine()

def get_engine():
    return game_engine