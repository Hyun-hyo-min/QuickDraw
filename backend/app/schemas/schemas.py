from pydantic import BaseModel

class RoomCreateRequest(BaseModel):
    room_name: str

class RoomResponse(BaseModel):
    id: int
    name: str
    host: str
    status: str
    max_players: int
    current_players: int
