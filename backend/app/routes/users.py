from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests
from auth.jwt import create_access_token
from database.connection import get_db_session
from models.models import User
from dto.request_dto import TokenRequest
from config import settings

router = APIRouter(
    tags=["User"],
)


@router.post("/login")
async def login(body: TokenRequest, session: AsyncSession = Depends(get_db_session)) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential, requests.Request(), settings.GOOGLE_CLIENT_ID)

        email = idinfo.get("email")
        name = idinfo.get("name")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token or missing email",
            )

        existing_user = await session.get(User, email)

        if existing_user:
            access_token = create_access_token(email)
        else:
            new_user = User(email=email, name=name)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            access_token = create_access_token(email)

        return {"access_token": access_token}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )
