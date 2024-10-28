from pydantic import BaseModel

class RoomResponse(BaseModel):
    id: int
    name: str
    host: str
    status: str
    max_players: int
    current_players: int
