"""Tests para endpoints de inventario."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def get_auth_token(client: AsyncClient) -> str:
    """Helper: Obtiene token de autenticación."""
    await client.post(
        "/api/auth/register",
        params={"email": "inventory@test.com", "password": "password123"},
    )
    response = await client.post(
        "/api/auth/login",
        data={"username": "inventory@test.com", "password": "password123"},
    )
    return response.json()["access_token"]


class TestStockEndpoints:
    """Tests para endpoints de stock (CRUD básico)."""
    
    @pytest.mark.asyncio
    async def test_list_stock_items_empty(self, client: AsyncClient):
        """Test: Lista vacía de stock."""
        response = await client.get("/api/stock/items")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @pytest.mark.asyncio
    async def test_create_stock_item(self, client: AsyncClient):
        """Test: Crear item de stock."""
        response = await client.post(
            "/api/stock/items",
            json={
                "sku": "TEST-001",
                "nombre": "Producto de Test",
                "cantidad": 10,
                "precio_base": 100.00,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == "TEST-001"
        assert data["nombre"] == "Producto de Test"
        assert data["cantidad"] == 10
        assert data["precio_base"] == "100.00"
    
    @pytest.mark.asyncio
    async def test_create_duplicate_sku(self, client: AsyncClient):
        """Test: No permite SKU duplicado."""
        await client.post(
            "/api/stock/items",
            json={"sku": "DUP-001", "nombre": "Item 1", "cantidad": 5},
        )
        
        response = await client.post(
            "/api/stock/items",
            json={"sku": "DUP-001", "nombre": "Item 2", "cantidad": 10},
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_stock_item(self, client: AsyncClient):
        """Test: Obtener item específico."""
        create_response = await client.post(
            "/api/stock/items",
            json={"sku": "GET-001", "nombre": "Get Test", "cantidad": 3},
        )
        item_id = create_response.json()["id"]
        
        response = await client.get(f"/api/stock/items/{item_id}")
        
        assert response.status_code == 200
        assert response.json()["sku"] == "GET-001"
    
    @pytest.mark.asyncio
    async def test_update_stock_item(self, client: AsyncClient):
        """Test: Actualizar item."""
        create_response = await client.post(
            "/api/stock/items",
            json={"sku": "UPD-001", "nombre": "Original", "cantidad": 5},
        )
        item_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/stock/items/{item_id}",
            json={"cantidad": 20},
        )
        
        assert response.status_code == 200
        assert response.json()["cantidad"] == 20
        assert response.json()["nombre"] == "Original"
    
    @pytest.mark.asyncio
    async def test_delete_stock_item(self, client: AsyncClient):
        """Test: Eliminar item."""
        create_response = await client.post(
            "/api/stock/items",
            json={"sku": "DEL-001", "nombre": "Delete Me", "cantidad": 1},
        )
        item_id = create_response.json()["id"]
        
        delete_response = await client.delete(f"/api/stock/items/{item_id}")
        assert delete_response.status_code == 204
        
        get_response = await client.get(f"/api/stock/items/{item_id}")
        assert get_response.status_code == 404


class TestBillingEndpoints:
    """Tests para endpoints de facturación."""
    
    @pytest.mark.asyncio
    async def test_tax_health(self, client: AsyncClient):
        """Test: Health check de impuestos."""
        response = await client.get("/api/billing/tax/health")
        
        assert response.status_code == 200
        assert response.json() == {"module": "billing", "status": "ok"}
    
    @pytest.mark.asyncio
    async def test_list_countries(self, client: AsyncClient):
        """Test: Listar países."""
        response = await client.get("/api/billing/countries")
        
        assert response.status_code == 200
        countries = response.json()
        assert isinstance(countries, list)
        # Los países se crean en el seed
    
    @pytest.mark.asyncio
    async def test_calculate_endpoint(self, client: AsyncClient):
        """Test: Endpoint de cálculo de precios con IVA."""
        token = await get_auth_token(client)
        
        response = await client.post(
            "/api/inventory/calculate",
            params={"net_price": 100, "country_code": "CL"},
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["net_price"] == 100
        assert data["tax_rate"] == 19.0
        assert data["total"] == 119.00
    
    @pytest.mark.asyncio
    async def test_calculate_with_tax_type(self, client: AsyncClient):
        """Test: Cálculo con tipo de IVA específico."""
        token = await get_auth_token(client)
        
        response = await client.post(
            "/api/inventory/calculate",
            params={
                "net_price": 100,
                "country_code": "AR",
                "tax_type": "reduced",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tax_rate"] == 10.5
        assert data["total"] == 110.50


class TestInventoryEndpoints:
    """Tests para endpoints de inventario protegidos."""
    
    @pytest.mark.asyncio
    async def test_get_inventory(self, client: AsyncClient):
        """Test: Obtener lista de inventario."""
        token = await get_auth_token(client)
        
        response = await client.get(
            "/api/inventory/",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_products" in data
        assert "user" in data
    
    @pytest.mark.asyncio
    async def test_get_inventory_unauthorized(self, client: AsyncClient):
        """Test: Inventario requiere autenticación."""
        response = await client.get("/api/inventory/")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_product_inventory_not_found(self, client: AsyncClient):
        """Test: Producto no encontrado."""
        token = await get_auth_token(client)
        
        response = await client.get(
            "/api/inventory/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404
