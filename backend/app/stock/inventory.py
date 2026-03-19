"""Router del módulo Inventory (protegido por JWT, filtrado por país)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.router import get_current_user
from app.auth.model import User
from app.billing.model import Product, Inventory, ProductPrice
from app.billing.taxes import calculate_total

router = APIRouter(prefix="/inventory", tags=["Inventario"])


@router.get("/")
async def get_inventory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista inventario de productos del país del usuario. Requiere JWT."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.inventory), selectinload(Product.precios))
        .where(Product.country_code == current_user.country_code)
        .order_by(Product.name)
    )
    products = result.scalars().all()

    inventory_list = []
    for product in products:
        item = {
            "product_id": str(product.id),
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "quantity": product.inventory.quantity if product.inventory else 0,
            "net_price": float(product.precios[0].net_price) if product.precios else 0,
        }
        inventory_list.append(item)

    return {
        "user": current_user.email,
        "country": current_user.country_code,
        "total_products": len(inventory_list),
        "items": inventory_list,
    }


@router.get("/{product_id}")
async def get_product_inventory(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene inventario de un producto del mismo país."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.inventory), selectinload(Product.precios))
        .where(Product.id == product_id, Product.country_code == current_user.country_code)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {
        "product_id": str(product.id),
        "sku": product.sku,
        "name": product.name,
        "quantity": product.inventory.quantity if product.inventory else 0,
        "net_price": float(product.precios[0].net_price) if product.precios else 0,
    }


@router.post("/calculate")
async def calculate_product_price(
    net_price: float,
    country_code: str | None = None,
    tax_type: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Calcula precio con impuestos del país configurado. Requiere JWT."""
    result = calculate_total(net_price, country_code or current_user.country_code, tax_type)
    return result


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


@router.patch("/{product_id}")
async def update_inventory_quantity(
    product_id: UUID,
    data: InventoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza stock de un producto del mismo país. Auto-desactiva si stock=0."""
    if current_user.role not in ("accountant", "admin"):
        raise HTTPException(status_code=403, detail="Sin permisos para actualizar inventario")

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.inventory))
        .where(Product.id == product_id, Product.country_code == current_user.country_code)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if not product.inventory:
        inventory = Inventory(product_id=product_id, quantity=data.quantity)
        db.add(inventory)
        await db.flush()
        quantity = data.quantity
    else:
        product.inventory.quantity = data.quantity
        quantity = data.quantity

    if quantity <= 0 and product.is_active:
        product.is_active = False

    await db.flush()

    return {
        "product_id": str(product.id),
        "sku": product.sku,
        "name": product.name,
        "quantity": quantity,
        "is_active": product.is_active,
    }
