from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def create_access_token(email: EmailStr):
    exp = (datetime.now() + timedelta(minutes=60)).timestamp()

    payload = {
        "email": email,
        "exp": exp
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        exp = data.get("exp")

        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        if datetime.now() > exp:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired"
            )
        return data

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
