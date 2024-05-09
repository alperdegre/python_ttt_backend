

from unittest.mock import AsyncMock, Mock, patch
import pytest

from app.engine.game import Game
from app.engine.game_events import CheckWinResult, FirstTurnEvent, GameEventTypeEnum, GameResult, GameResultEvent, GameStatusEnum, InvalidEvent, UserDisconnectedEvent, UserTurnEvent
from app.models import LobbyUser


@pytest.fixture
def test_game(lobby_user: LobbyUser):
    second_user = LobbyUser(id="SECOND_ID", username="SECOND_USER")
    return Game({"TEST_ID":lobby_user, "SECOND_ID": second_user})

def test_connect_user_success(test_game: Game, mock_websocket: AsyncMock):
    result = test_game.connect_user("TEST_ID", mock_websocket)
    assert result is True

def test_connect_user_failure(test_game: Game, mock_websocket: AsyncMock):
    result = test_game.connect_user("NO_ID", mock_websocket)
    assert result is False

@pytest.mark.anyio
async def test_game_sync(test_game: Game):

    with patch('app.engine.game.Game.broadcast', new_callable=AsyncMock) as mock_broadcast:
        await test_game.game_sync()

        mock_broadcast.assert_called_once()

        args, _ = mock_broadcast.call_args

        state_sync_event = args[0]
        assert state_sync_event.data.status == test_game.status
        assert list(state_sync_event.data.users) == list(test_game.users.values())
        assert state_sync_event.data.turn == test_game.users[test_game.user_ids[test_game.turn]]
        assert state_sync_event.data.total_turns == test_game.total_turns
        assert state_sync_event.data.board == test_game.board

@pytest.mark.anyio
async def test_broadcast(test_game: Game, mock_websocket: AsyncMock):
        test_game.websockets["TEST_ID"] = mock_websocket
        start_turn_event = UserTurnEvent(data={"tile_index":1})
        await test_game.broadcast(start_turn_event)

        mock_websocket.send_json.assert_called_once()
        args, _ = mock_websocket.send_json.call_args
        assert args[0] == {'type': GameEventTypeEnum.USER_TURN, 'data': {'tile_index': 1}}

@pytest.mark.anyio
async def test_broadcast_start(test_game: Game):
    with patch('app.engine.game.Game.decide_turn', new_callable=AsyncMock) as mock_decide_turn, patch('app.engine.game.Game.game_sync', new_callable=AsyncMock) as mock_game_sync:
        assert test_game.status == GameStatusEnum.FORMING
        await test_game.broadcast_start()

        assert test_game.status == GameStatusEnum.STARTED
        mock_decide_turn.assert_called_once()
        mock_game_sync.assert_called_once()

@pytest.mark.anyio
async def test_decide_turn(test_game: Game):

    with patch('app.engine.game.Game.broadcast', new_callable=AsyncMock) as mock_broadcast:
        await test_game.decide_turn()

        mock_broadcast.assert_called_once()

        args, _ = mock_broadcast.call_args

        state_sync_event = args[0]
        assert state_sync_event.__class__ == FirstTurnEvent
        assert test_game.turn is 1 or test_game.turn is 0

@pytest.mark.anyio
async def test_start_game_success(test_game: Game, mock_websocket: AsyncMock):
    test_game.websockets["ONE"] = mock_websocket
    test_game.websockets["TWO"] = mock_websocket
    test_game.status = GameStatusEnum.FORMING

    with patch('app.engine.game.Game.broadcast_start', new_callable=AsyncMock) as mock_start:
        await test_game.start_game()
        mock_start.assert_called_once()

@pytest.mark.anyio
async def test_start_game_status_failure(test_game: Game, mock_websocket: AsyncMock):
    test_game.websockets["ONE"] = mock_websocket
    test_game.websockets["TWO"] = mock_websocket
    test_game.status = GameStatusEnum.STARTING

    with patch('app.engine.game.Game.broadcast_start', new_callable=AsyncMock) as mock_start:
        await test_game.start_game()
        mock_start.assert_not_called()


@pytest.mark.anyio
async def test_start_game_not_enough_users_failure(test_game: Game):
    test_game.status = GameStatusEnum.FORMING

    with patch('app.engine.game.Game.broadcast_start', new_callable=AsyncMock) as mock_start:
        await test_game.start_game()
        mock_start.assert_not_called()


@pytest.mark.anyio
async def test_check_valid_move_non_empty_space_failure(test_game: Game):
    test_game.board = ["","X",""]
    user_turn_event = UserTurnEvent(data={'tile_index':1})

    result = await test_game.check_valid_move(user_turn_event)

    assert result is False

@pytest.mark.anyio
async def test_check_valid_move_invalid_event_failure(test_game: Game):
    user_turn_event = InvalidEvent()

    result = await test_game.check_valid_move(user_turn_event)
    
    assert result is False

@pytest.mark.anyio
async def test_check_valid_move_success(test_game: Game):
    test_game.board = ["","X",""]
    user_turn_event = UserTurnEvent(data={'tile_index':2})

    result = await test_game.check_valid_move(user_turn_event)

    assert result is True

