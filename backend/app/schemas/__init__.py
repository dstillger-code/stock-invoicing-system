"""Esquemas Pydantic para request/response."""
from .stock import StockItemCreate, StockItemUpdate, StockItemResponse
from .invoicing import TaxConfigCreate, TaxConfigResponse

__all__ = [
    "StockItemCreate",
    "StockItemUpdate",
    "StockItemResponse",
    "TaxConfigCreate",
    "TaxConfigResponse",
]
