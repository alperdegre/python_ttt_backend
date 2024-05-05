


from app.engine.events import CreateLobbyEvent, EventTypeEnum, InvalidEvent, JoinLobbyEvent, LobbyFullEvent, LobbyNotFoundEvent, LobbyUser, StateSyncEvent, parse_event


def test_create_lobby():
    event = CreateLobbyEvent(data={"code":"Test"})

    assert event.type == EventTypeEnum.CREATE_LOBBY
    assert event.data.code == "Test"

    serialized = event.serialize_event()

    assert serialized['type'] == EventTypeEnum.CREATE_LOBBY
    assert serialized['data']['code'] == "Test"


def test_state_sync():
    test_user = LobbyUser(id="test_id", username="test_username")

    event = StateSyncEvent(data={"users":[test_user]})

    assert event.type == EventTypeEnum.STATE_SYNC
    assert event.data.users[0] == test_user
    assert event.data.users[0].id == "test_id"
    assert event.data.users[0].username == "test_username"

    serialized = event.serialize_event()

    assert serialized['type'] == EventTypeEnum.STATE_SYNC
    assert serialized['data']['users'][0]['id'] == "test_id"
    assert serialized['data']['users'][0]['username'] == "test_username"

def test_lobby_not_found():
    event = LobbyNotFoundEvent()

    assert event.type == EventTypeEnum.LOBBY_NOT_FOUND
    assert event.data.error == "Lobby Not Found"

    serialized = event.serialize_event()

    assert serialized['type'] == EventTypeEnum.LOBBY_NOT_FOUND
    assert serialized['data']['error'] == "Lobby Not Found"

def test_lobby_full():
    event = LobbyFullEvent()
    assert event.type == EventTypeEnum.LOBBY_FULL
    assert event.data.error == "Lobby Full"

    serialized = event.serialize_event()

    assert serialized['type'] == EventTypeEnum.LOBBY_FULL
    assert serialized['data']['error'] == "Lobby Full"

def test_invalid_event():
    event = InvalidEvent()
    assert event.type == EventTypeEnum.INVALID_EVENT
    assert event.data.error == "Invalid Event"

    serialized = event.serialize_event()

    assert serialized['type'] == EventTypeEnum.INVALID_EVENT
    assert serialized['data']['error'] == "Invalid Event"

def test_join_lobby():
    event = JoinLobbyEvent(data={"player_id":"test_id"})
    assert event.type == EventTypeEnum.JOIN_LOBBY
    assert event.data.player_id == "test_id"

    serialized = event.serialize_event()

    assert serialized['type'] == EventTypeEnum.JOIN_LOBBY
    assert serialized['data']['player_id'] == "test_id"

def test_parse_event_success():
    event = LobbyFullEvent()

    parsed_event, error = parse_event(event.__dict__, LobbyFullEvent)

    assert parsed_event.type == EventTypeEnum.LOBBY_FULL
    assert parsed_event.data.error == "Lobby Full"
    assert error == False

def test_parse_event_failure():
    event = LobbyFullEvent()

    parsed_event, error = parse_event(event.__dict__, JoinLobbyEvent)

    assert parsed_event.type == EventTypeEnum.INVALID_EVENT
    assert parsed_event.data.error == "Invalid Event"
    assert error == True