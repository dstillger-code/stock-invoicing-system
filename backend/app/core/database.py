"""Conexión a PostgreSQL y sesiones por esquema."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from .config import settings

# Motor async para toda la app (una sola URL)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Sesión por defecto (para esquema public o el que use el modelo)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """Dependency: sesión async para inyectar en rutas."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Crea los esquemas si no existen (auth, stock, invoicing)."""
    async with engine.begin() as conn:
        for schema in ("auth", "stock", "invoicing"):
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))


async def create_all_tables(base):
    """Crea todas las tablas definidas en los modelos (tras importar app.models)."""
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
