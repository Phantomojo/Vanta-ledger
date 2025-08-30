#!/usr/bin/env python3
"""
Vanta Ledger - Test Launcher

Purpose
- One-command launcher to bring the backend up for smoke testing.
- Creates/uses a local virtualenv (test_venv), installs minimal dependencies,
  sets safe dev environment, and starts Uvicorn.

Usage
- python3 scripts/launch_test_server.py

Options
- Set environment variables HOST and PORT if you need a different bind (defaults 127.0.0.1:8500).
- Set AUTO_PROBE=true to run scripts/probe_endpoints.py after server is up (best effort).

Notes
- Uses DEBUG=True and ALLOW_MISSING_DATABASES=True so it can start without DBs.
- Writes/updates a simple .env for local runs if missing.
- To stop the server, press Ctrl+C.
"""
import os
import sys
import subprocess
import venv
import shutil
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = REPO_ROOT / "test_venv"
PY = str((VENV_DIR / "bin" / "python"))
PIP = str((VENV_DIR / "bin" / "pip"))
UVICORN = str((VENV_DIR / "bin" / "uvicorn"))

MIN_DEPS = [
    "fastapi",
    "uvicorn",
    "python-multipart",
    "python-dotenv",
    "requests",
    "prometheus-client",
    "pydantic",
    "redis",
    "pymongo",
    "SQLAlchemy",
    "passlib[bcrypt]",
    "python-jose[cryptography]",
    "psutil",
]

DEFAULT_ENV = {
    "DEBUG": "True",
    "ALLOW_MISSING_DATABASES": "True",
    "ENABLE_LOCAL_LLM": "False",
    "ENABLE_GITHUB_MODELS": "True",
    "ALLOWED_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
    # Use a stable default secret key for dev smoke runs
    "SECRET_KEY": os.environ.get("SECRET_KEY", "development-secret-key-for-tests"),
}


def ensure_venv():
    if not VENV_DIR.exists():
        print(f"[launcher] Creating virtualenv at {VENV_DIR} ...")
        venv.EnvBuilder(with_pip=True, clear=False, symlinks=True).create(VENV_DIR)
    else:
        print(f"[launcher] Using existing virtualenv at {VENV_DIR}")


def install_min_deps():
    print("[launcher] Ensuring minimal dependencies are installed ...")
    try:
        subprocess.check_call([PY, "-m", "pip", "--version"])  # sanity check
        # Use quiet upgrade strategy; best effort
        subprocess.check_call([PIP, "install", "--upgrade", "pip", "setuptools", "wheel"])  # noqa: E501
        subprocess.check_call([PIP, "install", *MIN_DEPS])
    except subprocess.CalledProcessError as e:
        print("[launcher] Failed to install dependencies:", e)
        sys.exit(1)


def ensure_dotenv():
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        print("[launcher] Writing .env for local testing ...")
        lines = [f"{k}={v}\n" for k, v in DEFAULT_ENV.items()]
        env_path.write_text("".join(lines), encoding="utf-8")
    else:
        # Append missing keys without overwriting existing values
        existing = env_path.read_text(encoding="utf-8").splitlines()
        keys_in_file = {line.split("=", 1)[0] for line in existing if "=" in line and not line.strip().startswith("#")}
        with env_path.open("a", encoding="utf-8") as f:
            for k, v in DEFAULT_ENV.items():
                if k not in keys_in_file:
                    f.write(f"{k}={v}\n")


def set_runtime_env():
    # Export directly into current process as well to affect Uvicorn subprocess
    for k, v in DEFAULT_ENV.items():
        os.environ.setdefault(k, v)


def run_uvicorn():
    host = os.environ.get("HOST", "127.0.0.1")
    port = os.environ.get("PORT", "8500")
    app_path = "src.vanta_ledger.main:app"

    print("\n[launcher] Starting Vanta Ledger API for testing ...")
    print(f"[launcher] URL: http://{host}:{port}")
    print("[launcher] Useful endpoints:")
    print("  - /health")
    print("  - /ready")
    print("  - /metrics")
    print("  - /health/system  (snapshot)")
    print("  - /health/system/ai  (503 unless GitHub Models token set)")
    print("  - /test-companies (DEBUG only)")
    print("\n[launcher] Press Ctrl+C to stop.\n")

    # Launch uvicorn in foreground; propagate current env
    cmd = [UVICORN, app_path, "--host", host, "--port", port, "--log-level", "info"]
    proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT))

    # Optional: probe endpoints after a short wait
    if os.environ.get("AUTO_PROBE", "false").lower() == "true":
        time.sleep(2)
        try:
            subprocess.call([PY, str(REPO_ROOT / "scripts" / "probe_endpoints.py")])
        except Exception:
            pass

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n[launcher] Stopping server ...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    # Basic check we're in project root
    if not (REPO_ROOT / "src" / "vanta_ledger" / "main.py").exists():
        print("[launcher] Error: Could not find src/vanta_ledger/main.py. Run from repo root.")
        sys.exit(1)

    ensure_venv()
    install_min_deps()
    ensure_dotenv()
    set_runtime_env()
    run_uvicorn()


if __name__ == "__main__":
    main()
