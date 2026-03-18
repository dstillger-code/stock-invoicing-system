"""Aplicación FastAPI: Stock y Facturación Multiplataforma."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, create_all_tables
from app.core.base import Base
from app.routers import auth, stock, invoicing, negocio
from app.db.seed_tax_config import seed_tax_config

# Importar modelos para que Base.metadata tenga todas las tablas
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización: esquemas, tablas y seed de impuestos (Chile/Argentina)."""
    await init_db()
    await create_all_tables(Base)
    await seed_tax_config()
    yield
    # shutdown si hiciera falta (ej. cerrar pool)


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

# Routers por módulo (Auth, Stock, Facturación)
app.include_router(auth.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(invoicing.router, prefix="/api")
app.include_router(negocio.router, prefix="/api")


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "docs": "/docs"}
