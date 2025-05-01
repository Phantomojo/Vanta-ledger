from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from vanta_ledger.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Provide a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

