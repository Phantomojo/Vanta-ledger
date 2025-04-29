from fastapi import APIRouter

router = APIRouter()

@router.get("/transactions")
def get_transactions():
    return {"data": "This will list transactions"}
