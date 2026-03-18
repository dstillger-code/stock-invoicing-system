"""Tests para autenticación."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.router import get_password_hash, verify_password


class TestPasswordHashing:
    """Tests unitarios para hashing de contraseñas."""
    
    def test_hash_password(self):
        """Test: Hash de contraseña genera string."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_verify_password_correct(self):
        """Test: Verificar contraseña correcta."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test: Verificar contraseña incorrecta."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrong_password", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test: Contraseñas diferentes generan hashes diferentes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """Test: Misma contraseña genera hashes diferentes (salt único)."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Different salts
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAuthEndpoints:
    """Tests de integración para endpoints de autenticación."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test: Health check funciona."""
        response = await client.get("/api/auth/health")
        
        assert response.status_code == 200
        assert response.json() == {"module": "auth", "status": "ok"}
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test: Login con credenciales inválidas."""
        response = await client.post(
            "/api/auth/login",
            data={"username": "nonexistent@test.com", "password": "wrong"},
        )
        
        assert response.status_code == 401
        assert "Credenciales incorrectas" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_and_login(
        self, client: AsyncClient, test_session: AsyncSession
    ):
        """Test: Registrar usuario y hacer login."""
        # Registrar
        register_response = await client.post(
            "/api/auth/register",
            params={
                "email": "test@example.com",
                "password": "secure_password_123",
                "full_name": "Test User",
                "role": "operator",
                "allowed_modules": ["stock", "billing"],
            },
        )
        
        assert register_response.status_code == 200
        user_data = register_response.json()
        assert user_data["email"] == "test@example.com"
        assert user_data["full_name"] == "Test User"
        assert user_data["role"] == "operator"
        assert "stock" in user_data["allowed_modules"]
        assert "billing" in user_data["allowed_modules"]
        
        # Login
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "secure_password_123"},
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["user"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_session: AsyncSession
    ):
        """Test: No permite registrar email duplicado."""
        # Primer registro
        await client.post(
            "/api/auth/register",
            params={
                "email": "duplicate@test.com",
                "password": "password123",
            },
        )
        
        # Segundo registro con mismo email
        response = await client.post(
            "/api/auth/register",
            params={
                "email": "duplicate@test.com",
                "password": "password456",
            },
        )
        
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, client: AsyncClient, test_session: AsyncSession
    ):
        """Test: Login falla con contraseña incorrecta."""
        # Registrar
        await client.post(
            "/api/auth/register",
            params={
                "email": "user@test.com",
                "password": "correct_password",
            },
        )
        
        # Login con contraseña incorrecta
        response = await client.post(
            "/api/auth/login",
            data={"username": "user@test.com", "password": "wrong_password"},
        )
        
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests para endpoints protegidos con JWT."""
    
    @pytest.mark.asyncio
    async def test_inventory_without_token(self, client: AsyncClient):
        """Test: Acceso a inventario sin token retorna 401."""
        response = await client.get("/api/inventory/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_inventory_with_invalid_token(self, client: AsyncClient):
        """Test: Acceso con token inválido retorna 401."""
        response = await client.get(
            "/api/inventory/",
            headers={"Authorization": "Bearer invalid_token"},
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_inventory_with_valid_token(
        self, client: AsyncClient, test_session: AsyncSession
    ):
        """Test: Acceso con token válido funciona."""
        # Registrar y login
        await client.post(
            "/api/auth/register",
            params={"email": "inventory@test.com", "password": "password123"},
        )
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "inventory@test.com", "password": "password123"},
        )
        token = login_response.json()["access_token"]
        
        # Acceder a inventario
        response = await client.get(
            "/api/inventory/",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_products" in data
