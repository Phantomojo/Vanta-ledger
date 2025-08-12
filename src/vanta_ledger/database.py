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
    """
    Establish and return a new connection to the PostgreSQL database using the configured URI.

    Returns:
        connection: A new psycopg2 connection object to the PostgreSQL database.
    """
    return psycopg2.connect(settings.POSTGRES_URI)


def get_mongo_client():
    """
    Create and return a MongoDB client instance using the configured connection URI.

    Returns:
        MongoClient: A client connected to the MongoDB server specified in the configuration.
    """
    return pymongo.MongoClient(settings.MONGO_URI)


def get_redis_client():
    """
    Create and return a Redis client instance connected using the configured URI.

    The client is set to decode responses as strings.
    Returns:
        Redis: A Redis client instance connected to the specified URI.
    """
    return redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)
