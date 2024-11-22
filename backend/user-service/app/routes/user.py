from redis.asyncio import Redis
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from passlib.hash import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests
from app.auth.jwt import create_access_token
from app.db.connection import get_redis_client
from app.db.repositories import UserRepository
from app.db.models import User
from app.schemas.request import SignUpRequest, SignInRequest, LoginRequest
from app.config import settings

router = APIRouter(
    tags=["User"]
)


@router.get("/validate/{user_id}")
async def validate_user(
    user_id: UUID,
    user_repository: UserRepository = Depends(UserRepository),
    redis: Redis = Depends(get_redis_client)
):
    cached_result = await redis.get(f"user:{user_id}")
    if cached_result:
        return {"message": "User is valid"}

    user = await user_repository.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await redis.set(f"user:{user_id}", "valid", ex=3600)
    return {"message": "User is valid"}


@router.post("/")
async def sign_up(
    body: SignUpRequest,
    user_repository: UserRepository = Depends(UserRepository)
):
    existing_user = await user_repository.find_one_by_filter({"email": body.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )

    hashed_password = bcrypt.hash(body.password)

    user = User(
        email=body.email,
        name=body.name,
        password=hashed_password,
        created_at=datetime.now(timezone.utc)
    )
    await user_repository.insert_data(user)

    return {"message": "User signed up successfully"}


@router.post("/sign-in")
async def sign_in(
    body: SignInRequest,
    user_repository: UserRepository = Depends(UserRepository)
):
    user = await user_repository.find_one_by_filter({"email": body.email})
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password."
        )

    if not bcrypt.verify(body.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password."
        )

    access_token = create_access_token(str(user.id))

    return {"access_token": access_token}


@router.post("/login")
async def login(
    body: LoginRequest,
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
                status_code=400,
                detail="Invalid token or missing email"
            )

        user = await user_repository.find_one_by_filter({"email": email})

        if user:
            access_token = create_access_token(str(user.id))
        else:
            id = uuid4()
            user = User(id=id, email=email, name=name)
            await user_repository.insert_data(user)
            access_token = create_access_token(str(id))

        return {"access_token": access_token}

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {e}"
        )
