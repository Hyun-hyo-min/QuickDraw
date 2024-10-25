from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import create_access_token
from database.connection import get_db_session
from models.models import User

router = APIRouter(
    tags=["User"],
)

@router.post("/login")
async def login(body: User, session: AsyncSession = Depends(get_db_session)) -> dict:
    try:
        existing_user = await session.get(User, body.email)
        
        if existing_user:
            access_token = create_access_token(body.email)
        else:
            session.add(body)
            await session.commit()
            await session.refresh(body)
            access_token = create_access_token(body.email)
        
        return {"access_token": access_token}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error occurred: {str(e)}",
        )
