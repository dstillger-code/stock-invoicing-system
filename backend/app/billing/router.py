"""Router del módulo Billing (impuestos por país, Strategy)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.billing.model import Country

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/tax/health")
async def tax_health():
    """Health check del módulo de facturación/impuestos."""
    return {"module": "billing", "status": "ok"}


@router.get("/countries", response_model=list)
async def list_countries(db: AsyncSession = Depends(get_db)):
    """Lista países con configuración de impuestos."""
    result = await db.execute(select(Country).order_by(Country.code))
    return result.scalars().all()
