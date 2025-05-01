from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from vanta_ledger.api.endpoints import router as api_router
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vanta_ledger")

# Configure CORS to allow frontend origin on port 8001
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "ok"})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting VantaLedger backend server")
    uvicorn.run("src.vanta_ledger.main:app", host="0.0.0.0", port=8500, reload=True)
