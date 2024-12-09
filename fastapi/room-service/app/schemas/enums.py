from enum import Enum

class RoomStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"