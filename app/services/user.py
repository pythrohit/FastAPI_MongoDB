from datetime import datetime, timedelta
from typing import Optional, Annotated
from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException

from app.cores.config import settings
from app.cores.security import hash_password
from app.schema.user import TokenData
from app.cores.database import db
from app.cores.security import oauth2_scheme


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_user(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    token_user = TokenData(username=email).model_dump()
    user = await get_user(email=token_user['username'])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def clean_user(user_dict: dict):
    user_dict['password'] = hash_password(user_dict['password'])
    user_dict['created_at'] = datetime.now()
    user_dict['updated_at'] = datetime.now()
    user_dict['blogs'] = []
    return user_dict
