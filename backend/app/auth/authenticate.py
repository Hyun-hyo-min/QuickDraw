from fastapi import Depends, HTTPException, status
from auth.jwt import oauth2_scheme, verify_access_token


async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )

    try:
        decode_token = verify_access_token(token)
        return decode_token["user"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token"
        )
