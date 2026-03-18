"""Router de autenticación (esquema auth)."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.auth import User

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.get("/health")
async def auth_health():
    """Health check del módulo Auth."""
    return {"module": "auth", "status": "ok"}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Inicio de sesión - retorna usuario con permisos."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    return {
        "access_token": user.email,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "rol": user.rol,
            "permisos_modulos": user.permisos_modulos or [],
        },
    }


@router.post("/register")
async def register(
    email: str,
    password: str,
    full_name: str | None = None,
    rol: str = "usuario",
    permisos_modulos: list[str] = ["stock", "invoicing", "negocio"],
    db: AsyncSession = Depends(get_db),
):
    """Registro de nuevo usuario (para desarrollo)."""
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        rol=rol,
        permisos_modulos=permisos_modulos,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "rol": new_user.rol,
        "permisos_modulos": new_user.permisos_modulos,
    }
