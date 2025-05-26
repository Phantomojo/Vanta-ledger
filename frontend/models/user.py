"""
User model for Vanta Ledger Enhanced.

This module defines the data model for application users with role-based access control.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import uuid
import hashlib

@dataclass
class User:
    """
    Data model for an application user.
    
    Attributes:
        id: Unique identifier for the user
        username: Username for login
        password_hash: Hashed password
        name: Full name of the user
        email: Email address of the user
        role: User role (bookkeeper, owner, admin)
        owner_id: ID of the owner record if user is an owner
        active: Whether the user account is active
        last_login: When the user last logged in
        created_at: When the user record was created
        updated_at: When the user record was last updated
        permissions: Set of permission strings
        preferences: User preferences
        metadata: Additional user information
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    password_hash: str = ""
    name: str = ""
    email: str = ""
    role: str = "bookkeeper"  # bookkeeper, owner, admin
    owner_id: str = ""
    active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    permissions: Set[str] = field(default_factory=set)
    preferences: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for API and storage."""
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "owner_id": self.owner_id,
            "active": self.active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "permissions": list(self.permissions),
            "preferences": self.preferences,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary data."""
        # Handle datetime strings
        last_login = data.get("last_login")
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        # Handle permissions
        permissions = data.get("permissions", [])
        if isinstance(permissions, list):
            permissions = set(permissions)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            role=data.get("role", "bookkeeper"),
            owner_id=data.get("owner_id", ""),
            active=data.get("active", True),
            last_login=last_login,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            permissions=permissions,
            preferences=data.get("preferences", {}),
            metadata=data.get("metadata", {})
        )
    
    def set_password(self, password: str) -> None:
        """Set the user's password (hashed)."""
        self.password_hash = self._hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return self.password_hash == self._hash_password(password)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password for storage."""
        # In a real implementation, use a proper password hashing library
        # This is a simple example using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()
    
    def has_permission(self, permission: str) -> bool:
        """Check if the user has a specific permission."""
        # Admin role has all permissions
        if self.role == "admin":
            return True
        
        return permission in self.permissions
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now()


@dataclass
class UserManager:
    """
    Manager for application users.
    
    Features:
    - Add, update, and remove users
    - Get user by ID or username
    - List users with filtering
    - Authentication and permission management
    """
    
    users: List[User] = field(default_factory=list)
    
    def add_user(self, user: User) -> User:
        """Add a new user."""
        # Ensure ID is unique
        existing_ids = [u.id for u in self.users]
        if user.id in existing_ids:
            user.id = str(uuid.uuid4())
        
        # Ensure username is unique
        existing_usernames = [u.username.lower() for u in self.users]
        if user.username.lower() in existing_usernames:
            raise ValueError(f"Username '{user.username}' already exists")
        
        # Set default permissions based on role
        self._set_default_permissions(user)
        
        self.users.append(user)
        return user
    
    def update_user(self, user_id: str, data: Dict) -> Optional[User]:
        """Update an existing user."""
        for i, user in enumerate(self.users):
            if user.id == user_id:
                # Check if username is being changed and ensure it's unique
                if "username" in data and data["username"] != user.username:
                    existing_usernames = [u.username.lower() for u in self.users if u.id != user_id]
                    if data["username"].lower() in existing_usernames:
                        raise ValueError(f"Username '{data['username']}' already exists")
                
                # Update fields
                for key, value in data.items():
                    if key == "password":
                        user.set_password(value)
                    elif hasattr(user, key):
                        setattr(user, key, value)
                
                # Update timestamp
                user.updated_at = datetime.now()
                
                # Update permissions if role changed
                if "role" in data:
                    self._set_default_permissions(user)
                
                # Replace in list
                self.users[i] = user
                return user
        
        return None
    
    def remove_user(self, user_id: str) -> bool:
        """Remove a user by ID."""
        for i, user in enumerate(self.users):
            if user.id == user_id:
                del self.users[i]
                return True
        
        return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        for user in self.users:
            if user.username.lower() == username.lower():
                return user
        
        return None
    
    def list_users(
        self,
        role: Optional[str] = None,
        active_only: bool = False
    ) -> List[User]:
        """
        List users with filtering options.
        
        Args:
            role: Filter by user role
            active_only: Only include active users
            
        Returns:
            List of filtered users
        """
        filtered = self.users
        
        # Apply filters
        if role:
            filtered = [u for u in filtered if u.role == role]
        
        if active_only:
            filtered = [u for u in filtered if u.active]
        
        return filtered
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.get_user_by_username(username)
        
        if user and user.active and user.verify_password(password):
            user.update_last_login()
            return user
        
        return None
    
    def _set_default_permissions(self, user: User) -> None:
        """Set default permissions based on user role."""
        # Clear existing permissions
        user.permissions.clear()
        
        # Set permissions based on role
        if user.role == "admin":
            # Admin has all permissions
            user.permissions.update([
                "user:create", "user:read", "user:update", "user:delete",
                "owner:create", "owner:read", "owner:update", "owner:delete",
                "transaction:create", "transaction:read", "transaction:update", "transaction:delete",
                "report:generate", "settings:update"
            ])
        elif user.role == "bookkeeper":
            # Bookkeeper can manage transactions and view owners
            user.permissions.update([
                "owner:read",
                "transaction:create", "transaction:read", "transaction:update", "transaction:delete",
                "report:generate"
            ])
        elif user.role == "owner":
            # Owner can view their own transactions
            user.permissions.update([
                "transaction:read"
            ])
            
            # If this user is linked to an owner record
            if user.owner_id:
                user.permissions.add(f"owner:{user.owner_id}:read")
                user.permissions.add(f"transaction:{user.owner_id}:read")
