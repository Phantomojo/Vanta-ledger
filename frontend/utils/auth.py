"""
Authentication and security module for Vanta Ledger Enhanced.

This module provides authentication, session management, and security features.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import uuid
import hashlib
import json
import os

from frontend.models.user import User

@dataclass
class Session:
    """
    User session data model.
    
    Attributes:
        id: Unique session identifier
        user_id: ID of the authenticated user
        created_at: When the session was created
        expires_at: When the session expires
        ip_address: IP address of the client
        user_agent: User agent of the client
        is_active: Whether the session is active
        data: Additional session data
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True
    data: Dict = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """Create session from dictionary data."""
        # Handle datetime strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        expires_at = data.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user_id=data.get("user_id", ""),
            created_at=created_at or datetime.now(),
            expires_at=expires_at or (datetime.now() + timedelta(hours=24)),
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
            is_active=data.get("is_active", True),
            data=data.get("data", {})
        )


class AuthManager:
    """
    Authentication and session management.
    
    Features:
    - User authentication
    - Session creation and validation
    - Password hashing and verification
    - Role-based access control
    """
    
    def __init__(self, session_dir: str = None):
        """
        Initialize the authentication manager.
        
        Args:
            session_dir: Directory to store session data
        """
        self.sessions: Dict[str, Session] = {}
        self.current_user: Optional[User] = None
        self.current_session: Optional[Session] = None
        
        # Set session directory
        if session_dir:
            self.session_dir = session_dir
        else:
            self.session_dir = os.path.join(os.path.expanduser("~"), ".vanta_ledger_sessions")
        
        # Ensure session directory exists
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Load existing sessions
        self._load_sessions()
    
    def authenticate(self, username: str, password: str, user_manager, 
                    ip_address: str = "", user_agent: str = "") -> Optional[str]:
        """
        Authenticate a user and create a session.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            user_manager: UserManager instance for user lookup
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Session ID if authentication successful, None otherwise
        """
        # Authenticate user
        user = user_manager.authenticate(username, password)
        if not user:
            return None
        
        # Create session
        session = Session(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store session
        self.sessions[session.id] = session
        self._save_session(session)
        
        # Set current user and session
        self.current_user = user
        self.current_session = session
        
        return session.id
    
    def validate_session(self, session_id: str, user_manager) -> bool:
        """
        Validate a session and load the associated user.
        
        Args:
            session_id: Session ID to validate
            user_manager: UserManager instance for user lookup
            
        Returns:
            True if session is valid, False otherwise
        """
        # Check if session exists
        if session_id not in self.sessions:
            # Try to load from storage
            session = self._load_session(session_id)
            if not session:
                return False
            self.sessions[session_id] = session
        
        session = self.sessions[session_id]
        
        # Check if session is active and not expired
        if not session.is_active or session.is_expired():
            return False
        
        # Get user
        user = user_manager.get_user(session.user_id)
        if not user or not user.active:
            return False
        
        # Set current user and session
        self.current_user = user
        self.current_session = session
        
        return True
    
    def logout(self, session_id: str = None) -> bool:
        """
        Invalidate a session.
        
        Args:
            session_id: Session ID to invalidate, or current session if None
            
        Returns:
            True if session was invalidated, False otherwise
        """
        # Use current session if none specified
        if not session_id and self.current_session:
            session_id = self.current_session.id
        
        # Check if session exists
        if session_id not in self.sessions:
            return False
        
        # Invalidate session
        session = self.sessions[session_id]
        session.is_active = False
        self._save_session(session)
        
        # Clear current user and session if this was the current session
        if self.current_session and self.current_session.id == session_id:
            self.current_user = None
            self.current_session = None
        
        return True
    
    def logout_all(self, user_id: str) -> int:
        """
        Invalidate all sessions for a user.
        
        Args:
            user_id: User ID to invalidate sessions for
            
        Returns:
            Number of sessions invalidated
        """
        count = 0
        for session_id, session in list(self.sessions.items()):
            if session.user_id == user_id and session.is_active:
                session.is_active = False
                self._save_session(session)
                count += 1
                
                # Clear current user and session if this was the current session
                if self.current_session and self.current_session.id == session_id:
                    self.current_user = None
                    self.current_session = None
        
        return count
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            
        Returns:
            List of active sessions for the user
        """
        return [
            session for session in self.sessions.values()
            if session.user_id == user_id and session.is_active and not session.is_expired()
        ]
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if the current user has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if the user has the permission, False otherwise
        """
        if not self.current_user:
            return False
        
        return self.current_user.has_permission(permission)
    
    def _save_session(self, session: Session) -> None:
        """Save a session to storage."""
        file_path = os.path.join(self.session_dir, f"{session.id}.json")
        with open(file_path, 'w') as f:
            json.dump(session.to_dict(), f)
    
    def _load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from storage."""
        file_path = os.path.join(self.session_dir, f"{session_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Session.from_dict(data)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _load_sessions(self) -> None:
        """Load all sessions from storage."""
        if not os.path.exists(self.session_dir):
            return
        
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json extension
                session = self._load_session(session_id)
                if session and session.is_active and not session.is_expired():
                    self.sessions[session_id] = session


class SecurityUtils:
    """
    Security utility functions.
    
    Features:
    - Password hashing and verification
    - Token generation and validation
    - Input sanitization
    """
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Dict[str, str]:
        """
        Hash a password with an optional salt.
        
        Args:
            password: Password to hash
            salt: Optional salt, generated if not provided
            
        Returns:
            Dictionary with hash and salt
        """
        if not salt:
            salt = uuid.uuid4().hex
        
        # In a real implementation, use a proper password hashing library
        # This is a simple example using SHA-256 with salt
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return {
            "hash": password_hash,
            "salt": salt
        }
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: Password to verify
            stored_hash: Stored password hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        # Hash the provided password with the same salt
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        # Compare hashes
        return password_hash == stored_hash
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate a random token.
        
        Args:
            length: Length of the token in bytes
            
        Returns:
            Random token string
        """
        return uuid.uuid4().hex[:length]
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_str: Input string to sanitize
            
        Returns:
            Sanitized string
        """
        # In a real implementation, use a proper HTML sanitization library
        # This is a simple example that removes potentially dangerous characters
        sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
        return sanitized
