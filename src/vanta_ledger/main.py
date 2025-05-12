from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.requests import Request
from vanta_ledger.api.endpoints import router as api_router
import os
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vanta_ledger")

# Configure CORS to allow frontend origin on port 8500 (backend serving frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8500", "http://127.0.0.1:8500", "http://0.0.0.0:8500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Serve Vue.js frontend static files and index.html for root path
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(base_dir, "..", "..", "frontend"))

if os.path.isdir(frontend_path):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
    logger.info(f"Mounted static files from {frontend_path} at /")

    # Remove the explicit root route since StaticFiles with html=True serves index.html automatically
else:
    logger.warning("Frontend dist directory not found. Static files will not be served.")

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "ok"})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return JSONResponse(content={"detail": "Internal server error"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting VantaLedger backend server")
    uvicorn.run("vanta_ledger.main:app", host="0.0.0.0", port=8500, reload=True)
