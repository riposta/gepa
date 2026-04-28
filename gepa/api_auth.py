from fastapi import Header, HTTPException, status
from gepa.config.settings import settings


async def verify_api_key(x_api_key: str = Header(default="")) -> None:
    if settings.api_key.get_secret_value() and x_api_key != settings.api_key.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy klucz API.",
        )
