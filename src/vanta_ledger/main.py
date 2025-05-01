
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

@app.get("/")
def read_index():
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.vanta_ledger.main:app", host="0.0.0.0", port=8000, reload=True)
