from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from vanta_ledger.api.endpoints import router as api_router
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Vanta-ledger', 'frontend')
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_index():
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.vanta_ledger.main:app", host="0.0.0.0", port=8000, reload=True)
