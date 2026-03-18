"""Cálculo de impuestos por país."""

IVA_RATES = {
    "CL": {
        "default": 19.0,
        "exempt": 0.0,
    },
    "AR": {
        "default": 21.0,
        "reduced": 10.5,
        "additional": 27.0,
        "exempt": 0.0,
    },
}


def calculate_total(
    net_price: float,
    country_code: str,
    tax_type: str | None = None,
) -> dict:
    """
    Calcula el precio total incluyendo impuestos.

    Args:
        net_price: Precio sin IVA
        country_code: Código de país ('CL' o 'AR')
        tax_type: Tipo de impuesto (opcional, para Argentina)
            - None: usa default
            - 'reduced': 10.5% en Argentina
            - 'additional': 27% en Argentina

    Returns:
        dict con:
            - net_price: precio original
            - tax_rate: tasa aplicada
            - tax_amount: monto del impuesto
            - total: precio final con IVA
            - country_code: país usado
    """
    if country_code not in IVA_RATES:
        raise ValueError(f"Código de país no soportado: {country_code}")

    rates = IVA_RATES[country_code]

    if country_code == "CL":
        tax_rate = rates["default"]
    elif country_code == "AR":
        if tax_type is None:
            tax_rate = rates["default"]
        elif tax_type == "reduced":
            tax_rate = rates["reduced"]
        elif tax_type == "additional":
            tax_rate = rates["additional"]
        else:
            raise ValueError(f"Tipo de impuesto no válido para AR: {tax_type}")
    else:
        tax_rate = rates.get("default", 0)

    tax_amount = round(net_price * (tax_rate / 100), 2)
    total = round(net_price + tax_amount, 2)

    return {
        "net_price": net_price,
        "tax_rate": tax_rate,
        "tax_type": tax_type,
        "tax_amount": tax_amount,
        "total": total,
        "country_code": country_code,
    }


def calculate_invoice_items(
    items: list[dict],
    country_code: str,
    tax_type: str | None = None,
) -> dict:
    """
    Calcula totales para una lista de items de factura.

    Args:
        items: Lista de dicts con 'description' y 'net_price'
        country_code: Código de país
        tax_type: Tipo de impuesto (para AR)

    Returns:
        dict con subtotal, impuestos y total
    """
    calculated_items = []
    subtotal = 0.0

    for item in items:
        result = calculate_total(item["net_price"], country_code, tax_type)
        calculated_items.append({
            "description": item.get("description", ""),
            **result,
        })
        subtotal += result["net_price"]

    total_tax = sum(item["tax_amount"] for item in calculated_items)
    total = round(subtotal + total_tax, 2)

    return {
        "items": calculated_items,
        "subtotal": round(subtotal, 2),
        "total_tax": round(total_tax, 2),
        "total": total,
        "country_code": country_code,
    }
