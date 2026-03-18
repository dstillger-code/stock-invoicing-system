"""Strategy base para cálculo de impuestos por país."""
from abc import ABC, abstractmethod
from decimal import Decimal


class TaxStrategy(ABC):
    """Interfaz del motor de impuestos internacional."""

    country_code: str = ""

    @abstractmethod
    def get_vat_rate(self) -> Decimal:
        """Devuelve la alícuota principal de IVA (ej. 19 para Chile)."""
        pass

    @abstractmethod
    def compute_tax(self, base_amount: Decimal) -> Decimal:
        """Calcula el impuesto sobre base_amount."""
        pass

    def get_extra_rates(self) -> dict[str, Decimal]:
        """Opcional: alícuotas adicionales (Argentina). Por defecto vacío."""
        return {}

    def get_perception_rates(self) -> dict[str, Decimal]:
        """Opcional: percepciones (Argentina). Por defecto vacío."""
        return {}
