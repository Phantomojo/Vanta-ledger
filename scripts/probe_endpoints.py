#!/usr/bin/env python3
"""
Probe endpoints for Vanta Ledger backend.
Starts uvicorn in a thread and verifies key endpoints.
"""
import os
import time
import threading
import sys
from pathlib import Path
import requests
import logging
logger = logging.getLogger(__name__)

# Ensure project root on sys.path so `src.vanta_ledger` is importable when running from scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure debug so test routes are mounted
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ALLOW_MISSING_DATABASES", "True")
os.environ.setdefault("ENABLE_LOCAL_LLM", "False")

HOST = "127.0.0.1"
PORT = 8500
BASE = f"http://{HOST}:{PORT}"


def start_server():
    from src.vanta_ledger.main import app
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


def wait_for_health(timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def main():
    logger.info("🔎 Starting server and probing endpoints...\n")
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    ok = wait_for_health()
    if not ok:
        logger.info("❌ Server did not become healthy in time")
        return 1
    logger.info("✅ /health OK")

    def get(path, expect=None):
        url = f"{BASE}{path}"
        try:
            resp = requests.get(url, timeout=5)
            status = resp.status_code
            logger.info(f"GET {path} -> {status}")
            if expect is not None and status != expect:
                logger.info(f"   ⚠️ Expected {expect}, got {status}")
            else:
                # print small payload excerpt
                text = resp.text
                logger.info(f"   Body: {text[:180]}{")
        except Exception as e:
            logger.error(f"GET {path} -> ERROR: {e}")

    # readiness
    get("/ready")
    # system health (no AI)
    get("/health/system")
    # system health AI (likely 503 when models disabled)
    get("/health/system/ai", expect=None)
    # github models health
    get("/github-models/health")
    # debug-only helper endpoints
    get("/test-companies")

    # simple-auth (DEBUG only)
    try:
        r = requests.post(f"{BASE}/simple-auth", params={"username": "demo", "password": "demo"}, timeout=5)
        logger.info(f"POST /simple-auth -> {r.status_code}")
        logger.info(f"   Body: {r.text[:200]}{")
    except Exception as e:
        logger.error(f"POST /simple-auth -> ERROR: {e}")

    logger.info("\n🎯 Probe completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
