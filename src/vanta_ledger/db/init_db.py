import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from vanta_ledger.core.config import settings
from vanta_ledger.models.transaction import Transaction  # Import all models here

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_models():
    async with engine.begin() as conn:
        # Import Base from models or base_class
        from vanta_ledger.db.base_class import Base
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
