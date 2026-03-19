"""Router del módulo Products (CRUD filtrado por país)."""
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
    ProductResponse,
    ProductListResponse,
)

router = APIRouter(prefix="/products", tags=["Productos"])


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


@router.get("/", response_model=list[ProductListResponse])
async def list_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista productos del país del usuario. Todos los roles pueden ver."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.inventory), selectinload(Product.precios))
        .where(Product.country_code == current_user.country_code)
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
            country_code=p.country_code,
            quantity=p.inventory.quantity if p.inventory else 0,
            prices=[
                {"id": str(price.id), "net_price": float(price.net_price)}
                for price in p.precios
            ],
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene un producto por ID del mismo país."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id, Product.country_code == current_user.country_code)
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
        country_code=product.country_code,
        quantity=product.inventory.quantity if product.inventory else 0,
        prices=[
            {"id": str(price.id), "net_price": float(price.net_price)}
            for price in product.precios
        ],
    )


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea un nuevo producto en el país del usuario (accountant/admin)."""
    check_edit_permission(current_user)

    existing = await db.execute(
        select(Product).where(
            Product.sku == data.sku, Product.country_code == current_user.country_code
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El SKU ya existe en este país")

    product = Product(
        sku=data.sku,
        name=data.name,
        description=data.description,
        category=data.category,
        is_active=True,
        country_code=current_user.country_code,
    )
    db.add(product)
    await db.flush()

    if data.net_price is not None and data.net_price > 0:
        price = ProductPrice(product_id=product.id, net_price=data.net_price)
        db.add(price)

    inventory = Inventory(product_id=product.id, quantity=data.initial_quantity or 0)
    db.add(inventory)

    await db.flush()

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
        country_code=product.country_code,
        quantity=product.inventory.quantity if product.inventory else 0,
        prices=[
            {"id": str(price.id), "net_price": float(price.net_price)}
            for price in product.precios
        ],
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza un producto del mismo país (accountant/admin)."""
    check_edit_permission(current_user)

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id, Product.country_code == current_user.country_code)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "sku" in update_data:
        existing = await db.execute(
            select(Product).where(
                Product.sku == update_data["sku"],
                Product.country_code == current_user.country_code,
                Product.id != product_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="El SKU ya existe en este país")

    for key, value in update_data.items():
        if key == "net_price":
            if product.precios:
                product.precios[0].net_price = value
        else:
            setattr(product, key, value)

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
        country_code=product.country_code,
        quantity=product.inventory.quantity if product.inventory else 0,
        prices=[
            {"id": str(price.id), "net_price": float(price.net_price)}
            for price in product.precios
        ],
    )


@router.post("/{product_id}/toggle-active", response_model=ProductResponse)
async def toggle_product_active(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Activa/desactiva un producto del mismo país (accountant/admin)."""
    check_edit_permission(current_user)

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(Product.id == product_id, Product.country_code == current_user.country_code)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product.is_active = not product.is_active
    await db.flush()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        is_active=product.is_active,
        created_at=product.created_at,
        country_code=product.country_code,
        quantity=product.inventory.quantity if product.inventory else 0,
        prices=[
            {"id": str(price.id), "net_price": float(price.net_price)}
            for price in product.precios
        ],
    )


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina un producto del mismo país (solo admin)."""
    check_delete_permission(current_user)

    result = await db.execute(
        select(Product).where(
            Product.id == product_id, Product.country_code == current_user.country_code
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(product)
