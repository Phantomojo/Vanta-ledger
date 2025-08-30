#!/usr/bin/env python3
"""
Database connection utilities.

Handles connections to PostgreSQL, MongoDB, and Redis with proper error handling
and fallback mechanisms for development environments.
"""

import time
from typing import Dict, Any, Optional

from .config import settings


def get_postgres_connection(timeout: int = 5):
    """
    Establish and return a new connection to the PostgreSQL database.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        psycopg2 connection object to the PostgreSQL database

    Raises:
        RuntimeError: If PostgreSQL driver is not available or connection fails
    """
    try:
        import psycopg2  # Lazy import to avoid hard dependency

        return psycopg2.connect(settings.POSTGRES_URI, connect_timeout=timeout)
    except Exception as e:
        raise RuntimeError(
            "PostgreSQL driver not available or connection failed"
        ) from e


def get_mongo_client(timeout_ms: int = 5000):
    """
    Create and return a MongoDB client instance.

    Args:
        timeout_ms: Connection timeout in milliseconds

    Returns:
        MongoClient connected to the MongoDB server

    Raises:
        RuntimeError: If MongoDB driver is not available or connection fails
    """
    try:
        import pymongo  # Lazy import

        return pymongo.MongoClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            uuidRepresentation="standard",
        )
    except Exception as e:
        raise RuntimeError("MongoDB driver not available or connection failed") from e


def get_redis_client(connect_timeout: int = 5, socket_timeout: int = 5):
    """
    Create and return a Redis client instance.

    Args:
        connect_timeout: Connection timeout in seconds
        socket_timeout: Socket timeout in seconds

    Returns:
        Redis client instance or NullRedis fallback
    """
    try:
        import redis  # Lazy import

        return redis.Redis.from_url(
            settings.REDIS_URI,
            decode_responses=True,
            socket_connect_timeout=connect_timeout,
            socket_timeout=socket_timeout,
        )
    except Exception:
        # Provide a no-op client to allow app to function without Redis
        class _NullRedis:
            def setex(self, *args, **kwargs):
                return True

            def exists(self, *args, **kwargs):
                return 0

            def ping(self):
                return False

        return _NullRedis()


# Health ping helpers with latency and version info


def postgres_ping(timeout: int = 5) -> Dict[str, Any]:
    """
    Test PostgreSQL connection and return health status.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with connection status and metadata
    """
    start = time.time()
    if not settings.POSTGRES_URI:
        return {"status": "skipped", "reason": "POSTGRES_URI not set"}
    try:
        import psycopg2

        conn = psycopg2.connect(settings.POSTGRES_URI, connect_timeout=timeout)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version_row = cur.fetchone()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return {
            "status": "ok",
            "latency_ms": int((time.time() - start) * 1000),
            "version": version_row[0] if version_row else None,
        }
    except Exception as e:
        return {
            "status": "error",
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }


def mongo_ping(timeout_ms: int = 5000) -> Dict[str, Any]:
    """
    Test MongoDB connection and return health status.

    Args:
        timeout_ms: Connection timeout in milliseconds

    Returns:
        Dictionary with connection status and metadata
    """
    start = time.time()
    if not settings.MONGO_URI:
        return {"status": "skipped", "reason": "MONGO_URI not set"}
    try:
        client = get_mongo_client(timeout_ms)
        client.admin.command("ping")
        info = client.server_info() if hasattr(client, "server_info") else {}
        return {
            "status": "ok",
            "latency_ms": int((time.time() - start) * 1000),
            "version": info.get("version"),
        }
    except Exception as e:
        return {
            "status": "error",
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }


def redis_ping(timeout: int = 5) -> Dict[str, Any]:
    """
    Test Redis connection and return health status.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with connection status and metadata
    """
    start = time.time()
    if not settings.REDIS_URI:
        return {"status": "skipped", "reason": "REDIS_URI not set"}
    try:
        client = get_redis_client(connect_timeout=timeout, socket_timeout=timeout)
        result = client.ping()
        return {
            "status": "ok" if result else "error",
            "latency_ms": int((time.time() - start) * 1000),
        }
    except Exception as e:
        return {
            "status": "error",
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }
