from unittest.mock import AsyncMock, patch
import pytest

from app.engine.events import LobbyStartingEvent, StateSyncEvent
from app.engine.lobby import Lobby
from app.models import LobbyUser

@pytest.mark.anyio
async def test_lobby_join_success(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")
    result = await lobby.join(lobby_user, mock_websocket)

    assert result == True
    mock_websocket.send_json.assert_called_once()

@pytest.mark.anyio
async def test_lobby_join_lobby_full(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")
    await lobby.join(lobby_user, mock_websocket)
    mock_user_two = LobbyUser(id="user_2", username="user_two")
    mock_user_three = LobbyUser(id="user_3", username="user_three")
    await lobby.join(mock_user_two, mock_websocket)
    result = await lobby.join(mock_user_three, mock_websocket)

    assert result == False
    mock_websocket.send_json.assert_called()
    assert len(lobby.users.keys()) == 2

@pytest.mark.anyio
async def test_lobby_join_wrong_data(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")
    try:
        await lobby.join({'test'}, mock_websocket)
    except AttributeError:
        assert AttributeError

@pytest.mark.anyio
async def test_lobby_leave(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")

    with patch('app.engine.lobby.Lobby.state_sync', new_callable=AsyncMock) as mock_state_sync:
        await lobby.join(lobby_user, mock_websocket)
        await lobby.leave(lobby_user)

        mock_state_sync.assert_called()
        assert len(lobby.users.keys()) == 0

@pytest.mark.anyio
async def test_lobby_state_sync(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")
    await lobby.join(lobby_user, mock_websocket)
    
    state_sync_event = StateSyncEvent(data={"owner":lobby.owner,"code":lobby.code, "users":lobby.users.values()})

    await lobby.state_sync()

    mock_websocket.send_json.assert_called_with(state_sync_event.serialize_event())

@pytest.mark.anyio
async def test_lobby_start_success(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")
    await lobby.join(lobby_user, mock_websocket)
    mock_user_two = LobbyUser(id="user_2", username="user_two")
    await lobby.join(mock_user_two, mock_websocket)
    result = await lobby.start(code=lobby.code)

    start_event = LobbyStartingEvent(data={'code':lobby.code, 'starting':True})

    assert result is True
    mock_websocket.send_json.assert_called_with(start_event.serialize_event())

@pytest.mark.anyio
async def test_lobby_start_not_enough_users(lobby_user, mock_websocket):
    lobby = Lobby(owner="test_owner", code="1234")
    await lobby.join(lobby_user, mock_websocket)
    result = await lobby.start(code=lobby.code)

    state_sync_event = StateSyncEvent(data={"owner":lobby.owner,"code":lobby.code, "users":lobby.users.values()})

    assert result is False
    mock_websocket.send_json.assert_called_once_with(state_sync_event.serialize_event())