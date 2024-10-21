from fastapi import APIRouter, Depends, HTTPException, status
from auth.jwt import create_access_token
from database.connection import get_session
from models.users import User, TokenResponse

user_router = APIRouter(
    tags=["User"],
)

@user_router.post("/login", response_model=TokenResponse)
async def login(body: User, session=Depends(get_session)) -> dict:
    try:
        existing_user = session.get(User, body.email)
        
        if existing_user:
            access_token = create_access_token(body.email, body.exp)
        else:
            session.add(body)
            session.commit()
            session.refresh(body)
            access_token = create_access_token(body.email, body.exp)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error occurred: {str(e)}",
        )
