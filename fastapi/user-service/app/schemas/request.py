from pydantic import BaseModel
from pydantic import EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    credential: str
