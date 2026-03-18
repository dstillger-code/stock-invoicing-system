"""Estrategia de impuestos para Argentina (múltiples alícuotas y percepciones)."""
from decimal import Decimal

from .base import TaxStrategy


class ArgentinaTaxStrategy(TaxStrategy):
    """
    Argentina: múltiples alícuotas de IVA y percepciones.
    Estructura lista para extender con extra_rates y perception_rates.
    """

    country_code = "AR"

    def __init__(self, default_rate: Decimal = Decimal("21"), extra_rates: dict | None = None, perception_rates: dict | None = None):
        self._default_rate = default_rate
        self._extra_rates = extra_rates or {}
        self._perception_rates = perception_rates or {}

    def get_vat_rate(self) -> Decimal:
        return self._default_rate

    def compute_tax(self, base_amount: Decimal) -> Decimal:
        return (base_amount * self.get_vat_rate() / 100).quantize(Decimal("0.01"))

    def get_extra_rates(self) -> dict[str, Decimal]:
        return {k: Decimal(str(v)) for k, v in self._extra_rates.items()}

    def get_perception_rates(self) -> dict[str, Decimal]:
        return {k: Decimal(str(v)) for k, v in self._perception_rates.items()}
