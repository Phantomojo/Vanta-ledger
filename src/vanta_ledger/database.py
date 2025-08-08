#!/usr/bin/env python3
"""
Database connection utilities
Handles connections to PostgreSQL, MongoDB, and Redis
"""

import psycopg2
import pymongo
import redis
from .config import settings

def get_postgres_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(settings.POSTGRES_URI)

def get_mongo_client():
    """Get MongoDB client"""
    return pymongo.MongoClient(settings.MONGO_URI)

def get_redis_client():
    """Get Redis client"""
    return redis.Redis.from_url(settings.REDIS_URI, decode_responses=True) 