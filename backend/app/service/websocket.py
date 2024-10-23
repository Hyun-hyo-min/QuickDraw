from typing import Set, Dict
from threading import Lock


class MaximumSessionReachException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class MaximumConnectionPerSessionReachException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class WebSocketManager:
    MAX_SESSIONS = 1000
    MAX_CONNECTIONS_PER_SESSION = 8
    _instance = None
    _lock = Lock()

    def __init__(self):
        self.connected_clients: Dict[int, Set] = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WebSocketManager, cls).__new__(cls)
        return cls._instance

    def add_client(self, session_id, client):
        if len(self.connected_clients) >= self.MAX_SESSIONS:
            raise MaximumSessionReachException("Session is full")

        if session_id not in self.connected_clients:
            self.connected_clients[session_id] = set()

        if len(self.connected_clients[session_id]) >= self.MAX_CONNECTIONS_PER_SESSION:
            raise MaximumConnectionPerSessionReachException(
                "Maximum connections per session exceeded")

        self.connected_clients[session_id].add(client)

    def remove_client(self, session_id, client):
        self.connected_clients[session_id].remove(client)

    def get_clients(self, session_id):
        return self.connected_clients.get(session_id, set())


def get_ws_manager():
    return WebSocketManager()
