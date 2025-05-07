# VantaLedger Application

## Project Overview

VantaLedger is a ledger management system designed to help users track and manage financial transactions efficiently. It consists of a FastAPI backend API, a modern frontend dashboard built with Tailwind CSS and Alpine.js, and an Android WebView app that provides mobile access to the frontend interface.

## Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, Tailwind CSS, Alpine.js, Font Awesome
- **Mobile App:** Android WebView
- **Containerization:** Docker

## Backend

The backend is a FastAPI application exposing RESTful APIs under the `/api` prefix. It handles transaction data management and serves static frontend files optionally.

### Running Backend with Docker

1. Build the backend Docker image:
   ```bash
   docker build -f backend.Dockerfile -t vantaledger-backend .
   ```

2. Run the backend container:
   ```bash
   docker run -d -p 8500:8500 vantaledger-backend
   ```

### Running Backend Locally

To run the backend locally without Docker, ensure you have Python and dependencies installed, then run:

```bash
uvicorn src.vanta_ledger.main:app --host 0.0.0.0 --port 8500 --reload
```

The backend listens on port 8500 by default.

## Frontend

The frontend is a responsive dashboard web app named "VantaLedger Dashboard" built with Tailwind CSS and Alpine.js. It provides features such as:

- Viewing transaction lists with details (ID, type, amount, description, date)
- Adding and updating transactions via a form
- Exporting transactions
- Dark mode toggle
- Access token-based login

### Running Frontend with Docker

1. Build the frontend Docker image:
   ```bash
   docker build -f frontend.Dockerfile -t vantaledger-frontend .
   ```

2. Run the frontend container:
   ```bash
   docker run -d -p 3000:3000 vantaledger-frontend
   ```

### Running Frontend Locally

You can serve the frontend files using any static file server or open `frontend/index.html` directly in a browser. The frontend expects the backend API to be accessible at `http://localhost:8500/api`.

## Android WebView App

The Android app is a WebView wrapper that loads the frontend dashboard. It is designed to run on Android devices or emulators.

### Running the Android App

1. Open the `android-webview-app` folder in Android Studio.
2. Build and run the app on an emulator or physical device.
3. The app loads the frontend served at `http://10.0.2.2:3000` by default (adjust if needed).

You can customize the frontend URL in `MainActivity.kt`.

## Docker Usage Summary

- Backend runs on port 8500
- Frontend runs on port 3000
- Android app connects to frontend via `10.0.2.2` (Android emulator localhost)

## Notes

- Ensure the backend is running and accessible at `http://localhost:8500`.
- The Android emulator uses `10.0.2.2` to access the host machine's localhost.
- For production deployment, consider bundling frontend assets inside the Android app or hosting the backend remotely.
- CORS is configured to allow frontend origin on port 8001 for local development.

## License

*(Add license information here if applicable)*

## Contribution

Contributions are welcome. Please open issues or pull requests for improvements or bug fixes.

---

&copy; 2025 VantaLedger. All rights reserved.
