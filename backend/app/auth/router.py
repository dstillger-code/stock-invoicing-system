"""Router de autenticación (esquema auth)."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.database import get_db
from app.core.config import settings
from app.auth.model import User

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario desactivado")
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.email != "admin@stock.com":
        raise HTTPException(status_code=403, detail="Solo el administrador puede acceder")
    return current_user


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "operator"
    allowed_modules: list[str] = ["stock"]
    expiration_days: int = 30


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    allowed_modules: Optional[list[str]] = None
    is_active: Optional[bool] = None
    expiration_days: Optional[int] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    allowed_modules: list[str]
    password_changed: bool
    expiration_days: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("/health")
async def auth_health():
    return {"module": "auth", "status": "ok"}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    if user.expiration_days == 0:
        raise HTTPException(status_code=403, detail="Usuario caducado. Contacte al administrador.")

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "allowed_modules": user.allowed_modules or [],
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "allowed_modules": user.allowed_modules or [],
            "password_changed": user.password_changed,
        },
    }


@router.post("/register")
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed_password = get_password_hash(data.password)
    new_user = User(
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name,
        role=data.role,
        allowed_modules=data.allowed_modules,
        expiration_days=data.expiration_days,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.role,
    }


@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    current_user.password_hash = get_password_hash(data.new_password)
    current_user.password_changed = True
    await db.flush()

    return {"message": "Contraseña actualizada correctamente"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "allowed_modules": current_user.allowed_modules or [],
        "password_changed": current_user.password_changed,
        "expiration_days": current_user.expiration_days,
    }


@router.post("/decrement-expiration")
async def decrement_expiration(db: AsyncSession = Depends(get_db)):
    """Decrementa un día de expiración a todos los usuarios no-admin activos."""
    result = await db.execute(
        update(User)
        .where(User.email != "admin@stock.com")
        .where(User.is_active == True)
        .where(User.expiration_days > 0)
        .values(expiration_days=User.expiration_days - 1)
    )
    await db.commit()
    return {"message": f"Expiración decrementada en {result.rowcount} usuarios"}


class UserAdminResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    allowed_modules: list[str]
    password_changed: bool
    expiration_days: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/admin/users", response_model=list[UserAdminResponse])
async def list_users(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los usuarios (solo admin)."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        UserAdminResponse(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            allowed_modules=u.allowed_modules or [],
            password_changed=u.password_changed,
            expiration_days=u.expiration_days,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.post("/admin/users", response_model=UserAdminResponse)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea un nuevo usuario (solo admin)."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed_password = get_password_hash(data.password)
    new_user = User(
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name,
        role=data.role,
        allowed_modules=data.allowed_modules,
        expiration_days=data.expiration_days,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return UserAdminResponse(
        id=str(new_user.id),
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
        allowed_modules=new_user.allowed_modules or [],
        password_changed=new_user.password_changed,
        expiration_days=new_user.expiration_days,
        created_at=new_user.created_at,
    )


@router.patch("/admin/users/{user_id}", response_model=UserAdminResponse)
async def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza un usuario (solo admin)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.email == "admin@stock.com" and data.is_active == False:
        raise HTTPException(status_code=400, detail="No se puede desactivar el usuario admin")

    update_data = data.model_dump(exclude_unset=True)

    if "allowed_modules" in update_data:
        user.allowed_modules = update_data["allowed_modules"]
    else:
        for key, value in update_data.items():
            setattr(user, key, value)

    await db.flush()
    await db.refresh(user)

    return UserAdminResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        allowed_modules=user.allowed_modules or [],
        password_changed=user.password_changed,
        expiration_days=user.expiration_days,
        created_at=user.created_at,
    )


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina un usuario (solo admin)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.email == "admin@stock.com":
        raise HTTPException(status_code=400, detail="No se puede eliminar el usuario admin")

    await db.delete(user)

    return {"message": "Usuario eliminado"}
