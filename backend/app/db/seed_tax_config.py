"""Seed: configuración de impuestos por defecto (Chile 19%, estructura Argentina)."""
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import TaxConfig


async def seed_tax_config():
    """Inserta configuración Chile (IVA 19%) y deja lista Argentina. Idempotente."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TaxConfig).where(TaxConfig.country_code == "CL"))
        if result.scalar_one_or_none() is not None:
            print("TaxConfig Chile ya existe, omitiendo seed.")
            return

        session.add(
            TaxConfig(
                country_code="CL",
                country_name="Chile",
                default_vat_rate=19.00,
                extra_rates_json=None,
                perception_enabled=False,
                perception_rates_json=None,
                is_active=True,
            )
        )
        # Argentina: estructura lista (múltiples alícuotas y percepciones)
        session.add(
            TaxConfig(
                country_code="AR",
                country_name="Argentina",
                default_vat_rate=21.00,
                extra_rates_json='{"10.5": 10.5, "27": 27}',
                perception_enabled=True,
                perception_rates_json='{}',
                is_active=True,
            )
        )
        await session.commit()
        print("Seed TaxConfig: Chile (19%) y Argentina creados.")


if __name__ == "__main__":
    from app.core.database import init_db, create_all_tables
    from app.core.base import Base
    from app import models  # noqa: F401

    async def _main():
        await init_db()
        await create_all_tables(Base)
        await seed_tax_config()

    asyncio.run(_main())
