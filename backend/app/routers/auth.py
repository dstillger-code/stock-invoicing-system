"""Router de autenticación (esquema auth)."""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/health")
async def auth_health():
    """Health check del módulo Auth."""
    return {"module": "auth", "status": "ok"}
