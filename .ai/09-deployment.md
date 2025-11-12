# 09 - Deployment

## Three Deployment Models

### 1. Full Production (main.py)
- All databases: PostgreSQL + MongoDB + Redis
- AI features enabled
- Full feature set
- Use: Production environments

### 2. Simplified (simple_main.py)
- PostgreSQL only
- No MongoDB, Redis
- Core features
- Use: Cost-effective deployments

### 3. Testing (main_simple.py)
- No databases
- Minimal features
- Use: CI/CD, quick testing

## Docker Deployment
```bash
# Full stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

## Environment Variables (.env)
Required:
- POSTGRES_URI
- MONGO_URI (if using full)
- REDIS_URI (if using full)
- SECRET_KEY (32+ characters)
- POSTGRES_PASSWORD
- MONGO_INITDB_ROOT_PASSWORD

## Ports
- Backend: 8500
- Frontend: 5173
- PostgreSQL: 5432
- MongoDB: 27017
- Redis: 6379

## Monitoring
- Prometheus metrics at `/metrics`
- Health check at `/`
- Logs in `logs/app.log`

## Next: Common Tasks (`10-common-tasks.md`)
