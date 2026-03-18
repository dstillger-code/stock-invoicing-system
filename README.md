# Stock & Billing Multiplatform System

Sistema de gestión de inventario y facturación con soporte para múltiples países (Chile y Argentina).

## Índice

- [Descripción](#descripción)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Documentación API](#documentación-api)
- [Modelos de Base de Datos](#modelos-de-base-de-datos)
- [Autenticación](#autenticación)
- [Cálculo de Impuestos](#cálculo-de-impuestos)
- [Tests](#tests)
- [Desarrollo](#desarrollo)

---

## Descripción

Sistema multiplataforma para la gestión de stock y facturación que soporta:
- Múltiples países con diferentes regímenes de IVA
- Control de inventario por producto y región
- Autenticación JWT con roles y permisos
- Cálculo de precios con impuestos variables

---

## Tecnologías

### Backend
| Tecnología | Propósito |
|------------|-----------|
| FastAPI | Framework web async |
| SQLAlchemy 2.0 | ORM con soporte async |
| PostgreSQL 15+ | Base de datos |
| python-jose | Tokens JWT |
| passlib + bcrypt | Hash de contraseñas |
| Pydantic | Validación de datos |

### Frontend
| Tecnología | Propósito |
|------------|-----------|
| React 18 | Librería UI |
| Vite | Bundler/Dev server |
| TypeScript | Tipado estático |
| Tailwind CSS | Estilos |
| Zustand | Estado global |
| React Router | Navegación |

---

## Estructura del Proyecto

```
stock-invoicing-system/
├── backend/
│   ├── app/
│   │   ├── auth/           # Login, JWT, permisos
│   │   │   ├── model.py    # User SQLAlchemy model
│   │   │   ├── router.py   # Auth endpoints
│   │   │   └── seed.py     # Seed de países
│   │   ├── stock/          # Módulo de inventario
│   │   │   ├── model.py    # StockItem model
│   │   │   ├── router.py   # Stock CRUD endpoints
│   │   │   ├── schema.py   # Pydantic schemas
│   │   │   └── inventory.py # Protected inventory endpoints
│   │   ├── billing/        # Módulo de facturación
│   │   │   ├── model.py    # Country, Product, ProductPrice, Inventory
│   │   │   ├── router.py   # Billing endpoints
│   │   │   ├── schema.py   # Billing schemas
│   │   │   └── taxes.py    # Cálculo de impuestos
│   │   └── core/           # Configuración global
│   │       ├── config.py   # Settings (Pydantic)
│   │       ├── database.py # Async SQLAlchemy
│   │       └── base.py     # Base model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes reutilizables
│   │   │   ├── ui/         # PrivateRoute
│   │   │   └── Sidebar.tsx
│   │   ├── modules/        # Módulos de la app
│   │   │   ├── Auth/       # Login
│   │   │   ├── Stock/      # Inventario
│   │   │   └── Billing/    # Facturación
│   │   ├── store/          # Zustand stores
│   │   │   ├── useAuthStore.ts
│   │   │   └── useConfigStore.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Requisitos

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 15+ (o Docker)
- **npm** o **pnpm**

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/dstillger-code/stock-invoicing-system.git
cd stock-invoicing-system
```

### 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario (valores por defecto funcionan)
```

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Base de datos con Docker

```bash
# En la raíz del proyecto
docker compose up -d
```

---

## Ejecución

### Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

---

## Documentación API

FastAPI provee documentación interactiva:

| URL | Descripción |
|-----|-------------|
| `/docs` | Swagger UI (recomendado) |
| `/redoc` | ReDoc alternativa |
| `/openapi.json` | Esquema OpenAPI 3.0 |

### Endpoints Principales

#### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login con credenciales |
| POST | `/api/auth/register` | Registro de usuario |
| GET | `/api/auth/health` | Health check |

#### Stock

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/stock/items` | Listar items |
| POST | `/api/stock/items` | Crear item |
| GET | `/api/stock/items/{id}` | Obtener item |
| PATCH | `/api/stock/items/{id}` | Actualizar item |
| DELETE | `/api/stock/items/{id}` | Eliminar item |

#### Inventario (Protegido)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/inventory/` | Listar inventario (JWT) |
| GET | `/api/inventory/{id}` | Detalle producto (JWT) |
| POST | `/api/inventory/calculate` | Calcular precio con IVA (JWT) |

#### Facturación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/billing/tax/health` | Health check |
| GET | `/api/billing/countries` | Listar países |

---

## Modelos de Base de Datos

### Esquema `auth`

```sql
CREATE TABLE auth.users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'operator',  -- admin, operator, accountant
    is_active BOOLEAN DEFAULT true,
    allowed_modules TEXT[] DEFAULT '{stock}',  -- stock, billing
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Esquema `business`

```sql
-- Países con configuración fiscal
CREATE TABLE business.countries (
    code VARCHAR(2) PRIMARY KEY,  -- CL, AR
    name TEXT NOT NULL,
    currency_code VARCHAR(3),
    default_tax_rate DECIMAL(5,2)  -- 19.00 (CL), 21.00 (AR)
);

-- Catálogo de productos
CREATE TABLE business.products (
    id UUID PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Precios por país
CREATE TABLE business.product_prices (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    country_code VARCHAR(2) REFERENCES countries(code),
    net_price DECIMAL(12,2) NOT NULL,
    tax_rate DECIMAL(5,2) NOT NULL,
    is_exempt BOOLEAN DEFAULT false
);

-- Inventario
CREATE TABLE business.inventory (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id) UNIQUE,
    quantity INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT now()
);
```

---

## Autenticación

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@test.com&password=secret123"
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@test.com",
    "full_name": "Admin",
    "role": "admin",
    "allowed_modules": ["stock", "billing"]
  }
}
```

### Uso del Token

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/inventory/"
```

---

## Cálculo de Impuestos

### Tasas por País

| País | IVA Default | IVA Reducido | IVA Adicional |
|------|-------------|--------------|---------------|
| Chile (CL) | 19% | - | - |
| Argentina (AR) | 21% | 10.5% | 27% |

### Ejemplo de Cálculo

```python
from app.billing.taxes import calculate_total

# Chile - 19% IVA
result = calculate_total(100.00, "CL")
# {'net_price': 100.00, 'tax_rate': 19.0, 'tax_amount': 19.00, 'total': 119.00}

# Argentina - 21% IVA
result = calculate_total(100.00, "AR")
# {'net_price': 100.00, 'tax_rate': 21.0, 'tax_amount': 21.00, 'total': 121.00}

# Argentina - IVA reducido 10.5%
result = calculate_total(100.00, "AR", tax_type="reduced")
# {'net_price': 100.00, 'tax_rate': 10.5, 'tax_amount': 10.50, 'total': 110.50}
```

---

## Tests

### Backend

```bash
cd backend

# Instalar dependencias de test
pip install pytest pytest-asyncio httpx pytest-cov

# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend

```bash
cd frontend

# Instalar Vitest (ya incluido en devDependencies)
npm run test

# Modo watch
npm run test:watch
```

---

## Desarrollo

### Ramas

- `main`: Rama de producción (stable)
- `develop`: Rama de desarrollo activo

### Flujo de trabajo

1. Crear rama desde `develop`: `git checkout -b feature/nueva-funcion`
2. Implementar cambios
3. Commit: `git commit -m "feat: descripción"`
4. Push: `git push`
5. Crear Pull Request hacia `develop`

### Registros de país

El sistema incluye seed de países al iniciar:

```python
# backend/app/auth/seed.py
Country(code="CL", name="Chile", currency_code="CLP", default_tax_rate=19.00)
Country(code="AR", name="Argentina", currency_code="ARS", default_tax_rate=21.00)
```

---

## Licencia

MIT License
