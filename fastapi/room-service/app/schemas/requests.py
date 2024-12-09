from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
    room_name: str
