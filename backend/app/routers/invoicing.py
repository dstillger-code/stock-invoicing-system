"""Router del módulo Facturación (impuestos por país, Strategy)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.invoicing import TaxConfig
from app.schemas.invoicing import TaxConfigResponse

router = APIRouter(prefix="/invoicing", tags=["Invoicing"])


@router.get("/tax/health")
async def tax_health():
    """Health check del módulo de facturación/impuestos."""
    return {"module": "invoicing", "status": "ok"}


@router.get("/tax/config", response_model=list[TaxConfigResponse])
async def list_tax_config(db: AsyncSession = Depends(get_db)):
    """Lista la configuración de impuestos por país (Chile 19%, Argentina, etc.)."""
    result = await db.execute(select(TaxConfig).where(TaxConfig.is_active).order_by(TaxConfig.country_code))
    return result.scalars().all()
