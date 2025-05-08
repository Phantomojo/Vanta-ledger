#!/bin/bash

# Check if npm is installed
if ! command -v npm &> /dev/null
then
    echo "npm could not be found. Please install Node.js and npm to build the frontend."
    echo "You can install Node.js from https://nodejs.org/"
    exit 1
fi

echo "Building Vue.js frontend..."
cd frontend-vue
npm install || { echo "npm install failed. Check your network or proxy settings."; exit 1; }
npx vue-cli-service build || { echo "Vue build failed. Ensure @vue/cli-service is installed."; exit 1; }
cd ..

echo "Copying built frontend to backend static directory..."
rm -rf frontend
mkdir frontend
cp -r frontend-vue/dist/* frontend/

echo "Starting VantaLedger backend..."
PYTHONPATH=$(pwd)/src uvicorn --app-dir src vanta_ledger.main:app --host 0.0.0.0 --port 8500 --reload
