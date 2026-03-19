"""Router de Facturación - Generación de Facturas y Boletas."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.router import get_current_user
from app.auth.model import User
from app.billing.model import Product, ProductPrice, Inventory
from app.billing.taxes import calculate_total, IVA_RATES

router = APIRouter(prefix="/billing", tags=["Facturación"])


class InvoiceItem(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class InvoiceCreate(BaseModel):
    document_type: str = Field(..., pattern="^(factura|boleta)$")
    tax_type: str | None = Field(None, pattern="^(default|reduced|additional)?$")
    items: list[InvoiceItem] = Field(..., min_length=1)


class InvoiceItemResponse(BaseModel):
    product_id: str
    sku: str
    name: str
    quantity: int
    unit_price: float
    net_amount: float
    tax_rate: float
    tax_amount: float
    total: float


class InvoiceResponse(BaseModel):
    document_type: str
    document_number: str
    country_code: str
    country_name: str
    issued_at: datetime
    issuer_name: str
    items: list[InvoiceItemResponse]
    subtotal: float
    tax_rate: float
    tax_type: str | None
    tax_amount: float
    total: float
    currency: str


_INVOICE_COUNTER: dict[str, int] = {}


def _get_next_number(country: str) -> str:
    year = datetime.utcnow().year
    _INVOICE_COUNTER.setdefault(country, 0)
    _INVOICE_COUNTER[country] += 1
    return f"{year}-{country}-{_INVOICE_COUNTER[country]:06d}"


@router.get("/products")
async def list_billing_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista productos activos del país para facturar."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(
            Product.country_code == current_user.country_code,
            Product.is_active == True,
        )
        .order_by(Product.name)
    )
    products = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "stock": p.inventory.quantity if p.inventory else 0,
            "unit_price": float(p.precios[0].net_price) if p.precios else 0,
        }
        for p in products
    ]


@router.get("/tax-rates")
async def get_tax_rates(
    current_user: User = Depends(get_current_user),
):
    """Devuelve las tasas de impuesto del país configurado."""
    country = current_user.country_code
    rates = IVA_RATES.get(country, {})
    return {
        "country_code": country,
        "rates": rates,
        "document_types": (
            ["factura", "boleta"] if country == "AR" else ["factura"]
        ),
    }


@router.post("/invoice")
async def create_invoice(
    data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genera una factura o boleta con cálculo de impuestos."""
    if current_user.country_code == "AR" and data.document_type == "boleta":
        tax_rate = 0.0
    elif current_user.country_code == "CL":
        tax_rate = 19.0
    elif current_user.country_code == "AR":
        ar_rates = IVA_RATES.get("AR", {})
        if data.tax_type == "reduced":
            tax_rate = ar_rates.get("reduced", 10.5)
        elif data.tax_type == "additional":
            tax_rate = ar_rates.get("additional", 27.0)
        else:
            tax_rate = ar_rates.get("default", 21.0)
    else:
        tax_rate = 0.0

    product_ids = [item.product_id for item in data.items]
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.precios), selectinload(Product.inventory))
        .where(
            Product.id.in_(product_ids),
            Product.country_code == current_user.country_code,
        )
    )
    products = {p.id: p for p in result.scalars().all()}

    invoice_items = []
    subtotal = 0.0

    for item in data.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        if not product.is_active:
            raise HTTPException(status_code=400, detail=f"Producto {product.name} está inactivo")

        unit_price = float(product.precios[0].net_price) if product.precios else 0.0
        net_amount = round(unit_price * item.quantity, 2)
        tax_amount = round(net_amount * (tax_rate / 100), 2)
        total = round(net_amount + tax_amount, 2)
        subtotal += net_amount

        invoice_items.append(InvoiceItemResponse(
            product_id=str(product.id),
            sku=product.sku,
            name=product.name,
            quantity=item.quantity,
            unit_price=unit_price,
            net_amount=net_amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total,
        ))

        if product.inventory and product.inventory.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {product.name}: disponible {product.inventory.quantity}",
            )

    total_tax = round(subtotal * (tax_rate / 100), 2)
    total = round(subtotal + total_tax, 2)

    currency_map = {"CL": "CLP", "AR": "ARS"}
    name_map = {"CL": "Chile", "AR": "Argentina"}

    return InvoiceResponse(
        document_type=data.document_type,
        document_number=_get_next_number(current_user.country_code),
        country_code=current_user.country_code,
        country_name=name_map.get(current_user.country_code, current_user.country_code),
        issued_at=datetime.utcnow(),
        issuer_name=current_user.full_name or current_user.email,
        items=invoice_items,
        subtotal=round(subtotal, 2),
        tax_rate=tax_rate,
        tax_type=data.tax_type,
        tax_amount=total_tax,
        total=total,
        currency=currency_map.get(current_user.country_code, "USD"),
    )
