"""Estrategia de impuestos para Chile (IVA 19%)."""
from decimal import Decimal

from .base import TaxStrategy


class ChileTaxStrategy(TaxStrategy):
    """Chile: IVA único 19%."""

    country_code = "CL"

    def get_vat_rate(self) -> Decimal:
        return Decimal("19.00")

    def compute_tax(self, base_amount: Decimal) -> Decimal:
        return (base_amount * self.get_vat_rate() / 100).quantize(Decimal("0.01"))
