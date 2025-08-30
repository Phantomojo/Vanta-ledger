import re
import subprocess
from pathlib import Path

# Define the unified dependency version baseline (from your analysis)
dependencies = {
    "fastapi": ">=0.95.0",
    "pydantic": ">=1.10.0",
    "python-jose": ">=3.3.0",
    "python-multipart": ">=0.0.6",
    "redis": ">=4.5.0",
    "black": ">=23.0.0",
    "pyarrow": ">=10.0.1",
    "pymysql": ">=1.0.2",
    "jinja2": ">=3.1.2",
    "pymongo": "==4.14.0",
    "PyPDF2": "==3.0.1",
    "Pillow": "==11.3.0",
    "transformers": ">=4.30.0",
    "torch": ">=2.0.0",
    "scikit-learn": "==1.7.1",
    "requests": "==2.32.4",
    "ecdsa": "==0.19.1",
    "sentence-transformers": ">=2.2.0",
    "llama-cpp-python": ">=0.2.0",
    "python-Levenshtein": ">=0.12.0",
    "regex": ">=2021.0.0"
}

# File locations (add/remove if needed)
target_files = [
    "phantomojo/Vanta-ledger/pyproject.toml",
    "phantomojo/Vanta-ledger/requirements.txt",
    "database/backup_20250807_004013/requirements.txt",
    "site-packages/pandas/pyproject.toml",
]

def update_dependency_lines(content, dep_map):
    new_lines = []
    for line in content.splitlines():
        updated_line = line
        for pkg, version in dep_map.items():
            # Replace if match found - more precise pattern matching
            if re.match(fr"^{re.escape(pkg)}[=><~]", line.strip(), re.IGNORECASE):
                updated_line = f"{pkg}{version}"
                break  # Only replace the first match per line
        new_lines.append(updated_line)
    return "\n".join(new_lines)

def update_file(file_path, dep_map):
    print(f"🛠 Updating: {file_path}")
    path = Path(file_path)
    if not path.exists():
        print(f"⚠️  Skipping missing file: {file_path}")
        return

    content = path.read_text()
    updated_content = update_dependency_lines(content, dep_map)
    path.write_text(updated_content)

def warn_about_venv_cfg(cfg_path):
    print(f"📘 Checking virtualenv: {cfg_path}")
    content = Path(cfg_path).read_text()
    for pkg, version in dependencies.items():
        if pkg.lower() in content.lower():
            print(f"⚠️  Check manually: '{pkg}' in {cfg_path} may not match desired version {version}")

def compile_requirements():
    if Path("requirements.in").exists():
        print("📦 Recompiling requirements with pip-tools...")
        subprocess.run(["pip-compile", "requirements.in", "--upgrade"], check=False)

def main():
    for file in target_files:
        update_file(file, dependencies)

    # Warn user about venv
    warn_about_venv_cfg("Vanta-ledger/.venv/pyvenv.cfg")

    # Recompile if using pip-tools
    compile_requirements()

    print("✅ All dependencies updated!")

if __name__ == "__main__":
    main()
