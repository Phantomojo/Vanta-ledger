#!/usr/bin/env python3
"""
Security Logging Configuration for Vanta Ledger

This module provides security-focused logging functionality.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .security_config import SECURITY_LOGGING

class SecurityLogger:
    """Security-focused logger with structured logging."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up security logger with file rotation."""
        self.logger.setLevel(getattr(logging, SECURITY_LOGGING["log_level"]))
        
        # Create logs directory
        log_file = Path(SECURITY_LOGGING["log_file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when=SECURITY_LOGGING["log_rotation"],
            backupCount=SECURITY_LOGGING["log_retention"],
            encoding='utf-8'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "WARNING"):
        """Log a security event with structured data."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        message = f"SECURITY_EVENT: {event_type} - {details}"
        
        if severity == "CRITICAL":
            self.logger.critical(message, extra=log_data)
        elif severity == "ERROR":
            self.logger.error(message, extra=log_data)
        elif severity == "WARNING":
            self.logger.warning(message, extra=log_data)
        else:
            self.logger.info(message, extra=log_data)
    
    def log_attack_attempt(self, ip_address: str, attack_type: str, details: Dict[str, Any]):
        """Log an attack attempt."""
        self.log_security_event(
            "ATTACK_ATTEMPT",
            {
                "ip_address": ip_address,
                "attack_type": attack_type,
                **details
            },
            "CRITICAL"
        )
    
    def log_suspicious_activity(self, ip_address: str, activity: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        self.log_security_event(
            "SUSPICIOUS_ACTIVITY",
            {
                "ip_address": ip_address,
                "activity": activity,
                **details
            },
            "WARNING"
        )
    
    def log_authentication_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log authentication-related events."""
        self.log_security_event(
            f"AUTH_{event_type}",
            {
                "user_id": user_id,
                **details
            },
            "INFO"
        )
    
    def log_authorization_event(self, event_type: str, user_id: str, resource: str, details: Dict[str, Any]):
        """Log authorization-related events."""
        self.log_security_event(
            f"AUTHZ_{event_type}",
            {
                "user_id": user_id,
                "resource": resource,
                **details
            },
            "INFO"
        )

# Global security logger instance
security_logger = SecurityLogger()
