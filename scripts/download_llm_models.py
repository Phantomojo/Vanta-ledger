#!/usr/bin/env python3
"""
Download Local LLM Models for Vanta Ledger
Optimized for RTX 3050 GPU with automatic hardware detection
"""

import os
import sys
import requests
import json
from pathlib import Path
from tqdm import tqdm
import hashlib
import logging
logger = logging.getLogger(__name__)

def download_file(url: str, filepath: str, expected_sha256: str = None, headers: dict = None):
    """Download file with progress bar and SHA256 verification"""
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as file, tqdm(
            desc=os.path.basename(filepath),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                pbar.update(size)
        
        # Verify SHA256 if provided
        if expected_sha256:
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                if file_hash != expected_sha256:
                    logger.warning(f"Warning: SHA256 mismatch for {filepath}")
                    logger.info(f"Expected: {expected_sha256}")
                    logger.info(f"Got: {file_hash}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

def get_rtx3050_models():
    """Get model configurations optimized for RTX 3050"""
    return {
        "mistral_7b": {
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "path": "models/mistral/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "size_gb": 4.1,
            "description": "Primary model for general text processing",
            "sha256": None  # Add SHA256 if available
        },
        "phi3_mini": {
            "url": "https://huggingface.co/TheBloke/Phi-3-mini-4k-instruct-GGUF/resolve/main/phi-3-mini-4k-instruct.Q4_K_M.gguf",
            "path": "models/phi3/phi-3-mini-4k-instruct.Q4_K_M.gguf",
            "size_gb": 2.1,
            "description": "Secondary model for quick analysis",
            "sha256": None
        },
        "tinyllama": {
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "path": "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "size_gb": 0.6,
            "description": "Fallback model for lightweight tasks",
            "sha256": None
        }
    }

def get_cpu_models():
    """Get model configurations for CPU-only systems"""
    return {
        "phi3_mini": {
            "url": "https://huggingface.co/TheBloke/Phi-3-mini-4k-instruct-GGUF/resolve/main/phi-3-mini-4k-instruct.Q4_K_M.gguf",
            "path": "models/phi3/phi-3-mini-4k-instruct.Q4_K_M.gguf",
            "size_gb": 2.1,
            "description": "Primary model for CPU processing",
            "sha256": None,
            "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        },
        "tinyllama": {
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "path": "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "size_gb": 0.6,
            "description": "Secondary model for CPU processing",
            "sha256": None
        }
    }

def detect_hardware():
    """Detect available hardware"""
    try:
        import sys
        sys.path.append('venv/lib/python3.12/site-packages')
        from GPUtil import getGPUs
        gpus = getGPUs()
        if gpus:
            gpu = gpus[0]
            if "RTX 3050" in gpu.name:
                return "rtx3050"
            elif "RTX" in gpu.name:
                return "rtx_other"
            else:
                return "gpu_generic"
        else:
            return "cpu_only"
    except:
        return "cpu_only"

def main():
    """Main download function"""
    logger.info("🚀 Vanta Ledger Local LLM Model Downloader")
    logger.info("=")
    
    # Detect hardware
    hardware_type = detect_hardware()
    logger.info(f"Detected hardware: {hardware_type}")
    
    # Select models based on hardware
    if hardware_type == "rtx3050":
        models = get_rtx3050_models()
        logger.info("📦 Downloading models optimized for RTX 3050")
    elif hardware_type in ["rtx_other", "gpu_generic"]:
        models = get_rtx3050_models()  # Use same models for other GPUs
        logger.info("📦 Downloading models for GPU processing")
    else:
        models = get_cpu_models()
        logger.info("📦 Downloading models optimized for CPU processing")
    
    logger.info(f"Total models to download: {len(models)}")
    
    # Calculate total size
    total_size_gb = sum(model["size_gb"] for model in models.values())
    logger.info(f"Total download size: {total_size_gb:.1f} GB")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with the download? (y/N): ")
    if response.lower() != 'y':
        logger.info("Download cancelled.")
        return
    
    # Download models
    successful_downloads = 0
    failed_downloads = 0
    
    for model_name, model_info in models.items():
        logger.info(f"\n📥 Downloading {model_name}...")
        logger.info(f"   Description: {model_info[")
        logger.info(f"   Size: {model_info[")
        
        if os.path.exists(model_info["path"]):
            logger.info(f"   ⚠️  Model already exists, skipping...")
            successful_downloads += 1
            continue
        
        if download_file(model_info["url"], model_info["path"], model_info.get("sha256"), model_info.get("headers")):
            logger.info(f"   ✅ {model_name} downloaded successfully!")
            successful_downloads += 1
        else:
            logger.error(f"   ❌ Failed to download {model_name}")
            failed_downloads += 1
    
    # Summary
    logger.info("\n")
    logger.info("📊 Download Summary:")
    logger.info(f"   Successful: {successful_downloads}")
    logger.error(f"   Failed: {failed_downloads}")
    logger.info(f"   Total: {len(models)}")
    
    if successful_downloads > 0:
        logger.info("\n🎉 Models downloaded successfully!")
        logger.info("Next steps:")
        logger.info("1. Install LLM dependencies: pip install -r backend/requirements-llm.txt")
        logger.info("2. Start the Vanta Ledger backend")
        logger.info("3. Check model status: GET /api/v2/llm/models/status")
    else:
        logger.info("\n❌ No models were downloaded successfully.")
        logger.info("Please check your internet connection and try again.")

if __name__ == "__main__":
    main() 