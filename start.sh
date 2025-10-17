#!/bin/bash

# HintAI Easy Start Script
# Starts the backend server in the background

echo "🚀 Starting HintAI Backend Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Kill existing server if running
echo "🔍 Checking for existing server..."
pkill -f "backend/api/main.py" 2>/dev/null && echo "✓ Stopped existing server"

# Start server in background
echo "⚡ Starting server on http://localhost:8000..."
nohup python3 backend/api/main.py > hintai.log 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ HintAI backend is running! (PID: $SERVER_PID)"
    echo ""
    echo "📝 Logs: tail -f hintai.log"
    echo "🛑 Stop: ./stop.sh"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Now open Chrome and go to LeetCode!"
    echo "The extension will automatically connect."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ Failed to start server"
    echo "Check hintai.log for errors"
    exit 1
fi
