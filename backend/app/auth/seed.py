"""Seed: países y configuración de impuestos (Chile 19%, Argentina 21%)."""
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.billing.model import Country


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


if __name__ == "__main__":
    from app.core.database import init_db, create_all_tables
    from app.core.base import Base

    async def _main():
        await init_db()
        await create_all_tables(Base)
        await seed_tax_config()

    asyncio.run(_main())
