
import pytest

from app.engine.lobby_events import EventTypeEnum


@pytest.mark.anyio
async def test_create_lobby(async_client):
    response = await async_client.post(f"/lobby/create-lobby")

    res_json = response.json()

    assert response.status_code == 200
    assert 'data' in res_json
    assert 'code' in res_json['data']
    assert 'type' in res_json
    assert res_json['type'] == EventTypeEnum.CREATE_LOBBY

@pytest.mark.anyio
async def test_create_lobby(async_client, game_engine):
    game_engine.create_lobby("LOBBY_1")
    game_engine.create_lobby("LOBBY_2")

    response = await async_client.get(f"/lobby/get-lobbies")

    res_json = response.json()

    assert response.status_code == 200
    assert 'lobbies' in res_json
    lobby_owners = [lobby['owner'] for lobby in res_json['lobbies']]

    assert "LOBBY_1" in lobby_owners
    assert "LOBBY_2" in lobby_owners