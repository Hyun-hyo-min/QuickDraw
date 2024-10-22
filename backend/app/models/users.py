from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
	name: str
	exp: int

class User(UserBase, table=True):
	email: EmailStr = Field(primary_key=True)

class TokenResponse(BaseModel):
	access_token: str
	token_type: str