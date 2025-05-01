from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.requests import Request
from vanta_ledger.api.endpoints import router as api_router
import os
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vanta_ledger")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Determine frontend path dynamically and mount if exists
base_dir = os.path.dirname(os.path.abspath(__file__))
possible_frontend_dirs = [
    os.path.join(base_dir, "..", "..", "vanta-ledger", "frontend"),
    os.path.join(base_dir, "..", "..", "Vanta-ledger", "frontend"),
    os.path.join(base_dir, "..", "..", "frontend"),
]

frontend_path = None
for path in possible_frontend_dirs:
    if os.path.isdir(path):
        frontend_path = path
        break

if frontend_path:
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info(f"Mounted static files from {frontend_path}")
else:
    logger.warning("Frontend directory not found. Static files will not be served.")

@app.get("/")
def read_index():
    if frontend_path:
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.isfile(index_path):
            logger.info(f"Serving index.html from {index_path}")
            return FileResponse(index_path)
        else:
            logger.warning("index.html not found in frontend directory.")
    return JSONResponse(content={"message": "Frontend not available"}, status_code=404)

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
    uvicorn.run("src.vanta_ledger.main:app", host="0.0.0.0", port=8000, reload=True)

