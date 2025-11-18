"""
Shared database utilities for database scripts.
Provides common database connection functions to reduce code duplication.
"""

import os
import logging
from sqlalchemy import create_engine
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_database_credentials():
    """
    Get database credentials from environment variables.
    
    Returns:
        dict: Dictionary containing database credentials for PostgreSQL and MongoDB
    """
    # PostgreSQL credentials
    postgres_user = os.getenv('POSTGRES_USER', 'vanta_user')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_db = os.getenv('POSTGRES_DB', 'vanta_ledger')
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    
    # MongoDB credentials
    mongo_user = os.getenv('MONGO_ROOT_USERNAME', 'admin')
    mongo_password = os.getenv('MONGO_ROOT_PASSWORD')
    mongo_db = os.getenv('MONGO_DATABASE', 'vanta_ledger')
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    
    return {
        'postgres': {
            'user': postgres_user,
            'password': postgres_password,
            'database': postgres_db,
            'host': postgres_host,
            'uri': f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}"
        },
        'mongo': {
            'user': mongo_user,
            'password': mongo_password,
            'database': mongo_db,
            'host': mongo_host,
            'uri': f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:27017/{mongo_db}?authSource=admin"
        }
    }


def connect_databases():
    """
    Connect to both PostgreSQL and MongoDB databases.
    
    Returns:
        tuple: (postgres_engine, mongo_client, mongo_db)
        
    Raises:
        Exception: If database connection fails
    """
    try:
        credentials = get_database_credentials()
        
        # Connect to PostgreSQL
        postgres_engine = create_engine(credentials['postgres']['uri'])
        logger.info("✅ Connected to PostgreSQL")
        
        # Connect to MongoDB
        mongo_client = MongoClient(credentials['mongo']['uri'])
        mongo_db = mongo_client[credentials['mongo']['database']]
        logger.info("✅ Connected to MongoDB")
        
        return postgres_engine, mongo_client, mongo_db
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


def validate_database_credentials():
    """
    Validate that all required database credentials are present.
    
    Raises:
        ValueError: If required credentials are missing
    """
    credentials = get_database_credentials()
    
    if not credentials['postgres']['password']:
        raise ValueError("POSTGRES_PASSWORD environment variable is required")
    if not credentials['mongo']['password']:
        raise ValueError("MONGO_ROOT_PASSWORD environment variable is required")
