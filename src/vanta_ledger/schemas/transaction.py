from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Expenditure(Base):
    __tablename__ = "expenditures"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    amount = Column(Float)
    description = Column(String)

# Create the engine (use SQLite for simplicity)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables in the database
Base.metadata.create_all(bind=engine)