def test_advance_turn_zero_to_one(test_game):
    test_game.turn = 0
    test_game.total_turns = 0

    test_game.advance_turn()

    assert test_game.turn == 1
    assert test_game.total_turns == 1

def test_advance_turn_one_to_zero(test_game):
    test_game.turn = 1
    test_game.total_turns = 5

    test_game.advance_turn()

    assert test_game.turn == 0
    assert test_game.total_turns == 6

def test_get_mark_x(test_game):
    test_game.turn = 0
    mark = test_game.get_mark()

    assert mark == "X"

def test_get_mark_o(test_game):
    test_game.turn = 1
    mark = test_game.get_mark()

    assert mark == "O"

@pytest.mark.anyio
async def test_game_loop_invalid_move_scenario(test_game: Game):
    test_game.turn = 0
    test_game.user_ids = ["TEST"]
    test_game.status = GameStatusEnum.STARTED

    with patch('app.engine.game.Game.check_valid_move', return_value=False) as mock_valid_move:
        user_turn_event = UserTurnEvent(data={'tile_index':1})
        loop_result = await test_game.game_loop("TEST", user_turn_event)

        assert loop_result is False
        mock_valid_move.assert_called_once_with(user_turn_event)

@pytest.mark.anyio
async def test_game_loop_game_continue_scenario(test_game: Game):
    test_game.turn = 0
    test_game.user_ids = ["TEST"]
    test_game.status = GameStatusEnum.STARTED

    with patch('app.engine.game.Game.check_valid_move', return_value=True) as mock_valid_move, \
        patch('app.engine.game.Game.sync_click_with_other_user', new_callable=AsyncMock) as mock_click_sync, \
        patch('app.engine.game.Game.game_sync', new_callable=AsyncMock) as mock_game_sync, \
        patch('app.engine.game.Game.check_game_over', return_value=GameResult(is_over=False, status=GameStatusEnum.STARTED, winner=None,  combination=None)) as mock_check_game_over, \
        patch('app.engine.game.Game.advance_turn', new_callable=Mock) as mock_advance_turn:

        user_turn_event = UserTurnEvent(data={'tile_index':1})
        loop_result = await test_game.game_loop("TEST", user_turn_event)

        assert loop_result is False
        mock_valid_move.assert_called_once_with(user_turn_event)
        mock_click_sync.assert_called_once_with(user_turn_event, "TEST")
        mock_game_sync.assert_called()
        mock_check_game_over.assert_called_once_with("TEST")
        mock_advance_turn.assert_called()

@pytest.mark.anyio
async def test_game_loop_game_over_scenario(test_game: Game):
    test_game.turn = 0
    test_game.user_ids = ["TEST"]
    test_game.status = GameStatusEnum.STARTED
    test_result = GameResult(is_over=True, status=GameStatusEnum.STARTED, winner=None,  combination=None)

    with patch('app.engine.game.Game.check_valid_move', return_value=True) as mock_valid_move, \
        patch('app.engine.game.Game.sync_click_with_other_user', new_callable=AsyncMock) as mock_click_sync, \
        patch('app.engine.game.Game.game_sync', new_callable=AsyncMock) as mock_game_sync, \
        patch('app.engine.game.Game.check_game_over', return_value=test_result) as mock_check_game_over, \
        patch('app.engine.game.Game.end_game', new_callable=AsyncMock) as mock_end_game:

        user_turn_event = UserTurnEvent(data={'tile_index':1})
        loop_result = await test_game.game_loop("TEST", user_turn_event)

        assert loop_result is True
        mock_valid_move.assert_called_once_with(user_turn_event)
        mock_click_sync.assert_called_once_with(user_turn_event, "TEST")
        mock_game_sync.assert_called()
        mock_check_game_over.assert_called_once_with("TEST")
        mock_end_game.assert_called_once_with(test_result)

@pytest.mark.anyio
async def test_game_loop_user_doesnt_exist_scenario(test_game: Game):
    test_game.turn = 0
    test_game.status = GameStatusEnum.STARTED

    user_turn_event = UserTurnEvent(data={'tile_index':1})
    loop_result = await test_game.game_loop("TEST", user_turn_event)

    assert loop_result is False

@pytest.mark.anyio
async def test_game_loop_game_already_ended_scenario(test_game: Game):
    test_game.turn = 0
    test_game.user_ids = ["TEST"]
    test_game.status = GameStatusEnum.ENDED

    user_turn_event = UserTurnEvent(data={'tile_index':1})
    loop_result = await test_game.game_loop("TEST", user_turn_event)

    assert loop_result is False

