"""
Owner model for Vanta Ledger Enhanced.

This module defines the data model for company owners.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class Owner:
    """
    Data model for a company owner.
    
    Attributes:
        id: Unique identifier for the owner
        name: Full name of the owner
        email: Email address of the owner
        phone: Phone number of the owner
        ownership_percentage: Percentage of company ownership
        active: Whether the owner is active
        created_at: When the owner record was created
        updated_at: When the owner record was last updated
        metadata: Additional owner information
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: str = ""
    ownership_percentage: float = 0.0
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert owner to dictionary for API and storage."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "ownership_percentage": self.ownership_percentage,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Owner':
        """Create owner from dictionary data."""
        # Handle datetime strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            ownership_percentage=data.get("ownership_percentage", 0.0),
            active=data.get("active", True),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            metadata=data.get("metadata", {})
        )


@dataclass
class OwnerManager:
    """
    Manager for company owners.
    
    Features:
    - Add, update, and remove owners
    - Get owner by ID
    - List all owners
    - Calculate ownership distribution
    """
    
    owners: List[Owner] = field(default_factory=list)
    
    def add_owner(self, owner: Owner) -> Owner:
        """Add a new owner."""
        # Ensure ID is unique
        existing_ids = [o.id for o in self.owners]
        if owner.id in existing_ids:
            owner.id = str(uuid.uuid4())
        
        self.owners.append(owner)
        return owner
    
    def update_owner(self, owner_id: str, data: Dict) -> Optional[Owner]:
        """Update an existing owner."""
        for i, owner in enumerate(self.owners):
            if owner.id == owner_id:
                # Update fields
                for key, value in data.items():
                    if hasattr(owner, key):
                        setattr(owner, key, value)
                
                # Update timestamp
                owner.updated_at = datetime.now()
                
                # Replace in list
                self.owners[i] = owner
                return owner
        
        return None
    
    def remove_owner(self, owner_id: str) -> bool:
        """Remove an owner by ID."""
        for i, owner in enumerate(self.owners):
            if owner.id == owner_id:
                del self.owners[i]
                return True
        
        return False
    
    def get_owner(self, owner_id: str) -> Optional[Owner]:
        """Get an owner by ID."""
        for owner in self.owners:
            if owner.id == owner_id:
                return owner
        
        return None
    
    def list_owners(self, active_only: bool = False) -> List[Owner]:
        """List all owners, optionally filtering for active only."""
        if active_only:
            return [owner for owner in self.owners if owner.active]
        return self.owners
    
    def get_ownership_distribution(self) -> Dict[str, float]:
        """Get the distribution of ownership percentages."""
        distribution = {}
        for owner in self.owners:
            if owner.active:
                distribution[owner.id] = owner.ownership_percentage
        
        return distribution
    
    def validate_ownership_percentages(self) -> bool:
        """Validate that ownership percentages sum to 100%."""
        total = sum(owner.ownership_percentage for owner in self.owners if owner.active)
        return abs(total - 100.0) < 0.01  # Allow for small floating point errors
