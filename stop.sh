#!/bin/bash

# HintAI Stop Script
# Stops the background server

echo "🛑 Stopping HintAI Backend Server..."

if pkill -f "backend/api/main.py"; then
    echo "✅ Server stopped successfully"
else
    echo "ℹ️  No running server found"
fi
