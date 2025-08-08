#!/usr/bin/env python3
"""
Vanta Ledger - Simplified Main FastAPI Application
For testing and systems verification
"""

import os
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import settings
from .config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Vanta Ledger API",
    description="Advanced document processing and financial data management system",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Handles the root endpoint and returns a status message with the API version.
    
    Returns:
        dict: A JSON object containing a status message and the API version.
    """
    return {"message": "Vanta Ledger API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """
    Return the current health status, timestamp, and API version for service monitoring.
    
    Returns:
        dict: A JSON-serializable dictionary with keys "status", "timestamp", and "version".
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

@app.get("/test")
async def test_endpoint():
    """
    Handles GET requests to the /test endpoint, returning a success message for verification purposes.
    
    Returns:
        dict: A JSON object with a confirmation message and success status.
    """
    return {"message": "Test endpoint working", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500) 