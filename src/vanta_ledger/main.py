from fastapi import FastAPI
from vanta_ledger.api.endpoints import router as api_router

app = FastAPI(title="VantaLedger")

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Welcome to VantaLedger"}
