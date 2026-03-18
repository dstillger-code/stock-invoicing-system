"""Tests para el módulo de impuestos."""
import pytest
from app.billing.taxes import calculate_total, calculate_invoice_items, IVA_RATES


class TestTaxCalculation:
    """Tests unitarios para el cálculo de impuestos."""
    
    def test_iva_rates_defined(self):
        """Verifica que las tasas de IVA estén definidas."""
        assert "CL" in IVA_RATES
        assert "AR" in IVA_RATES
        assert IVA_RATES["CL"]["default"] == 19.0
        assert IVA_RATES["AR"]["default"] == 21.0
    
    def test_calculate_total_chile_19_percent(self):
        """Test: Chile aplica 19% de IVA."""
        result = calculate_total(100.00, "CL")
        
        assert result["net_price"] == 100.00
        assert result["tax_rate"] == 19.0
        assert result["tax_amount"] == 19.00
        assert result["total"] == 119.00
        assert result["country_code"] == "CL"
    
    def test_calculate_total_argentina_21_percent(self):
        """Test: Argentina aplica 21% de IVA por defecto."""
        result = calculate_total(100.00, "AR")
        
        assert result["net_price"] == 100.00
        assert result["tax_rate"] == 21.0
        assert result["tax_amount"] == 21.00
        assert result["total"] == 121.00
        assert result["country_code"] == "AR"
    
    def test_calculate_total_argentina_reduced(self):
        """Test: Argentina IVA reducido 10.5%."""
        result = calculate_total(100.00, "AR", tax_type="reduced")
        
        assert result["tax_rate"] == 10.5
        assert result["tax_amount"] == 10.50
        assert result["total"] == 110.50
        assert result["tax_type"] == "reduced"
    
    def test_calculate_total_argentina_additional(self):
        """Test: Argentina IVA adicional 27%."""
        result = calculate_total(100.00, "AR", tax_type="additional")
        
        assert result["tax_rate"] == 27.0
        assert result["tax_amount"] == 27.00
        assert result["total"] == 127.00
        assert result["tax_type"] == "additional"
    
    def test_calculate_total_invalid_country(self):
        """Test: Error con código de país inválido."""
        with pytest.raises(ValueError, match="Código de país no soportado"):
            calculate_total(100.00, "BR")
    
    def test_calculate_total_invalid_tax_type(self):
        """Test: Error con tipo de impuesto inválido para AR."""
        with pytest.raises(ValueError, match="Tipo de impuesto no válido"):
            calculate_total(100.00, "AR", tax_type="invalid")
    
    def test_calculate_total_zero_price(self):
        """Test: Precio cero."""
        result = calculate_total(0.00, "CL")
        
        assert result["net_price"] == 0.00
        assert result["tax_amount"] == 0.00
        assert result["total"] == 0.00
    
    def test_calculate_total_large_price(self):
        """Test: Precio grande."""
        result = calculate_total(999999.99, "CL")
        
        assert result["net_price"] == 999999.99
        assert result["tax_amount"] == 189999.9981
        assert result["total"] == 1189999.99
    
    def test_calculate_total_chile_with_none_tax_type(self):
        """Test: Chile ignora tax_type."""
        result = calculate_total(100.00, "CL", tax_type="reduced")
        
        assert result["tax_rate"] == 19.0
        assert result["tax_type"] is None


class TestInvoiceCalculation:
    """Tests para cálculo de facturas con múltiples items."""
    
    def test_calculate_invoice_single_item(self):
        """Test: Factura con un item."""
        items = [{"description": "Producto A", "net_price": 100.00}]
        
        result = calculate_invoice_items(items, "CL")
        
        assert len(result["items"]) == 1
        assert result["subtotal"] == 100.00
        assert result["total_tax"] == 19.00
        assert result["total"] == 119.00
    
    def test_calculate_invoice_multiple_items(self):
        """Test: Factura con múltiples items."""
        items = [
            {"description": "Producto A", "net_price": 100.00},
            {"description": "Producto B", "net_price": 50.00},
            {"description": "Producto C", "net_price": 25.00},
        ]
        
        result = calculate_invoice_items(items, "CL")
        
        assert len(result["items"]) == 3
        assert result["subtotal"] == 175.00
        assert result["total_tax"] == 33.25
        assert result["total"] == 208.25
    
    def test_calculate_invoice_argentina(self):
        """Test: Factura en Argentina."""
        items = [
            {"description": "Producto A", "net_price": 100.00},
            {"description": "Producto B", "net_price": 100.00},
        ]
        
        result = calculate_invoice_items(items, "AR", tax_type="reduced")
        
        assert result["total_tax"] == 21.00
        assert result["total"] == 221.00
    
    def test_calculate_invoice_empty(self):
        """Test: Factura vacía."""
        result = calculate_invoice_items([], "CL")
        
        assert len(result["items"]) == 0
        assert result["subtotal"] == 0.0
        assert result["total_tax"] == 0.0
        assert result["total"] == 0.0
