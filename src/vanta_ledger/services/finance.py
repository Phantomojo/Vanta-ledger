from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from vanta_ledger.models.transaction import Transaction
from datetime import datetime
from collections import defaultdict

async def calculate_totals(db: AsyncSession) -> dict:
    """
    Calculate total sales and expenses, including daily, monthly, quarterly, and yearly aggregates.

    Args:
        db (AsyncSession): Database session.

    Returns:
        dict: A dictionary with total sales, total expenses, and aggregates.
    """
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()

    total_sales = 0.0
    total_expenses = 0.0

    daily_sales = defaultdict(float)
    daily_expenses = defaultdict(float)
    monthly_sales = defaultdict(float)
    monthly_expenses = defaultdict(float)
    quarterly_sales = defaultdict(float)
    quarterly_expenses = defaultdict(float)
    yearly_sales = defaultdict(float)
    yearly_expenses = defaultdict(float)

    for tx in transactions:
        date = tx.date
        year = date.year
        month = date.month
        day = date.day
        quarter = (month - 1) // 3 + 1

        if tx.type == "sale":
            total_sales += tx.amount
            daily_sales[date.date()] += tx.amount
            monthly_sales[(year, month)] += tx.amount
            quarterly_sales[(year, quarter)] += tx.amount
            yearly_sales[year] += tx.amount
        elif tx.type == "expenditure":
            total_expenses += tx.amount
            daily_expenses[date.date()] += tx.amount
            monthly_expenses[(year, month)] += tx.amount
            quarterly_expenses[(year, quarter)] += tx.amount
            yearly_expenses[year] += tx.amount

    profit_loss = total_sales - total_expenses

    return {
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "profit_loss": profit_loss,
        "daily_sales": dict(daily_sales),
        "daily_expenses": dict(daily_expenses),
        "monthly_sales": dict(monthly_sales),
        "monthly_expenses": dict(monthly_expenses),
        "quarterly_sales": dict(quarterly_sales),
        "quarterly_expenses": dict(quarterly_expenses),
        "yearly_sales": dict(yearly_sales),
        "yearly_expenses": dict(yearly_expenses),
    }