@pytest.mark.anyio
async def test_check_game_over_win_scenario(test_game: Game, lobby_user):
    test_win_result = CheckWinResult(is_win=True, combination=[1,2,3])
    test_game.users["TEST"] = lobby_user

    with patch('app.engine.game.Game.get_mark', return_value="X") as mock_get_mark, \
        patch('app.engine.game.Game.check_win', return_value=test_win_result) as mock_check_win:
        
        result = await test_game.check_game_over("TEST")

        mock_get_mark.assert_called_once()
        mock_check_win.assert_called_once_with("X")

        assert result.is_over is True
        assert result.status is GameStatusEnum.ENDED
        assert result.winner is lobby_user
        assert result.combination[0] is 1
        assert result.combination[1] is 2
        assert result.combination[2] is 3

@pytest.mark.anyio
async def test_check_game_over_tie_scenario(test_game: Game, lobby_user):
    test_win_result = CheckWinResult(is_win=False, combination=[1,2,3])
    test_game.users["TEST"] = lobby_user

    with patch('app.engine.game.Game.get_mark', return_value="X") as mock_get_mark, \
        patch('app.engine.game.Game.check_win', return_value=test_win_result) as mock_check_win, \
        patch('app.engine.game.Game.check_tie', return_value=True) as mock_check_tie:
        
        result = await test_game.check_game_over("TEST")

        mock_get_mark.assert_called_once()
        mock_check_win.assert_called_once_with("X")
        mock_check_tie.assert_called_once()

        assert result.is_over is True
        assert result.status is GameStatusEnum.ENDED
        assert result.winner is None
        assert result.combination is None

@pytest.mark.anyio
async def test_check_game_over_game_not_over_scenario(test_game: Game, lobby_user):
    test_win_result = CheckWinResult(is_win=False, combination=[1,2,3])
    test_game.status = GameStatusEnum.STARTED
    test_game.users["TEST"] = lobby_user

    with patch('app.engine.game.Game.get_mark', return_value="X") as mock_get_mark, \
        patch('app.engine.game.Game.check_win', return_value=test_win_result) as mock_check_win, \
        patch('app.engine.game.Game.check_tie', return_value=False) as mock_check_tie:
        
        result = await test_game.check_game_over("TEST")

        mock_get_mark.assert_called_once()
        mock_check_win.assert_called_once_with("X")
        mock_check_tie.assert_called_once()

        assert result.is_over is False
        assert result.status is GameStatusEnum.STARTED
        assert result.winner is None
        assert result.combination is None

def test_check_win_is_win(test_game):
    test_game.board = ["X","X","X","","","","","",""]

    result = test_game.check_win("X")

    assert result.is_win is True
    assert result.combination[0] is 0
    assert result.combination[1] is 1
    assert result.combination[2] is 2

def test_check_win_not_win(test_game):
    test_game.board = ["X","0","X","","","","","",""]

    result = test_game.check_win("X")
    assert result.is_win is False
    assert result.combination is None

def test_check_tie_is_tie(test_game):
    test_game.board = ["X","0","X","X","X","X","X","X","X"]

    result = test_game.check_tie()

    assert result is True

def test_check_tie_not_tie(test_game):
    test_game.board = ["X","0","X","X","X","X","X","X",""]

    result = test_game.check_tie()

    assert result is False

@pytest.mark.anyio
async def test_send_game_over(test_game):
    game_result = GameResult(is_over=True, status=GameStatusEnum.STARTED, winner=None, combination=None)
    with patch('app.engine.game.Game.broadcast', new_callable=AsyncMock) as mock_broadcast:
        await test_game.send_game_over(game_result=game_result)
        mock_broadcast.assert_called_once()

        args, _ = mock_broadcast.call_args

        assert args[0].__class__ is GameResultEvent

@pytest.mark.anyio
async def test_end_game(test_game):
    game_result = GameResult(is_over=True, status=GameStatusEnum.STARTED, winner=None, combination=None)
    
    with patch('app.engine.game.Game.send_game_over', new_callable=AsyncMock) as mock_game_over:
        await test_game.end_game(game_result)
        assert test_game.status == GameStatusEnum.ENDED
        mock_game_over.assert_called_once_with(game_result)

@pytest.mark.anyio
async def test_handle_disconnect(test_game, mock_websocket):
    test_game.websockets["TEST_ID"] = mock_websocket
    disconnected_event = UserDisconnectedEvent()

    with patch('app.engine.game.Game.broadcast', new_callable=AsyncMock) as mock_broadcast:
        await test_game.handle_disconnect("TEST_ID")
        mock_broadcast.assert_called_once_with(disconnected_event)
        assert "TEST_ID" not in test_game.websockets

@pytest.mark.anyio
async def test_sync_click_with_other_user(test_game, mock_websocket):
    user_turn_event = UserTurnEvent(data={"tile_index":1})

    mock_listening_ws = AsyncMock()
    mock_listening_ws.send_json = AsyncMock()
    test_game.user_ids = ["PLAYING_ID", "LISTENING_ID"]
    test_game.websockets["PLAYING_ID"] = mock_websocket
    test_game.websockets["LISTENING_ID"] = mock_listening_ws

    await test_game.sync_click_with_other_user(user_turn_event, "PLAYING_ID")
    mock_listening_ws.send_json.assert_called_once_with(user_turn_event.serialize_event())