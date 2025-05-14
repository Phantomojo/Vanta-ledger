# Vanta Ledger

This project is a ledger application with a Python Kivy-based mobile and desktop UI.

## Setup

1. Create and activate a Python virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the backend API server (optional):

```bash
uvicorn src.vanta_ledger.main:app --reload
```

4. Run the Kivy UI app:

```bash
./run.sh
```

or on Windows:

```bash
run.bat
```

## Mobile Application

The frontend is implemented using Kivy, which supports mobile and desktop platforms. The app can be packaged for Android using Buildozer.

### Packaging for Android

#### Prerequisites

- Linux environment (Ubuntu recommended)
- Python 3.7+
- Install Buildozer and dependencies:

```bash
sudo apt update
sudo apt install -y python3-pip python3-setuptools git \
    build-essential libssl-dev libffi-dev python3-dev \
    libsqlite3-dev
pip install --upgrade cython
pip install buildozer
```

#### Initialize Buildozer

From the project root directory:

```bash
buildozer init
```

This creates a `buildozer.spec` file.

#### Configure buildozer.spec

- Set `title = Vanta Ledger`
- Set `package.name = vanta_ledger`
- Set `package.domain = org.example`
- Add required Python modules to `requirements` (e.g., kivy, sqlite3, etc.)
- Set `source.include_exts = py,png,jpg,kv,atlas`
- Adjust other settings as needed.

#### Build the APK

```bash
buildozer -v android debug
```

This will download the Android SDK/NDK and build the APK.

#### Deploy to Device

Connect your Android device via USB with debugging enabled:

```bash
buildozer android deploy run
```

## Notes

- The app uses a local SQLite database (`vanta_ledger.db`).
- Ensure the database is properly initialized on the device or implement syncing as needed.
- The app UI and functionality are designed for mobile use but may require UI adjustments for different screen sizes.
- The login/access token mechanism has been removed for simplicity; the app is accessible without authentication.

## Removed Frontends

- The old Vue.js frontend and Tkinter UI app have been removed.
- The current UI is implemented using Kivy for better mobile and desktop support.

## Project Cleanup

- Unused frontend files and dependencies have been removed.
- The project is cleaned up to focus on the Kivy UI app and backend API.

## Troubleshooting

- The Kivy app requires system clipboard utilities `xclip` and `xsel` on Linux.
- If you encounter crashes or segmentation faults, it may be related to graphics drivers or Kivy compatibility.
- Consider running the app with debug logging enabled for troubleshooting.

For any issues or further customization, please refer to the Kivy and Buildozer documentation.
