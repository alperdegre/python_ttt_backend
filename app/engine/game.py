import random
from typing import Dict, List
from fastapi import WebSocket

from app.engine.game_events import CheckWinResult, FirstTurnEvent, GameEvent, GameResult, GameResultEvent, GameStatusEnum, GameSyncEvent, UserDisconnectedEvent, UserTurnEvent, parse_game_event
from app.models import LobbyUser

winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal wins
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical wins
        [0, 4, 8], [2, 4, 6]             # Diagonal wins
]
    
class Game():
    def __init__(self, users: Dict[str, LobbyUser]):
        self.websockets: Dict[str, WebSocket] = {}
        self.users = users
        self.user_ids: List[str] = list(users.keys())
        self.status:GameStatusEnum = GameStatusEnum.FORMING
        self.total_turns: int = 0
        self.turn: int = 0
        self.board = ["" for _ in range(9)]
        
    def connect_user(self, user_id:str, websocket: WebSocket):
        if user_id in self.users.keys():
            self.websockets[user_id] = websocket
            return True
        else:
            return False
    
    async def game_sync(self):
        turn = self.turn
        user_id = self.user_ids[turn]
        current_turn_user = self.users[user_id]
        state_sync_event = GameSyncEvent(data={"status":self.status, "users":self.users.values(), "turn":current_turn_user, "total_turns":self.total_turns, "board":self.board})
        await self.broadcast(state_sync_event)

    async def broadcast(self, event:GameEvent):
        for ws in self.websockets.values():
            await ws.send_json(event.serialize_event())

    async def broadcast_start(self):
        self.status = GameStatusEnum.STARTING
        await self.decide_turn()
        self.status = GameStatusEnum.STARTED
        await self.game_sync()

    async def decide_turn(self):
        random_number = random.randint(0, 1)
        self.turn = random_number
        starting_user = self.users[self.user_ids[random_number]]
        start_turn_event = FirstTurnEvent(data=starting_user)
        await self.broadcast(start_turn_event)

    async def start_game(self):
        if self.status == GameStatusEnum.FORMING and len(self.websockets.keys()) == 2:
            await self.broadcast_start()

    async def check_valid_move(self, event: GameEvent):
        if event.__class__ is UserTurnEvent:
            tile_ix = event.data.tile_index
            if self.board[tile_ix] != "":
                return False
            
            mark = self.get_mark()
            self.board[tile_ix] = mark

            return True
        return False

    def advance_turn(self):
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn = 0

        self.total_turns += 1

    def get_mark(self):
        if self.turn == 0:
            return "X"
        else:
            return "O"
    
    async def game_loop(self, user_id: str, event: GameEvent):
        if self.user_ids[self.turn] == user_id and self.status is not GameStatusEnum.ENDED:
            is_valid_move = await self.check_valid_move(event)

            if is_valid_move is False:
                return False
            
            await self.sync_click_with_other_user(event, user_id);
            await self.game_sync()
            
            game_result = await self.check_game_over(user_id)
            if game_result.is_over is False:
                self.advance_turn()
                await self.game_sync()
                return False
            else:
                await self.end_game(game_result)
                return True
        else:
            return False

    async def check_game_over(self, user_id: str) -> GameResult:
        mark = self.get_mark()
        win_result = self.check_win(mark)

        if win_result.is_win is True:
            return GameResult(is_over=True, status=GameStatusEnum.ENDED, winner=self.users[user_id], combination=win_result.combination)
        
        is_tie = self.check_tie()

        if is_tie is True:
            return GameResult(is_over=True, status=GameStatusEnum.ENDED, winner=None, combination=None)
        
        return GameResult(is_over=False, status=self.status, winner=None,  combination=None)
    
    def check_win(self, mark:str):
        for combination in winning_combinations:
            if all(self.board[i] == mark for i in combination):
                return CheckWinResult(is_win=True, combination=combination)
        return CheckWinResult(is_win=False, combination=None)
    
    def check_tie(self):
        if "" in self.board:
            return False
        return True
    
    async def send_game_over(self, game_result: GameResult):
        game_result_event = GameResultEvent(data=game_result)
        await self.broadcast(game_result_event)

    async def end_game(self, game_result: GameResult):
        self.status = GameStatusEnum.ENDED
        await self.send_game_over(game_result)
        websockets = self.websockets.values()
        for ws in websockets:
            await ws.close()

    async def handle_disconnect(self, dced_user_id:str):
        del self.websockets[dced_user_id]
        user_disconnected_event = UserDisconnectedEvent()
        await self.broadcast(user_disconnected_event)

    async def sync_click_with_other_user(self, event: UserTurnEvent, user_id: str):
        current_index = self.user_ids.index(user_id)
        other_user = 1 - current_index
        other_user_ws = self.websockets[self.user_ids[other_user]]
        await other_user_ws.send_json(event.serialize_event())