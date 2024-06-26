

from unittest.mock import patch

import pytest

from app.engine.engine import GameEngine
from app.engine.game import Game, GameStatusEnum
from app.engine.lobby import Lobby
from app.models import LobbyUser


def test_create_lobby():
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE") as mock_get_unique_lobby_code:
        engine.create_lobby("TEST_OWNER")

        mock_get_unique_lobby_code.assert_called_once()
        assert "CODE" in engine.lobbies
        assert len(engine.lobbies) == 1
        assert engine.lobbies["CODE"].owner == "TEST_OWNER"
        assert engine.lobbies["CODE"].code == "CODE"

def test_get_lobby_success():
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE") as mock_get_unique_lobby_code:
        engine.create_lobby("TEST_OWNER")

        mock_get_unique_lobby_code.assert_called_once()

        lobby = engine.get_lobby("CODE")

        assert isinstance(lobby, Lobby)
        assert lobby.code == "CODE"
        assert lobby.owner == "TEST_OWNER"

def test_get_lobby_fail():
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE") as mock_get_unique_lobby_code:
        engine.create_lobby("TEST_OWNER")

        mock_get_unique_lobby_code.assert_called_once()

        lobby = engine.get_lobby("WRONG_CODE")

        assert lobby is None

def test_close_lobby_success():
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE") as mock_get_unique_lobby_code:
        engine.create_lobby("TEST_OWNER")

        mock_get_unique_lobby_code.assert_called_once()

        engine.close_lobby("CODE")

        assert "CODE" not in engine.lobbies

def test_close_lobby_fail():
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE") as mock_get_unique_lobby_code:
        engine.create_lobby("TEST_OWNER")

        mock_get_unique_lobby_code.assert_called_once()

        lobby = engine.close_lobby("WRONG_CODE")

        assert lobby is None

def test_get_unique_lobby_code():
    engine = GameEngine()
    with patch('app.engine.engine.create_lobby_code', return_value="CODE") as mock_create_lobby_code:
        code = engine.get_unique_lobby_code()
        mock_create_lobby_code.assert_called_once()

        assert isinstance(code, str)
        assert code == "CODE"

def test_get_unique_game_code():
    engine = GameEngine()
    with patch('app.engine.engine.create_game_code', return_value="GAME_CODE") as mock_create_game_code:
        code = engine.get_unique_game_code()
        mock_create_game_code.assert_called_once()

        assert isinstance(code, str)
        assert code == "GAME_CODE"

def test_start_lobby_non_existing_lobby():
    engine = GameEngine()

    result = engine.start_lobby("LOBBY")

    assert result is None

def test_start_lobby_not_enough_users():
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE"):
        engine.create_lobby("TEST_OWNER")

        result = engine.start_lobby("CODE")

        assert result is None

@pytest.mark.anyio
async def test_start_lobby_success(lobby_user, mock_websocket):
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE"), patch('app.engine.engine.GameEngine.get_unique_game_code', return_value="GAME_CODE") as mock_game_code:
        engine.create_lobby("TEST_OWNER")

        lobby = engine.get_lobby("CODE")

        await lobby.join(lobby_user, mock_websocket)
        mock_user_two = LobbyUser(id="user_2", username="user_two")
        await lobby.join(mock_user_two, mock_websocket)

        result = engine.start_lobby("CODE")
        assert result is "GAME_CODE"
        mock_game_code.assert_called_once()
        assert "GAME_CODE" in engine.games

def test_get_game_success(lobby_user):
    engine = GameEngine()
    engine.games["TEST"] = Game(users={'USER_ID':lobby_user})

    game = engine.get_game("TEST")

    assert "USER_ID" in game.users
    assert game.users['USER_ID'] is lobby_user
    assert game.status is GameStatusEnum.FORMING
    
def test_get_game_fail():
    engine = GameEngine()

    game = engine.get_game("TEST_NON_EXISTENT")
    assert game is None

@pytest.mark.anyio
async def test_get_lobbies(lobby_user, mock_websocket):
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE"), patch('app.engine.engine.GameEngine.get_unique_game_code', return_value="GAME_CODE"):
        engine.create_lobby("TEST_OWNER")
        lobby = engine.get_lobby("CODE")

        await lobby.join(lobby_user, mock_websocket)

        lobbies = engine.get_lobbies()

        assert lobbies[0].code is lobby.code
        assert lobbies[0].owner is lobby.owner
        assert lobbies[0].players[0] is lobby_user

@pytest.mark.anyio
async def test_get_game_success(lobby_user, mock_websocket):
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE"), patch('app.engine.engine.GameEngine.get_unique_game_code', return_value="GAME_CODE"):
        engine.create_lobby("TEST_OWNER")

        lobby = engine.get_lobby("CODE")

        await lobby.join(lobby_user, mock_websocket)
        mock_user_two = LobbyUser(id="user_2", username="user_two")
        await lobby.join(mock_user_two, mock_websocket)

        result = engine.start_lobby("CODE")

        get_game = engine.get_game(result)

        assert get_game is engine.games[result]
        assert len(get_game.users) is 2
        assert lobby_user in get_game.users.values()
        assert mock_user_two in get_game.users.values()

def test_get_game_failure():
    engine = GameEngine()

    game_doesnt_exist = engine.get_game("NON_EXISTENT")

    assert game_doesnt_exist is None


@pytest.mark.anyio
async def test_close_game_success(lobby_user, mock_websocket):
    engine = GameEngine()
    with patch('app.engine.engine.GameEngine.get_unique_lobby_code', return_value="CODE"), patch('app.engine.engine.GameEngine.get_unique_game_code', return_value="GAME_CODE"):
        engine.create_lobby("TEST_OWNER")
        lobby = engine.get_lobby("CODE")
        await lobby.join(lobby_user, mock_websocket)
        mock_user_two = LobbyUser(id="user_2", username="user_two")
        await lobby.join(mock_user_two, mock_websocket)

        result = engine.start_lobby("CODE")
        get_game = engine.get_game(result)

        assert get_game is not None

        engine.close_game(result)

        assert len(engine.games) is 0

def test_close_game_failure():
    engine = GameEngine()

    result = engine.close_game("NON_EXISTENT")

    assert result is None

    