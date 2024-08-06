from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings
from app.schema.response import ErrorResponse


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_NAME: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="Error",
            message=exc.detail
        ).model_dump()
    )
