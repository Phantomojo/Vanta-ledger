#!/usr/bin/env python3
"""
Database connection utilities
Handles connections to PostgreSQL, MongoDB, and Redis
"""

import psycopg2
import psycopg2.pool
import pymongo
import redis

from .config import settings

# Global connection pools for reuse
_postgres_pool = None
_mongo_client = None
_redis_pool = None


def _get_postgres_pool():
    """Get or create PostgreSQL connection pool"""
    global _postgres_pool
    if _postgres_pool is None:
        _postgres_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=settings.POSTGRES_URI
        )
    return _postgres_pool


def get_postgres_connection():
    """
    Get a connection from the PostgreSQL connection pool.
    
    Returns:
        connection: A pooled psycopg2 connection object to the PostgreSQL database.
    """
    pool = _get_postgres_pool()
    return pool.getconn()


def release_postgres_connection(conn):
    """
    Return a PostgreSQL connection to the pool.
    
    Args:
        conn: The connection to return to the pool.
    """
    pool = _get_postgres_pool()
    pool.putconn(conn)


def get_mongo_client():
    """
    Get or create a singleton MongoDB client instance.

    Returns:
        MongoClient: A reusable client connected to the MongoDB server.
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = pymongo.MongoClient(
            settings.MONGO_URI,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=45000,
            serverSelectionTimeoutMS=5000
        )
    return _mongo_client


def get_redis_client():
    """
    Get a Redis client from the connection pool.

    The client is set to decode responses as strings.
    Returns:
        Redis: A Redis client instance from the connection pool.
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URI,
            max_connections=20,
            decode_responses=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            retry_on_timeout=True
        )
    return redis.Redis(connection_pool=_redis_pool)
