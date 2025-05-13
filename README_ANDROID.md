# Vanta Ledger Android App Packaging and Usage

## Overview
This project includes a Kivy-based frontend app (`frontend/kivy_app.py`) that can be packaged and deployed as an Android app using Buildozer.

## Login Information
- The app uses an access token for login.
- The default admin access token is: `supersecretadmintoken`
- To login, enter this token in the "Access Token" field and press "Login".
- You can change the access token after login, but the admin token is reserved and cannot be used as a user token.

## Packaging for Android

### Prerequisites
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

### Initialize Buildozer
From the project root directory:
```bash
buildozer init
```
This creates a `buildozer.spec` file.

### Configure buildozer.spec
- Set `title = Vanta Ledger`
- Set `package.name = vanta_ledger`
- Set `package.domain = org.example`
- Add required Python modules to `requirements` (e.g., kivy, sqlite3, etc.)
- Set `source.include_exts = py,png,jpg,kv,atlas`
- Adjust other settings as needed.

### Build the APK
```bash
buildozer -v android debug
```
This will download the Android SDK/NDK and build the APK.

### Deploy to Device
Connect your Android device via USB with debugging enabled:
```bash
buildozer android deploy run
```

## Notes
- The app uses a local SQLite database (`vanta_ledger.db`).
- Ensure the database is properly initialized on the device or implement syncing as needed.
- The app UI and functionality are designed for mobile use but may require UI adjustments for different screen sizes.

## Fixing Warnings
- The backend uses Pydantic v2 style config.
- SQLAlchemy declarative_base import updated.
- Passlib crypt deprecation warning is from dependency; consider upgrading passlib if needed.

For any issues or further customization, please refer to the Kivy and Buildozer documentation.

---
