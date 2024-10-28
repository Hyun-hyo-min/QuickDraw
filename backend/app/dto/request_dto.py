from pydantic import BaseModel

class TokenRequest(BaseModel):
    credential: str
    
class RoomCreateRequest(BaseModel):
    room_name: str
