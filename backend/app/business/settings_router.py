"""Router de configuración de empresa (admin only)."""
import os
import uuid
import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.router import get_admin_user
from app.auth.model import User
from app.business.model import CompanySettings
from app.business.schema import CompanySettingsResponse, CompanySettingsUpdate

router = APIRouter(prefix="/settings", tags=["Configuración"])


@router.get("/", response_model=CompanySettingsResponse)
async def get_company_settings(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la configuración de empresa del país (solo admin)."""
    result = await db.execute(
        select(CompanySettings).where(
            CompanySettings.country_code == current_user.country_code
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = CompanySettings(
            country_code=current_user.country_code,
            company_name="Mi Empresa",
        )
        db.add(settings)
        await db.flush()
        await db.refresh(settings)

    return settings


@router.patch("/", response_model=CompanySettingsResponse)
async def update_company_settings(
    data: CompanySettingsUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza la configuración de empresa (solo admin)."""
    result = await db.execute(
        select(CompanySettings).where(
            CompanySettings.country_code == current_user.country_code
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = CompanySettings(country_code=current_user.country_code)
        db.add(settings)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    await db.flush()
    await db.refresh(settings)
    return settings


ALLOWED_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_SIZE = 2 * 1024 * 1024
UPLOAD_DIR = "/uploads/logos"


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Sube el logo de la empresa (solo admin). PNG/JPG, max 2MB."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_TYPES)}",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede 2MB")

    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{current_user.country_code}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(path, "wb") as f:
        f.write(contents)

    logo_url = f"/uploads/logos/{filename}"

    result = await db.execute(
        select(CompanySettings).where(
            CompanySettings.country_code == current_user.country_code
        )
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = CompanySettings(country_code=current_user.country_code, logo_url=logo_url)
        db.add(settings)
    else:
        settings.logo_url = logo_url
    await db.flush()
    await db.refresh(settings)

    return {"logo_url": logo_url, "message": "Logo actualizado"}


@router.delete("/logo")
async def delete_logo(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina el logo de la empresa (solo admin)."""
    result = await db.execute(
        select(CompanySettings).where(
            CompanySettings.country_code == current_user.country_code
        )
    )
    settings = result.scalar_one_or_none()
    if settings:
        settings.logo_url = None
        await db.flush()

    return {"message": "Logo eliminado"}
