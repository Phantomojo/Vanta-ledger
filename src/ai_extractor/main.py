from fastapi import FastAPI, Body
from typing import Dict

app = FastAPI()

@app.post("/extract")
def extract(data: Dict = Body(...)):
    ocr_text = data.get("ocr_text", "")
    # Placeholder for extraction logic
    return {"amounts": [], "dates": [], "companies": [], "addresses": [], "confidence_score": 0.0} 