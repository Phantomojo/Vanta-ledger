"""
Transaction model for Vanta Ledger Enhanced.

This module defines the data model for financial transactions with owner attribution.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class Transaction:
    """
    Data model for a financial transaction.
    
    Attributes:
        id: Unique identifier for the transaction
        type: Transaction type (sale, expenditure, transfer, etc.)
        amount: Transaction amount
        description: Description of the transaction
        date: Date of the transaction
        owner_id: ID of the owner associated with this transaction
        category: Category of the transaction
        payment_method: Method of payment
        reference: Reference number or identifier
        attachments: List of attachment references
        created_by: ID of the user who created the transaction
        created_at: When the transaction record was created
        updated_at: When the transaction record was last updated
        metadata: Additional transaction information
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""  # sale, expenditure, transfer, etc.
    amount: float = 0.0
    description: str = ""
    date: datetime = field(default_factory=datetime.now)
    owner_id: str = ""
    category: str = ""
    payment_method: str = ""
    reference: str = ""
    attachments: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary for API and storage."""
        return {
            "id": self.id,
            "type": self.type,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat(),
            "owner_id": self.owner_id,
            "category": self.category,
            "payment_method": self.payment_method,
            "reference": self.reference,
            "attachments": self.attachments,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """Create transaction from dictionary data."""
        # Handle datetime strings
        date = data.get("date")
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=data.get("type", ""),
            amount=data.get("amount", 0.0),
            description=data.get("description", ""),
            date=date or datetime.now(),
            owner_id=data.get("owner_id", ""),
            category=data.get("category", ""),
            payment_method=data.get("payment_method", ""),
            reference=data.get("reference", ""),
            attachments=data.get("attachments", []),
            created_by=data.get("created_by", ""),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            metadata=data.get("metadata", {})
        )


@dataclass
class TransactionManager:
    """
    Manager for financial transactions.
    
    Features:
    - Add, update, and remove transactions
    - Get transaction by ID
    - List transactions with filtering
    - Calculate financial summaries
    """
    
    transactions: List[Transaction] = field(default_factory=list)
    
    def add_transaction(self, transaction: Transaction) -> Transaction:
        """Add a new transaction."""
        # Ensure ID is unique
        existing_ids = [t.id for t in self.transactions]
        if transaction.id in existing_ids:
            transaction.id = str(uuid.uuid4())
        
        self.transactions.append(transaction)
        return transaction
    
    def update_transaction(self, transaction_id: str, data: Dict) -> Optional[Transaction]:
        """Update an existing transaction."""
        for i, transaction in enumerate(self.transactions):
            if transaction.id == transaction_id:
                # Update fields
                for key, value in data.items():
                    if hasattr(transaction, key):
                        setattr(transaction, key, value)
                
                # Update timestamp
                transaction.updated_at = datetime.now()
                
                # Replace in list
                self.transactions[i] = transaction
                return transaction
        
        return None
    
    def remove_transaction(self, transaction_id: str) -> bool:
        """Remove a transaction by ID."""
        for i, transaction in enumerate(self.transactions):
            if transaction.id == transaction_id:
                del self.transactions[i]
                return True
        
        return False
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        for transaction in self.transactions:
            if transaction.id == transaction_id:
                return transaction
        
        return None
    
    def list_transactions(
        self,
        owner_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """
        List transactions with filtering options.
        
        Args:
            owner_id: Filter by owner ID
            transaction_type: Filter by transaction type
            start_date: Filter by minimum date
            end_date: Filter by maximum date
            category: Filter by category
            min_amount: Filter by minimum amount
            max_amount: Filter by maximum amount
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of filtered transactions
        """
        filtered = self.transactions
        
        # Apply filters
        if owner_id:
            filtered = [t for t in filtered if t.owner_id == owner_id]
        
        if transaction_type:
            filtered = [t for t in filtered if t.type == transaction_type]
        
        if start_date:
            filtered = [t for t in filtered if t.date >= start_date]
        
        if end_date:
            filtered = [t for t in filtered if t.date <= end_date]
        
        if category:
            filtered = [t for t in filtered if t.category == category]
        
        if min_amount is not None:
            filtered = [t for t in filtered if t.amount >= min_amount]
        
        if max_amount is not None:
            filtered = [t for t in filtered if t.amount <= max_amount]
        
        # Sort by date (newest first)
        filtered.sort(key=lambda t: t.date, reverse=True)
        
        # Apply pagination
        return filtered[offset:offset + limit]
    
    def get_total_income(self, owner_id: Optional[str] = None) -> float:
        """Calculate total income, optionally for a specific owner."""
        transactions = self.transactions
        if owner_id:
            transactions = [t for t in transactions if t.owner_id == owner_id]
        
        return sum(t.amount for t in transactions if t.type == 'sale')
    
    def get_total_expenses(self, owner_id: Optional[str] = None) -> float:
        """Calculate total expenses, optionally for a specific owner."""
        transactions = self.transactions
        if owner_id:
            transactions = [t for t in transactions if t.owner_id == owner_id]
        
        return sum(t.amount for t in transactions if t.type == 'expenditure')
    
    def get_balance(self, owner_id: Optional[str] = None) -> float:
        """Calculate balance (income - expenses), optionally for a specific owner."""
        return self.get_total_income(owner_id) - self.get_total_expenses(owner_id)
    
    def get_transactions_by_category(
        self,
        transaction_type: str,
        owner_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get transaction totals grouped by category.
        
        Args:
            transaction_type: Type of transactions to include
            owner_id: Optional owner ID to filter by
            
        Returns:
            Dictionary mapping categories to total amounts
        """
        transactions = self.transactions
        if owner_id:
            transactions = [t for t in transactions if t.owner_id == owner_id]
        
        transactions = [t for t in transactions if t.type == transaction_type]
        
        result = {}
        for transaction in transactions:
            category = transaction.category or "Uncategorized"
            if category not in result:
                result[category] = 0
            result[category] += transaction.amount
        
        return result
    
    def get_transactions_by_date(
        self,
        transaction_type: str,
        period: str = 'month',
        owner_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get transaction totals grouped by date period.
        
        Args:
            transaction_type: Type of transactions to include
            period: Grouping period ('day', 'week', 'month', 'year')
            owner_id: Optional owner ID to filter by
            
        Returns:
            Dictionary mapping date periods to total amounts
        """
        transactions = self.transactions
        if owner_id:
            transactions = [t for t in transactions if t.owner_id == owner_id]
        
        transactions = [t for t in transactions if t.type == transaction_type]
        
        result = {}
        for transaction in transactions:
            if period == 'day':
                key = transaction.date.strftime('%Y-%m-%d')
            elif period == 'week':
                key = f"{transaction.date.year}-W{transaction.date.isocalendar()[1]}"
            elif period == 'month':
                key = transaction.date.strftime('%Y-%m')
            else:  # year
                key = str(transaction.date.year)
            
            if key not in result:
                result[key] = 0
            result[key] += transaction.amount
        
        return result
