from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from google.oauth2 import id_token
from google.auth.transport import requests
from auth.jwt import create_access_token, get_current_user
from database.connection import get_db_session
from database.repositories.user_repository import UserRepository
from database.repositories.player_repository import PlayerRepository
from models.models import User, Player
from dto.request_dto import TokenRequest
from config import settings

router = APIRouter(
    tags=["User"],
)


@router.post("/login")
async def login(
    body: TokenRequest,
    user_repository: UserRepository = Depends(UserRepository),
) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential, requests.Request(), settings.GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token or missing email",
            )

        existing_user = await user_repository.get_data_by_id(email)

        if existing_user:
            access_token = create_access_token(email)
        else:
            new_user = User(email=email, name=name)
            await user_repository.insert_data(new_user)
            access_token = create_access_token(email)

        return {"access_token": access_token}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )


@router.get("/rooms")
async def get_users_room(
    email: str = Depends(get_current_user),
    player_repository: PlayerRepository = Depends(PlayerRepository),
) -> dict:
    player = await player_repository.find_by_filter({"email": email})

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not in room"
        )

    room_id = player.room_id
    return {"room_id": room_id}
