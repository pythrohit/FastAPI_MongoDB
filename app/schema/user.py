from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    address: Optional[str]
    blogs: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    updated_at: Optional[datetime] = None
