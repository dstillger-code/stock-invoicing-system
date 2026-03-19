"""Router del módulo Products (CRUD protegido por roles)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.router import get_current_user
from app.auth.model import User
from app.billing.model import Product, ProductPrice, Inventory
from app.billing.products_schema import (
    ProductCreate,
    ProductUpdate,
    ProductPriceUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter(prefix="/products", tags=["Products"])


def check_edit_permission(user: User) -> None:
    if user.role not in ("accountant", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Solo contadores y administradores pueden modificar productos",
        )


def check_delete_permission(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo el administrador puede eliminar productos",
        )


async def _auto_deactivate_if_no_stock(product_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(Inventory).where(Inventory.product_id == product_id)
    )
    inventory = result.scalar_one_or_none()
    if inventory and inventory.quantity <= 0:
        prod_result = await db.execute(select(Product).where(Product.id == product_id))
        product = prod_result.scalar_one_or_none()
        if product and product.is_active:
            product.is_active = False


@router.get("/", response_model=list[ProductListResponse])
async def list_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los productos con cantidad. Todos los roles pueden ver."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.inventory))
        .order_by(Product.name)
    )
    products = result.scalars().all()

    return [
        ProductListResponse(
            id=p.id,
            sku=p.sku,
            name=p.name,
            description=p.description,
            category=p.category,
            is_active=p.is_active,
            created_at=p.created_at,
            quantity=p.inventory.quantity if p.inventory else 0,
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene un producto por ID con precios."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        is_active=product.is_active,
        created_at=product.created_at,
        prices=product.precios,
        quantity=product.inventory.quantity if product.inventory else 0,
    )


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea un nuevo producto (accountant/admin)."""
    check_edit_permission(current_user)

    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El SKU ya existe")

    product = Product(
        sku=data.sku,
        name=data.name,
        description=data.description,
        category=data.category,
        is_active=True,
    )
    db.add(product)
    await db.flush()

    for price_data in data.prices:
        price = ProductPrice(
            product_id=product.id,
            country_code=price_data.country_code,
            net_price=price_data.net_price,
            tax_rate=price_data.tax_rate,
            is_exempt=price_data.is_exempt,
        )
        db.add(price)

    inventory = Inventory(product_id=product.id, quantity=0)
    db.add(inventory)

    await db.flush()
    await db.refresh(product)

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios))
        .where(Product.id == product.id)
    )
    product = result.scalar_one()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        is_active=product.is_active,
        created_at=product.created_at,
        prices=product.precios,
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza un producto (accountant/admin)."""
    check_edit_permission(current_user)

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "sku" in update_data:
        existing = await db.execute(
            select(Product).where(Product.sku == update_data["sku"], Product.id != product_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="El SKU ya existe")

    for key, value in update_data.items():
        setattr(product, key, value)

    await db.flush()
    await db.refresh(product)

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product.id)
    )
    product = result.scalar_one()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        is_active=product.is_active,
        created_at=product.created_at,
        prices=product.precios,
        quantity=product.inventory.quantity if product.inventory else 0,
    )


@router.patch("/{product_id}/prices", response_model=ProductResponse)
async def update_product_prices(
    product_id: UUID,
    prices: list[ProductPriceUpdate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza precios de un producto (accountant/admin)."""
    check_edit_permission(current_user)

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for price_data in prices:
        existing = await db.execute(
            select(ProductPrice).where(
                ProductPrice.product_id == product_id,
                ProductPrice.country_code == price_data.country_code,
            )
        )
        existing_price = existing.scalar_one_or_none()

        if existing_price:
            update_data = price_data.model_dump(exclude_unset=True, exclude={"country_code"})
            for key, value in update_data.items():
                setattr(existing_price, key, value)
        else:
            new_price = ProductPrice(
                product_id=product_id,
                country_code=price_data.country_code,
                net_price=price_data.net_price or 0,
                tax_rate=price_data.tax_rate or 0,
                is_exempt=price_data.is_exempt or False,
            )
            db.add(new_price)

    await db.flush()

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id)
    )
    product = result.scalar_one()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        is_active=product.is_active,
        created_at=product.created_at,
        prices=product.precios,
        quantity=product.inventory.quantity if product.inventory else 0,
    )


@router.post("/{product_id}/toggle-active", response_model=ProductResponse)
async def toggle_product_active(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Activa/desactiva un producto (accountant/admin)."""
    check_edit_permission(current_user)

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product.is_active = not product.is_active
    await db.flush()
    await db.refresh(product)

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id)
    )
    product = result.scalar_one()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        is_active=product.is_active,
        created_at=product.created_at,
        prices=product.precios,
        quantity=product.inventory.quantity if product.inventory else 0,
    )


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina un producto (solo admin)."""
    check_delete_permission(current_user)

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(product)
    await db.flush()
