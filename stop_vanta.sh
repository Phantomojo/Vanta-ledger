#!/bin/bash

# Stop Vanta Ledger services
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
rm -f .backend.pid .frontend.pid 2>/dev/null || true
echo "✅ Vanta Ledger stopped" 