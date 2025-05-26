"""
API client utility for Vanta Ledger Enhanced.

This module provides a client for communicating with the backend API.
"""
import requests
import json
import os
from datetime import datetime

class ApiClient:
    """
    Client for interacting with the Vanta Ledger backend API.
    
    Features:
    - RESTful API communication
    - Error handling and retry logic
    - Offline operation support with local caching
    - Authentication management
    """
    
    def __init__(self, base_url="http://localhost:8500/api"):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL for the API.
        """
        self.base_url = base_url
        self.token = None
        self.user_info = None
        self.offline_mode = False
        self.offline_queue = []
    
    def login(self, username, password):
        """
        Authenticate with the API.
        
        Args:
            username (str): User's username.
            password (str): User's password.
            
        Returns:
            bool: True if login successful, False otherwise.
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_info = data.get("user")
                return True
            return False
        except requests.RequestException:
            self.offline_mode = True
            return False
    
    def get_transactions(self, owner_id=None, skip=0, limit=100):
        """
        Get transactions from the API.
        
        Args:
            owner_id (int, optional): Filter by owner ID.
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to return.
            
        Returns:
            list: List of transaction objects.
        """
        if self.offline_mode:
            # Return cached transactions in offline mode
            return self._get_cached_transactions(owner_id)
        
        try:
            params = {"skip": skip, "limit": limit}
            if owner_id:
                params["owner_id"] = owner_id
                
            headers = self._get_auth_headers()
            
            response = requests.get(
                f"{self.base_url}/transactions",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                transactions = response.json()
                self._cache_transactions(transactions)
                return transactions
            return []
        except requests.RequestException:
            self.offline_mode = True
            return self._get_cached_transactions(owner_id)
    
    def get_transaction(self, transaction_id):
        """
        Get a specific transaction by ID.
        
        Args:
            transaction_id (int): ID of the transaction to retrieve.
            
        Returns:
            dict: Transaction object or None if not found.
        """
        if self.offline_mode:
            # Return cached transaction in offline mode
            return self._get_cached_transaction(transaction_id)
        
        try:
            headers = self._get_auth_headers()
            
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            self.offline_mode = True
            return self._get_cached_transaction(transaction_id)
    
    def create_transaction(self, transaction_data):
        """
        Create a new transaction.
        
        Args:
            transaction_data (dict): Transaction data.
            
        Returns:
            dict: Created transaction or None if failed.
        """
        if self.offline_mode:
            # Queue for later sync in offline mode
            self.offline_queue.append({
                "action": "create",
                "data": transaction_data,
                "timestamp": datetime.now().isoformat()
            })
            return transaction_data
        
        try:
            headers = self._get_auth_headers()
            
            response = requests.post(
                f"{self.base_url}/transactions",
                json=transaction_data,
                headers=headers
            )
            
            if response.status_code in (200, 201):
                return response.json()
            return None
        except requests.RequestException:
            self.offline_mode = True
            self.offline_queue.append({
                "action": "create",
                "data": transaction_data,
                "timestamp": datetime.now().isoformat()
            })
            return transaction_data
    
    def update_transaction(self, transaction_id, transaction_data):
        """
        Update an existing transaction.
        
        Args:
            transaction_id (int): ID of the transaction to update.
            transaction_data (dict): Updated transaction data.
            
        Returns:
            dict: Updated transaction or None if failed.
        """
        if self.offline_mode:
            # Queue for later sync in offline mode
            self.offline_queue.append({
                "action": "update",
                "id": transaction_id,
                "data": transaction_data,
                "timestamp": datetime.now().isoformat()
            })
            return transaction_data
        
        try:
            headers = self._get_auth_headers()
            
            response = requests.put(
                f"{self.base_url}/transactions/{transaction_id}",
                json=transaction_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            self.offline_mode = True
            self.offline_queue.append({
                "action": "update",
                "id": transaction_id,
                "data": transaction_data,
                "timestamp": datetime.now().isoformat()
            })
            return transaction_data
    
    def delete_transaction(self, transaction_id):
        """
        Delete a transaction.
        
        Args:
            transaction_id (int): ID of the transaction to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if self.offline_mode:
            # Queue for later sync in offline mode
            self.offline_queue.append({
                "action": "delete",
                "id": transaction_id,
                "timestamp": datetime.now().isoformat()
            })
            return True
        
        try:
            headers = self._get_auth_headers()
            
            response = requests.delete(
                f"{self.base_url}/transactions/{transaction_id}",
                headers=headers
            )
            
            return response.status_code in (200, 204)
        except requests.RequestException:
            self.offline_mode = True
            self.offline_queue.append({
                "action": "delete",
                "id": transaction_id,
                "timestamp": datetime.now().isoformat()
            })
            return True
    
    def get_owners(self):
        """
        Get list of company owners.
        
        Returns:
            list: List of owner objects.
        """
        if self.offline_mode:
            # Return cached owners in offline mode
            return self._get_cached_owners()
        
        try:
            headers = self._get_auth_headers()
            
            response = requests.get(
                f"{self.base_url}/owners",
                headers=headers
            )
            
            if response.status_code == 200:
                owners = response.json()
                self._cache_owners(owners)
                return owners
            return []
        except requests.RequestException:
            self.offline_mode = True
            return self._get_cached_owners()
    
    def sync_offline_changes(self):
        """
        Synchronize offline changes with the server.
        
        Returns:
            bool: True if sync successful, False otherwise.
        """
        if not self.offline_mode or not self.offline_queue:
            return True
        
        try:
            # Test connection
            response = requests.get(f"{self.base_url}/health")
            if response.status_code != 200:
                return False
            
            self.offline_mode = False
            
            # Process offline queue
            success = True
            for item in list(self.offline_queue):
                if item["action"] == "create":
                    result = self.create_transaction(item["data"])
                    if result:
                        self.offline_queue.remove(item)
                    else:
                        success = False
                
                elif item["action"] == "update":
                    result = self.update_transaction(item["id"], item["data"])
                    if result:
                        self.offline_queue.remove(item)
                    else:
                        success = False
                
                elif item["action"] == "delete":
                    result = self.delete_transaction(item["id"])
                    if result:
                        self.offline_queue.remove(item)
                    else:
                        success = False
            
            return success
        except requests.RequestException:
            self.offline_mode = True
            return False
    
    def _get_auth_headers(self):
        """Get authentication headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _cache_transactions(self, transactions):
        """Cache transactions for offline use."""
        cache_dir = self._ensure_cache_dir()
        with open(os.path.join(cache_dir, "transactions.json"), "w") as f:
            json.dump(transactions, f)
    
    def _get_cached_transactions(self, owner_id=None):
        """Get cached transactions."""
        cache_dir = self._ensure_cache_dir()
        cache_file = os.path.join(cache_dir, "transactions.json")
        
        if not os.path.exists(cache_file):
            return []
        
        try:
            with open(cache_file, "r") as f:
                transactions = json.load(f)
            
            if owner_id:
                return [t for t in transactions if t.get("owner_id") == owner_id]
            return transactions
        except (json.JSONDecodeError, IOError):
            return []
    
    def _get_cached_transaction(self, transaction_id):
        """Get a cached transaction by ID."""
        transactions = self._get_cached_transactions()
        for transaction in transactions:
            if transaction.get("id") == transaction_id:
                return transaction
        return None
    
    def _cache_owners(self, owners):
        """Cache owners for offline use."""
        cache_dir = self._ensure_cache_dir()
        with open(os.path.join(cache_dir, "owners.json"), "w") as f:
            json.dump(owners, f)
    
    def _get_cached_owners(self):
        """Get cached owners."""
        cache_dir = self._ensure_cache_dir()
        cache_file = os.path.join(cache_dir, "owners.json")
        
        if not os.path.exists(cache_file):
            return []
        
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _ensure_cache_dir(self):
        """Ensure the cache directory exists."""
        cache_dir = os.path.join(os.path.expanduser("~"), ".vanta_ledger_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
