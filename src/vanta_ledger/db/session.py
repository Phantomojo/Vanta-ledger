from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from vanta_ledger.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    """
    Provide an async database session
    """
    async with AsyncSessionLocal() as session:
        yield session

