from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from vanta_ledger.db.base_class import Base  # Corrected import

class Expenditure(Base):
    __tablename__ = "expenditures"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'sale' or 'expense'
    description = Column(String)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
