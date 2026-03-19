"""Aplicación FastAPI: Stock y Facturación Multiplataforma."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.core.database import init_db, create_all_tables
from app.core.base import Base
from app.auth.router import router as auth_router
from app.stock.router import router as stock_router
from app.stock.inventory import router as inventory_router
from app.billing.router import router as billing_router
from app.billing.products_router import router as products_router
from app.billing.billing_router import router as invoice_router
from app.auth.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización: esquemas, tablas, países y usuario admin."""
    await init_db()
    await create_all_tables(Base)
    await seed_all()
    yield


app = FastAPI(
    title="Stock & Billing API",
    description="""
## Sistema de Stock y Facturación Multiplataforma

API REST para gestión de inventario y facturación con soporte para múltiples países.

### Características
- **Autenticación JWT** con roles y permisos por módulo
- **Inventario** con productos, precios y cantidades
- **Facturación** con cálculo de impuestos por país (CL, AR)
- **Multi-schema PostgreSQL** para separación de dominios

### Esquemas de Base de Datos
- `auth`: Usuarios con roles y módulos permitidos
- `business`: Productos, precios por país, inventario
- `stock`: Items de stock legacy
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api", tags=["Autenticación"])
app.include_router(stock_router, prefix="/api", tags=["Stock"])
app.include_router(inventory_router, prefix="/api", tags=["Inventario"])
app.include_router(billing_router, prefix="/api", tags=["Facturación"])
app.include_router(products_router, prefix="/api", tags=["Productos"])
app.include_router(invoice_router, prefix="/api", tags=["Facturación"])


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


def custom_openapi():
    """Personaliza el esquema OpenAPI."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["contact"] = {
        "name": "Soporte",
        "email": "soporte@ejemplo.com",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
