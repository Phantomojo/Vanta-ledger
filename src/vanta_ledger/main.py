<<<<<<< HEAD

app.include_router(api_router, prefix="/api")

<<<<<<< HEAD
@app.get(
    "/expenditures/",
    response_model=list[models.ExpenditureResponse],
    summary="Retrieve a list of expenditures",
    description="This endpoint retrieves a list of expenditures with optional pagination using skip and limit parameters."
)
async def read_expenditures(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    expenditures = crud.get_expenditures(db=db, skip=skip, limit=limit)
    return expenditures
=======
# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Vanta-ledger', 'frontend')
app.mount("/static", StaticFiles(directory=frontend_path), name="static")
>>>>>>> 3bc79707d12f701260e4fbf614f102ff472003a2
=======
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

# Serve frontend static files from unified directory
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

    @app.get("/")
    def read_index():
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.isfile(index_path):
            logger.info(f"Serving index.html from {index_path}")
            return FileResponse(index_path)
        else:
            logger.warning("index.html not found in frontend directory.")
            return JSONResponse(content={"message": "Frontend index.html not found"}, status_code=404)

    @app.get("/app.js")
    def serve_app_js():
        app_js_path = os.path.join(frontend_path, "app.js")
        if os.path.isfile(app_js_path):
            logger.info(f"Serving app.js from {app_js_path}")
            return FileResponse(app_js_path)
        else:
            logger.warning("app.js not found in frontend directory.")
            return JSONResponse(content={"message": "Frontend app.js not found"}, status_code=404)
else:
    logger.warning("Frontend directory not found. Static files will not be served.")

    @app.get("/")
    def root():
        return JSONResponse(content={"message": "Backend API is running. Frontend not available."})

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