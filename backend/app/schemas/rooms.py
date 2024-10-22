from pydantic import BaseModel

class RoomCreateRequest(BaseModel):
    room_name: str