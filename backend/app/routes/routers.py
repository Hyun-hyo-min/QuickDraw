from fastapi import APIRouter
from routes import users
from routes import rooms
from routes import websocket

router = APIRouter()

router.include_router(users.router, prefix="/api/v1/users")
router.include_router(rooms.router, prefix="/api/v1/rooms")
router.include_router(websocket.router, prefix="/ws")