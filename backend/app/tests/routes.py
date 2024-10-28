from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from database.connection import get_db_session
from auth.jwt import create_access_token, get_current_user
from models.models import User
from tests.schemas import LoginRequest


test_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@test_router.post("")
async def test_sign_up(body: User, session: AsyncSession = Depends(get_db_session)) -> dict:
    existing_user = await session.get(User, body.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = pwd_context.hash(body.password)
    test_user = User(email=body.email, name=body.name,
                     password=hashed_password)

    try:
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        return {"message": f"{body.email} signed up"}

    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@test_router.post("/login")
async def test_login(body: LoginRequest, session: AsyncSession = Depends(get_db_session)) -> dict:
    email = body.email
    password = body.password

    test_user = await session.get(User, email)

    if not test_user or not pwd_context.verify(password, test_user.password):
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    access_token = create_access_token(email)
    return {"access_token": access_token}


@test_router.get("/protected-endpoint")
async def protected_endpoint(token: str = Depends(get_current_user)):
    return {"message": "You have access to the protected endpoint"}
