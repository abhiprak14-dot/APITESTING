from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Validates the X-API-Key header against the configured API_KEY.
    """
    if api_key_header == settings.api_key:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing X-API-Key",
    )
