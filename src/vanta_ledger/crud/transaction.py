from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from vanta_ledger.models.transaction import Transaction

# Function to create a new transaction
async def create_transaction(db: AsyncSession, amount: float, type: str, description: str, date=None):
    db_transaction = Transaction(amount=amount, type=type, description=description)
    if date:
        db_transaction.date = date
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction

# Function to get a transaction by ID
async def get_transaction(db: AsyncSession, transaction_id: int):
    result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
    return result.scalars().first()

# Function to get all transactions
async def get_transactions(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Transaction).offset(skip).limit(limit))
    return result.scalars().all()
