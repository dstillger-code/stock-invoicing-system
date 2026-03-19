"""Seed: países y configuración de impuestos (Chile 19%, Argentina 21%)."""
import asyncio
import os
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.billing.model import Country
from app.auth.model import User
from app.auth.router import get_password_hash

DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "CL")


async def seed_tax_config():
    """Inserta países con sus tasas de IVA por defecto. Idempotente."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Country).where(Country.code == "CL"))
        if result.scalar_one_or_none() is not None:
            print("Country CL ya existe, omitiendo seed.")
            return

        session.add(Country(code="CL", name="Chile", currency_code="CLP", default_tax_rate=19.00))
        session.add(Country(code="AR", name="Argentina", currency_code="ARS", default_tax_rate=21.00))
        await session.commit()
        print("Seed: países CL y AR creados.")


async def seed_admin_user():
    """Crea usuario admin si no existe en el país por defecto."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.email == "admin@stock.com", User.country_code == DEFAULT_COUNTRY
            )
        )
        if result.scalar_one_or_none() is not None:
            print(f"Usuario admin ya existe en {DEFAULT_COUNTRY}, omitiendo seed.")
            return

        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        hashed = get_password_hash(admin_password)

        admin = User(
            email="admin@stock.com",
            password_hash=hashed,
            full_name="Administrador",
            role="admin",
            allowed_modules=["stock", "billing"],
            country_code=DEFAULT_COUNTRY,
        )
        session.add(admin)
        await session.commit()
        print(f"Seed: usuario admin@stock.com creado en {DEFAULT_COUNTRY} (password: {admin_password})")


async def seed_all():
    """Ejecuta todos los seeds."""
    await seed_tax_config()
    await seed_admin_user()


if __name__ == "__main__":
    from app.core.database import init_db, create_all_tables
    from app.core.base import Base

    async def _main():
        await init_db()
        await create_all_tables(Base)
        await seed_all()

    asyncio.run(_main())
