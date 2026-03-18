"""Router para el módulo de Negocio (Productos y Precios por Región)."""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.negocio import Producto, PrecioPorRegion
from app.schemas.negocio import (
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse,
    ProductoListResponse,
    PrecioPorRegionCreate,
    PrecioPorRegionUpdate,
    PrecioPorRegionResponse,
)

router = APIRouter(prefix="/api/negocio", tags=["negocio"])


@router.get("/productos", response_model=list[ProductoListResponse])
async def list_productos(db: AsyncSession = Depends(get_db)):
    """Lista todos los productos."""
    result = await db.execute(select(Producto).order_by(Producto.id))
    productos = result.scalars().all()
    return productos


@router.post("/productos", response_model=ProductoResponse)
async def create_producto(data: ProductoCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo producto con precios por región."""
    existing = await db.execute(select(Producto).where(Producto.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="SKU ya existe")

    producto = Producto(
        sku=data.sku,
        nombre=data.nombre,
        descripcion=data.descripcion,
        categoria=data.categoria,
    )
    db.add(producto)
    await db.flush()

    for precio_data in data.precios:
        precio = PrecioPorRegion(
            producto_id=producto.id,
            region=precio_data.region,
            precio_neto=precio_data.precio_neto,
            tipo_iva=precio_data.tipo_iva,
            observaciones=precio_data.observaciones,
        )
        db.add(precio)

    await db.refresh(producto)
    return producto


@router.get("/productos/{producto_id}", response_model=ProductoResponse)
async def get_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un producto por ID con sus precios."""
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.patch("/productos/{producto_id}", response_model=ProductoResponse)
async def update_producto(
    producto_id: int, data: ProductoUpdate, db: AsyncSession = Depends(get_db)
):
    """Actualiza un producto."""
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(producto, key, value)

    await db.refresh(producto)
    return producto


@router.delete("/productos/{producto_id}")
async def delete_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un producto."""
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(producto)
    return {"message": "Producto eliminado"}


@router.post("/productos/{producto_id}/precios", response_model=PrecioPorRegionResponse)
async def add_precio(
    producto_id: int, data: PrecioPorRegionCreate, db: AsyncSession = Depends(get_db)
):
    """Agrega un precio por región a un producto."""
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    existing = await db.execute(
        select(PrecioPorRegion).where(
            PrecioPorRegion.producto_id == producto_id,
            PrecioPorRegion.region == data.region,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe precio para esa región")

    precio = PrecioPorRegion(
        producto_id=producto_id,
        region=data.region,
        precio_neto=data.precio_neto,
        tipo_iva=data.tipo_iva,
        observaciones=data.observaciones,
    )
    db.add(precio)
    await db.refresh(precio)
    return precio


@router.patch("/precios/{precio_id}", response_model=PrecioPorRegionResponse)
async def update_precio(
    precio_id: int, data: PrecioPorRegionUpdate, db: AsyncSession = Depends(get_db)
):
    """Actualiza un precio por región."""
    result = await db.execute(select(PrecioPorRegion).where(PrecioPorRegion.id == precio_id))
    precio = result.scalar_one_or_none()
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(precio, key, value)

    await db.refresh(precio)
    return precio


@router.delete("/precios/{precio_id}")
async def delete_precio(precio_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un precio por región."""
    result = await db.execute(select(PrecioPorRegion).where(PrecioPorRegion.id == precio_id))
    precio = result.scalar_one_or_none()
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")

    await db.delete(precio)
    return {"message": "Precio eliminado"}
