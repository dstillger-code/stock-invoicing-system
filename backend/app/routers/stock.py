"""Router del módulo Stock (CRUD de ítems)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.stock import StockItem
from app.schemas.stock import StockItemCreate, StockItemUpdate, StockItemResponse

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("/items", response_model=list[StockItemResponse])
async def list_stock_items(db: AsyncSession = Depends(get_db)):
    """Lista todos los ítems de stock."""
    result = await db.execute(select(StockItem).order_by(StockItem.id))
    return result.scalars().all()


@router.post("/items", response_model=StockItemResponse)
async def create_stock_item(item: StockItemCreate, db: AsyncSession = Depends(get_db)):
    """Crea un ítem de stock."""
    db_item = StockItem(
        sku=item.sku,
        nombre=item.nombre,
        cantidad=item.cantidad,
        precio_base=item.precio_base,
    )
    db.add(db_item)
    await db.flush()
    await db.refresh(db_item)
    return db_item


@router.get("/items/{item_id}", response_model=StockItemResponse)
async def get_stock_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un ítem por ID."""
    result = await db.execute(select(StockItem).where(StockItem.id == item_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return obj


@router.patch("/items/{item_id}", response_model=StockItemResponse)
async def update_stock_item(
    item_id: int, payload: StockItemUpdate, db: AsyncSession = Depends(get_db)
):
    """Actualiza un ítem (parcial)."""
    result = await db.execute(select(StockItem).where(StockItem.id == item_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/items/{item_id}", status_code=204)
async def delete_stock_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un ítem."""
    result = await db.execute(select(StockItem).where(StockItem.id == item_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    await db.delete(obj)
    return None
