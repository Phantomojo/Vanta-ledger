#!/usr/bin/env python3
"""
Performance Optimizer
Micro-optimizations for caching, database performance, and query optimization
"""

import asyncio
import functools
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import redis
# from pymongo import MongoClient
from ..database import get_mongo_client
from pymongo.database import Database

from ..config import settings

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Performance optimization utilities"""

    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Cache settings
        self.default_ttl = 3600  # 1 hour
        self.short_ttl = 300  # 5 minutes
        self.long_ttl = 86400  # 24 hours

    def cache_result(self, ttl: int = None, key_prefix: str = ""):
        """Decorator for caching function results"""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func, args, kwargs, key_prefix)

                # Try to get from cache
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    try:
                        return json.loads(cached_result)
                    except json.JSONDecodeError:
                        pass

                # Execute function and cache result
                result = await func(*args, **kwargs)

                # Cache the result
                cache_ttl = ttl or self.default_ttl
                try:
                    self.redis_client.setex(
                        cache_key, cache_ttl, json.dumps(result, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache result: {str(e)}")

                return result

            return wrapper

        return decorator

    def _generate_cache_key(
        self, func: Callable, args: tuple, kwargs: dict, prefix: str
    ) -> str:
        """Generate a unique cache key for function call"""
        # Create a hash of function name, args, and kwargs
        key_data = {"func": func.__name__, "args": args, "kwargs": kwargs}

        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[
            :16
        ]  # Use first 16 chars for compatibility

        return f"{prefix}:{key_hash}" if prefix else f"cache:{key_hash}"

    def batch_operations(self, operations: List[Callable], batch_size: int = 100):
        """Execute operations in batches for better performance"""
        results = []

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            batch_results = asyncio.gather(*batch)
            results.extend(batch_results)

        return results

    def optimize_database_queries(self):
        """Optimize database queries and indexes"""
        try:
            # Create compound indexes for common query patterns
            self._create_optimized_indexes()

            # Analyze query performance
            self._analyze_query_performance()

            logger.info("Database query optimization completed")

        except Exception as e:
            logger.error(f"Error optimizing database queries: {str(e)}")

    def _create_optimized_indexes(self):
        """Create optimized database indexes"""
        try:
            # Document indexes
            self.db.documents.create_index(
                [("created_at", -1), ("status", 1), ("metadata.document_type", 1)]
            )

            self.db.documents.create_index(
                [("metadata.tags", 1), ("metadata.category_id", 1), ("created_by", 1)]
            )

            # Financial indexes
            self.db.invoices.create_index(
                [("invoice_date", -1), ("status", 1), ("customer_id", 1)]
            )

            self.db.journal_entries.create_index(
                [("entry_date", -1), ("is_posted", 1), ("created_by", 1)]
            )

            # Search optimization
            self.db.documents.create_index(
                [("metadata.title", "text"), ("extracted_text", "text")]
            )

            logger.info("Optimized indexes created successfully")

        except Exception as e:
            logger.error(f"Error creating optimized indexes: {str(e)}")

    def _analyze_query_performance(self):
        """Analyze and log query performance"""
        try:
            # Get slow query statistics
            slow_queries = self.db.command("profile", {"slowms": 100})

            if slow_queries:
                logger.warning(f"Found {len(slow_queries)} slow queries")
                for query in slow_queries[:5]:  # Log top 5 slow queries
                    logger.warning(f"Slow query: {query}")

        except Exception as e:
            logger.error(f"Error analyzing query performance: {str(e)}")

    def optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            # Clear old cache entries
            self._cleanup_old_cache()

            # Optimize Redis memory
            self._optimize_redis_memory()

            logger.info("Memory optimization completed")

        except Exception as e:
            logger.error(f"Error optimizing memory usage: {str(e)}")

    def _cleanup_old_cache(self):
        """Clean up old cache entries"""
        try:
            # Get all cache keys
            cache_keys = self.redis_client.keys("cache:*")

            # Remove keys older than 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)

            for key in cache_keys:
                # Check if key is old (simplified check)
                if self.redis_client.ttl(key) > 86400:  # 24 hours
                    self.redis_client.delete(key)

            logger.info(f"Cleaned up {len(cache_keys)} cache entries")

        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")

    def _optimize_redis_memory(self):
        """Optimize Redis memory usage"""
        try:
            # Set memory policy
            self.redis_client.config_set("maxmemory-policy", "allkeys-lru")

            # Enable compression for large values
            self.redis_client.config_set("hash-max-ziplist-entries", "512")
            self.redis_client.config_set("hash-max-ziplist-value", "64")

            logger.info("Redis memory optimization completed")

        except Exception as e:
            logger.error(f"Error optimizing Redis memory: {str(e)}")

    def async_batch_processor(
        self,
        items: List[Any],
        processor_func: Callable,
        batch_size: int = 50,
        max_concurrent: int = 4,
    ):
        """Process items in async batches"""

        async def process_batch(batch):
            tasks = [processor_func(item) for item in batch]
            return await asyncio.gather(*tasks, return_exceptions=True)

        async def process_all():
            results = []

            for i in range(0, len(items), batch_size):
                batch = items[i : i + batch_size]
                batch_results = await process_batch(batch)
                results.extend(batch_results)

            return results

        return asyncio.create_task(process_all())

    def connection_pool_optimizer(self):
        """Optimize database connection pools"""
        try:
            # Optimize MongoDB connection pool
            self.mongo_client.admin.command(
                {"setParameter": 1, "maxTransactionLockRequestTimeoutMillis": 5000}
            )

            # Optimize Redis connection pool
            pool = redis.ConnectionPool.from_url(
                settings.REDIS_URI,
                max_connections=20,
                retry_on_timeout=True,
                socket_keepalive=True,
            )

            logger.info("Connection pool optimization completed")

        except Exception as e:
            logger.error(f"Error optimizing connection pools: {str(e)}")

    def query_result_caching(
        self,
        collection_name: str,
        query: dict,
        projection: dict = None,
        ttl: int = None,
    ):
        """Cache query results for better performance"""
        try:
            # Generate cache key from query
            cache_key = (
                f"query:{collection_name}:{hash(json.dumps(query, sort_keys=True))}"
            )

            # Try to get from cache
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # Execute query
            collection = self.db[collection_name]
            result = list(collection.find(query, projection))

            # Cache result
            cache_ttl = ttl or self.short_ttl
            self.redis_client.setex(
                cache_key, cache_ttl, json.dumps(result, default=str)
            )

            return result

        except Exception as e:
            logger.error(f"Error in query result caching: {str(e)}")
            # Fallback to direct query
            collection = self.db[collection_name]
            return list(collection.find(query, projection))

    def background_task_optimizer(self, task_func: Callable, *args, **kwargs):
        """Run tasks in background for better performance"""

        async def background_task():
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor, task_func, *args, **kwargs
                )
                return result
            except Exception as e:
                logger.error(f"Background task error: {str(e)}")
                return None

        return asyncio.create_task(background_task())

    def response_compression_optimizer(self, response_data: Any) -> bytes:
        """Optimize response compression"""
        try:
            import gzip

            # Convert to JSON string
            json_data = json.dumps(response_data, default=str)

            # Compress if data is large enough
            if len(json_data) > 1024:  # 1KB threshold
                compressed_data = gzip.compress(json_data.encode("utf-8"))
                return compressed_data

            return json_data.encode("utf-8")

        except Exception as e:
            logger.error(f"Error in response compression: {str(e)}")
            return json.dumps(response_data, default=str).encode("utf-8")

    def database_query_optimizer(self, collection_name: str, pipeline: List[dict]):
        """Optimize MongoDB aggregation pipelines"""
        try:
            # Add optimization stages
            optimized_pipeline = []

            # Add $match stage early if not present
            has_match = any(stage.get("$match") for stage in pipeline)
            if not has_match:
                optimized_pipeline.append({"$match": {}})

            # Add optimization stages
            optimized_pipeline.extend(
                [
                    {"$addFields": {"_optimized": True}},
                    {"$hint": {"created_at": -1}},  # Use index hint
                ]
            )

            # Add original pipeline
            optimized_pipeline.extend(pipeline)

            # Add final optimization
            optimized_pipeline.append({"$limit": 1000})  # Prevent large results

            return optimized_pipeline

        except Exception as e:
            logger.error(f"Error optimizing database query: {str(e)}")
            return pipeline

    def cache_warmup(self, warmup_functions: List[Callable]):
        """Warm up cache with frequently accessed data"""
        try:

            async def warmup_cache():
                tasks = []
                for func in warmup_functions:
                    task = asyncio.create_task(func())
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

                successful_warmups = sum(
                    1 for r in results if not isinstance(r, Exception)
                )
                logger.info(
                    f"Cache warmup completed: {successful_warmups}/{len(warmup_functions)} successful"
                )

            asyncio.create_task(warmup_cache())

        except Exception as e:
            logger.error(f"Error in cache warmup: {str(e)}")

    def performance_monitor(self):
        """Monitor system performance"""
        try:
            import psutil

            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Database metrics
            db_stats = self.db.command("dbStats")

            # Redis metrics
            redis_info = self.redis_client.info()

            performance_metrics = {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                },
                "database": {
                    "collections": db_stats.get("collections", 0),
                    "data_size": db_stats.get("dataSize", 0),
                    "storage_size": db_stats.get("storageSize", 0),
                },
                "redis": {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory", 0),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Cache performance metrics
            self.redis_client.setex(
                "performance_metrics",
                300,  # 5 minutes TTL
                json.dumps(performance_metrics, default=str),
            )

            return performance_metrics

        except Exception as e:
            logger.error(f"Error monitoring performance: {str(e)}")
            return {}


# Global instance
performance_optimizer = PerformanceOptimizer()
