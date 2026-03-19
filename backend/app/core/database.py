"""Conexión a PostgreSQL y sesiones por esquema."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from .config import settings

_engine = None
_async_session_local = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
        )
    return _engine


def _get_session_maker():
    global _async_session_local
    if _async_session_local is None:
        _async_session_local = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_local


class AsyncSessionLocal:
    """Wrapper lazy - guarda referencia al maker y lo usa en __call__ y __aenter__."""

    def __init__(self):
        self._maker = None

    def __call__(self):
        if self._maker is None:
            self._maker = _get_session_maker()
        return self._maker()

    async def __aenter__(self):
        if self._maker is None:
            self._maker = _get_session_maker()
        self._session = self._maker()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "_session"):
            await self._session.close()
        return False


async def get_db():
    maker = _get_session_maker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Crea los esquemas si no existen (auth, stock, invoicing, business)."""
    eng = _get_engine()
    async with eng.begin() as conn:
        for schema in ("auth", "stock", "invoicing", "business"):
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))


async def create_all_tables(base):
    """Crea todas las tablas definidas en los modelos (tras importar app.models)."""
    eng = _get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
