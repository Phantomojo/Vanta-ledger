# VantaLedger Application

## Running Backend with Docker

1. Build the backend Docker image:
   \`\`\`
   docker build -f backend.Dockerfile -t vantaledger-backend .
   \`\`\`

2. Run the backend container:
   \`\`\`
   docker run -d -p 8500:8500 vantaledger-backend
   \`\`\`

## Running Frontend with Docker

1. Build the frontend Docker image:
   \`\`\`
   docker build -f frontend.Dockerfile -t vantaledger-frontend .
   \`\`\`

2. Run the frontend container:
   \`\`\`
   docker run -d -p 3000:3000 vantaledger-frontend
   \`\`\`

## Running Android WebView App

1. Open the \`android-webview-app\` folder in Android Studio.

2. Build and run the app on an emulator or physical device.

3. The app loads the frontend served at \`http://10.0.2.2:3000\` (adjust if needed).

## Notes

- Ensure backend is running and accessible at \`http://localhost:8500\`.

- The Android emulator uses \`10.0.2.2\` to access host machine localhost.

- You can customize the Android app URL in \`MainActivity.kt\`.

- For production, consider bundling frontend assets inside the app or hosting backend remotely.
