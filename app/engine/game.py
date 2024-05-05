from fastapi import WebSocket

class Game():
    def __init__(self, sockets):
        self.sockets: list[WebSocket] = sockets
