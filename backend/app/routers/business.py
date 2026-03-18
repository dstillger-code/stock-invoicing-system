"""Router para el módulo Business (Productos, Precios, Inventario)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.business import Country, Product, ProductPrice, Inventory
from app.schemas.business import (
    CountryCreate,
    CountryResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductPriceCreate,
    ProductPriceUpdate,
    ProductPriceResponse,
    InventoryUpdate,
    InventoryResponse,
)

router = APIRouter(prefix="/api/business", tags=["business"])


@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(db: AsyncSession = Depends(get_db)):
    """Lista todos los países."""
    result = await db.execute(select(Country).order_by(Country.code))
    return result.scalars().all()


@router.post("/countries", response_model=CountryResponse)
async def create_country(data: CountryCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo país."""
    existing = await db.execute(select(Country).where(Country.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="País ya existe")

    country = Country(**data.model_dump())
    db.add(country)
    await db.refresh(country)
    return country


@router.get("/products", response_model=list[ProductListResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    """Lista productos con cantidad de inventario."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.inventory))
        .order_by(Product.created_at.desc())
    )
    products = result.scalars().all()
    return [
        ProductListResponse(
            id=p.id,
            sku=p.sku,
            name=p.name,
            category=p.category,
            quantity=p.inventory.quantity if p.inventory else 0,
        )
        for p in products
    ]


@router.post("/products", response_model=ProductResponse)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo producto con inventario inicial."""
    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="SKU ya existe")

    product = Product(sku=data.sku, name=data.name, description=data.description, category=data.category)
    db.add(product)
    await db.flush()

    inventory = Inventory(product_id=product.id, quantity=data.initial_quantity)
    db.add(inventory)

    await db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene producto con precios e inventario."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza datos del producto."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await db.refresh(product)
    return product


@router.delete("/products/{product_id}")
async def delete_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    """Elimina producto (y su inventario por CASCADE)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    await db.delete(product)
    return {"message": "Producto eliminado"}


@router.post("/products/{product_id}/prices", response_model=ProductPriceResponse)
async def add_price(product_id: UUID, data: ProductPriceCreate, db: AsyncSession = Depends(get_db)):
    """Agrega precio para un país."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    existing = await db.execute(
        select(ProductPrice).where(
            ProductPrice.product_id == product_id, ProductPrice.country_code == data.country_code
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe precio para ese país")

    price = ProductPrice(product_id=product_id, **data.model_dump())
    db.add(price)
    await db.refresh(price)
    return price


@router.patch("/prices/{price_id}", response_model=ProductPriceResponse)
async def update_price(price_id: UUID, data: ProductPriceUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza precio."""
    result = await db.execute(select(ProductPrice).where(ProductPrice.id == price_id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Precio no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(price, key, value)

    await db.refresh(price)
    return price


@router.delete("/prices/{price_id}")
async def delete_price(price_id: UUID, db: AsyncSession = Depends(get_db)):
    """Elimina precio."""
    result = await db.execute(select(ProductPrice).where(ProductPrice.id == price_id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    await db.delete(price)
    return {"message": "Precio eliminado"}


@router.get("/inventory/{product_id}", response_model=InventoryResponse)
async def get_inventory(product_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene inventario de un producto."""
    result = await db.execute(select(Inventory).where(Inventory.product_id == product_id))
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return inventory


@router.patch("/inventory/{product_id}", response_model=InventoryResponse)
async def update_inventory(product_id: UUID, data: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza cantidad en inventario."""
    result = await db.execute(select(Inventory).where(Inventory.product_id == product_id))
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")

    inventory.quantity = data.quantity
    await db.refresh(inventory)
    return inventory
