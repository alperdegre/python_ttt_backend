from app.engine.game_events import FirstTurnEvent, GameEventTypeEnum, GameResultEvent, GameStatusEnum, GameSyncEvent, InvalidEvent, UnauthorizedEvent, UserConnectedEvent, UserDisconnectedEvent, UserTurnEvent, parse_game_event
from app.models import LobbyUser


def test_unauthorized_event():
    event = UnauthorizedEvent()
    assert event.type == GameEventTypeEnum.UNAUTHORIZED
    assert event.data.error == "Unauthorized"

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.UNAUTHORIZED
    assert serialized['data']['error'] == "Unauthorized"

def test_invalid_event():
    event = InvalidEvent()
    assert event.type == GameEventTypeEnum.INVALID_EVENT
    assert event.data.error == "Invalid Event"

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.INVALID_EVENT
    assert serialized['data']['error'] == "Invalid Event"

def test_user_disconnected_event():
    event = UserDisconnectedEvent()
    assert event.type == GameEventTypeEnum.USER_DISCONNECTED
    assert event.data.error == "User disconnected"

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.USER_DISCONNECTED
    assert serialized['data']['error'] == "User disconnected"

def test_user_connected():
    event = UserConnectedEvent(data={"user_id":"TEST_ID"})

    assert event.type == GameEventTypeEnum.USER_CONNECTED
    assert event.data.user_id == "TEST_ID"

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.USER_CONNECTED
    assert serialized['data']['user_id'] == "TEST_ID"

def test_game_sync():
    test_user = LobbyUser(id="test_id", username="test_username")
    test_board = ["X","O","X"]
    event = GameSyncEvent(data={"status":GameStatusEnum.STARTED, "users":[test_user], "board":test_board,"turn":test_user, "total_turns":0})

    assert event.type == GameEventTypeEnum.GAME_SYNC
    assert event.data.users[0] == test_user
    assert event.data.users[0].id == "test_id"
    assert event.data.users[0].username == "test_username"
    assert event.data.turn == test_user
    assert event.data.turn.id == "test_id"
    assert event.data.turn.username == "test_username"
    assert event.data.board[0] == "X"
    assert event.data.board[1] == "O"
    assert event.data.board[2] == "X"
    assert event.data.total_turns == 0

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.GAME_SYNC
    assert serialized['data']['users'][0]['id'] == "test_id"
    assert serialized['data']['users'][0]['username'] == "test_username"
    assert serialized['data']['turn']['id'] == "test_id"
    assert serialized['data']['turn']['username'] == "test_username"
    assert serialized['data']['board'][0] == "X"
    assert serialized['data']['board'][1] == "O"
    assert serialized['data']['board'][2] == "X"
    assert serialized['data']['total_turns'] == 0

def test_first_turn():
    event = FirstTurnEvent(data={"id":"TEST_ID", "username":"TEST_USERNAME"})

    assert event.type == GameEventTypeEnum.FIRST_TURN
    assert event.data.id == "TEST_ID"
    assert event.data.username == "TEST_USERNAME"

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.FIRST_TURN
    assert serialized['data']['id'] == "TEST_ID"
    assert serialized['data']['username'] == "TEST_USERNAME"

def test_result(lobby_user):
    event = GameResultEvent(data={"is_over":False, "status":GameStatusEnum.STARTED, 'winner': lobby_user, 'combination': [4,5,6]})

    assert event.type == GameEventTypeEnum.RESULT
    assert event.data.is_over == False
    assert event.data.status == GameStatusEnum.STARTED
    assert event.data.winner.id == "test_user"
    assert event.data.winner.username == "Test_User"
    assert event.data.combination[0] == 4
    assert event.data.combination[1] == 5
    assert event.data.combination[2] == 6

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.RESULT
    assert serialized['data']['is_over'] == False
    assert serialized['data']['status'] == GameStatusEnum.STARTED
    assert serialized['data']['winner']['id'] == "test_user"
    assert serialized['data']['winner']['username'] == "Test_User"
    assert serialized['data']['combination'][0] == 4
    assert serialized['data']['combination'][1] == 5
    assert serialized['data']['combination'][2] == 6

def test_user_turn():
    event = UserTurnEvent(data={"tile_index":5})

    assert event.type == GameEventTypeEnum.USER_TURN
    assert event.data.tile_index == 5

    serialized = event.serialize_event()

    assert serialized['type'] == GameEventTypeEnum.USER_TURN
    assert serialized['data']['tile_index'] == 5

def test_parse_game_event_success():
    event = UserTurnEvent(data={"tile_index":5})
    parsed_event = parse_game_event(event.__dict__)

    assert parsed_event.__class__ == UserTurnEvent
    assert parsed_event.type == GameEventTypeEnum.USER_TURN
    assert event.data.tile_index == 5

def test_parse_game_event_failure():
    event = {'type':"TEST_TYPE", 'data':"Test"}

    parsed_event = parse_game_event(event)

    assert parsed_event is None

