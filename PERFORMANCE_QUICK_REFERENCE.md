# Performance Optimization Quick Reference

## Quick Wins Applied ✅

### 1. Use Connection Pooling
```python
# ✅ Good - Uses connection pool
from vanta_ledger.database import get_postgres_connection, release_postgres_connection

conn = get_postgres_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
finally:
    release_postgres_connection(conn)

# ❌ Bad - Creates new connection every time
conn = psycopg2.connect(DATABASE_URL)
```

### 2. Batch Database Operations
```python
# ✅ Good - Single query
ids = [1, 2, 3, 4, 5]
placeholders = ",".join([f":id{i}" for i in range(len(ids))])
params = {f"id{i}": pid for i, pid in enumerate(ids)}
result = conn.execute(f"SELECT * FROM docs WHERE id IN ({placeholders})", params)

# ❌ Bad - N queries
for id in ids:
    result = conn.execute("SELECT * FROM docs WHERE id = :id", {"id": id})
```

### 3. Lazy Load Heavy Resources
```python
# ✅ Good - Lazy loading
_nlp_model = None

def get_nlp_model():
    global _nlp_model
    if _nlp_model is None:
        _nlp_model = spacy.load("en_core_web_sm")
    return _nlp_model

# ❌ Bad - Loads at import time
nlp_model = spacy.load("en_core_web_sm")
```

### 4. Use Caching for Expensive Operations
```python
# ✅ Good - Cached
from vanta_ledger.optimizations.performance_optimizer import performance_optimizer

@performance_optimizer.cache_result(ttl=3600)
async def expensive_calculation(param):
    # Expensive operation
    return result

# ❌ Bad - Recalculates every time
async def expensive_calculation(param):
    # Expensive operation (runs every time)
    return result
```

### 5. Optimize JSON Parsing
```python
# ✅ Good - Type check before parsing
for field in ('address', 'contact_info'):
    value = data.get(field)
    if value and isinstance(value, str):
        try:
            data[field] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

# ❌ Bad - Always tries to parse
if data.get('address'):
    data['address'] = json.loads(data['address'])
if data.get('contact_info'):
    data['contact_info'] = json.loads(data['contact_info'])
```

## Performance Checklist

Before committing code, check:

- [ ] Database connections use pooling via `get_postgres_connection()`
- [ ] PostgreSQL connections are released with `release_postgres_connection()`
- [ ] No N+1 queries (batch load related data)
- [ ] Heavy models/resources are lazy loaded
- [ ] Expensive operations use caching
- [ ] Database queries use appropriate indexes
- [ ] No unbounded loops or memory growth
- [ ] JSON parsing only when needed

## Common Patterns

### Database Query Pattern
```python
# PostgreSQL
conn = get_postgres_connection()
try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM table WHERE id = %s", (id,))
        result = cursor.fetchone()
finally:
    release_postgres_connection(conn)
```

### MongoDB Query Pattern
```python
# MongoDB (reuses singleton client)
from vanta_ledger.database import get_mongo_client

client = get_mongo_client()
db = client.vanta_ledger
result = db.collection.find({"key": "value"})
```

### Redis Pattern
```python
# Redis (reuses connection pool)
from vanta_ledger.database import get_redis_client

redis = get_redis_client()
redis.set("key", "value", ex=3600)
result = redis.get("key")
```

### Batch Processing Pattern
```python
# Process items in batches
BATCH_SIZE = 100

for i in range(0, len(items), BATCH_SIZE):
    batch = items[i:i + BATCH_SIZE]
    process_batch(batch)  # Single DB call per batch
```

## Performance Monitoring

### Check System Metrics
```python
from vanta_ledger.optimizations.performance_optimizer import performance_optimizer

metrics = performance_optimizer.performance_monitor()

print(f"CPU: {metrics['system']['cpu_percent']}%")
print(f"Memory: {metrics['system']['memory_percent']}%")
print(f"Redis Hit Rate: {metrics['redis']['keyspace_hits']}")
```

### Profile Slow Queries
```python
# MongoDB
db.set_profiling_level(1, slow_ms=100)
slow_queries = db.system.profile.find({millis: {"$gt": 100}})

# PostgreSQL
# Check pg_stat_statements extension
```

## Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| High memory usage | `performance_optimizer.optimize_memory_usage()` |
| Slow queries | Check indexes with `.explain()` |
| Connection pool exhausted | Verify connections are released |
| Rate limit errors | Check IP tracking cleanup |
| Cache misses | Verify cache keys are consistent |

## Performance Scripts

### Run Database Optimization
```bash
python scripts/optimize_database_indexes.py
```

### Validate Optimizations
```bash
python scripts/test_performance_optimizations.py
```

### Clear Old Cache
```python
from vanta_ledger.optimizations.performance_optimizer import performance_optimizer
performance_optimizer.optimize_memory_usage()
```

## Key Metrics

| Metric | Target | Action if Exceeded |
|--------|--------|-------------------|
| Connection pool usage | <80% | Increase pool size or check for leaks |
| Memory growth | <1MB/hr | Run memory optimization |
| Query time (indexed) | <100ms | Check indexes and query optimization |
| Cache hit rate | >70% | Review cache keys and TTL |
| Rate limit errors | <1% | Check IP cleanup configuration |

## Documentation

- Full guide: `PERFORMANCE_OPTIMIZATION.md`
- Summary: `OPTIMIZATION_SUMMARY.md`
- Index script: `scripts/optimize_database_indexes.py`
- Test script: `scripts/test_performance_optimizations.py`

## Support

For performance issues:
1. Check monitoring dashboard
2. Review application logs
3. Run profiling tools
4. Check this quick reference
5. See full documentation

---
**Last Updated**: 2024
**Status**: Production Ready ✅
