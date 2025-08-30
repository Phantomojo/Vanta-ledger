#!/usr/bin/env python3
"""
Database connection utilities
Handles connections to PostgreSQL, MongoDB, and Redis
"""

import time
from .config import settings


def get_postgres_connection(timeout: int = 5):
    """
    Establish and return a new connection to the PostgreSQL database using the configured URI.

    Returns:
        connection: A psycopg2 connection object to the PostgreSQL database.
    """
    try:
        import psycopg2  # Lazy import to avoid hard dependency at import time
        return psycopg2.connect(settings.POSTGRES_URI, connect_timeout=timeout)
    except Exception as e:
        raise RuntimeError(
            "PostgreSQL driver not available or connection failed"
        ) from e


def get_mongo_client(timeout_ms: int = 5000):
    """
    Create and return a MongoDB client instance using the configured connection URI.

    Returns:
        MongoClient: A client connected to the MongoDB server specified in the configuration.
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
    Create and return a Redis client instance connected using the configured URI.

    The client is set to decode responses as strings.
    Returns:
        Redis: A Redis client instance connected to the specified URI.
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

def postgres_ping(timeout: int = 5) -> dict:
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


def mongo_ping(timeout_ms: int = 5000) -> dict:
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


def redis_ping(connect_timeout: int = 5, socket_timeout: int = 5) -> dict:
    start = time.time()
    try:
        r = get_redis_client(connect_timeout=connect_timeout, socket_timeout=socket_timeout)
        ok = r.ping()
        version = None
        try:
            info = r.info()  # type: ignore[attr-defined]
            version = info.get("redis_version") if isinstance(info, dict) else None
        except Exception:
            pass
        return {
            "status": "ok" if ok else "error",
            "latency_ms": int((time.time() - start) * 1000),
            "version": version,
        }
    except Exception as e:
        return {
            "status": "error",
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }
