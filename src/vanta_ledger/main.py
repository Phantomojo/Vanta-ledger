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

# Configure CORS to allow frontend origin on port 8001
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://172.25.99.222:8001", "http://127.0.0.1:8001", "http://0.0.0.0:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Serve frontend static files and index.html for root path
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(base_dir, "..", "..", "frontend"))

if os.path.isdir(frontend_path):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info(f"Mounted static files from {frontend_path} at /static")

    # Serve index.html at root for simpler deployment
    from fastapi.responses import FileResponse

    @app.get("/")
    async def serve_index():
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            logger.warning("index.html not found in frontend directory")
            return JSONResponse(content={"detail": "Frontend not found"}, status_code=404)
else:
    logger.warning("Frontend directory not found. Static files will not be served.")

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
