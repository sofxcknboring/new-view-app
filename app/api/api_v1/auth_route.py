from core.config import settings
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key")


@router.get("/auth")
async def get_auth(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return {"message": "Access granted"}
