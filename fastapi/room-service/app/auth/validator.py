import httpx
from uuid import UUID
from fastapi import HTTPException
from app.config import settings

API_GATEWAY_URL = settings.API_GATEWAY_URL

async def validate_user_id(user_id: UUID):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_GATEWAY_URL}/api/v1/user/validate/{user_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid user ID")
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate user ID: {str(e)}"
        )