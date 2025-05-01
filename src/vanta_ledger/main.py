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

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Vanta-ledger", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_index():
    index_path = os.path.join(frontend_path, "index.html")
    logger.info(f"Serving index.html from {index_path}")
    return FileResponse(index_path)

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

