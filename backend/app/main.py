"""Aplicación FastAPI: Stock y Facturación Multiplataforma."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, create_all_tables
from app.core.base import Base
from app.auth.router import router as auth_router
from app.stock.router import router as stock_router
from app.stock.inventory import router as inventory_router
from app.billing.router import router as billing_router
from app.auth.seed import seed_tax_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización: esquemas, tablas y seed de impuestos (Chile/Argentina)."""
    await init_db()
    await create_all_tables(Base)
    await seed_tax_config()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(stock_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(billing_router, prefix="/api")


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "docs": "/docs"}
