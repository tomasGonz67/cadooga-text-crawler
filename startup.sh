#!/bin/bash

# Text Crawler Test Script
# Starts FastAPI server and runs crawler test

set -e



# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start FastAPI server in background
echo "📡 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000


# Wait for FastAPI to start
echo "⏳ Waiting for FastAPI server to start..."
sleep 5

# Check if FastAPI is running
if ! curl -f http://localhost:${PORT}/health/live >/dev/null 2>&1; then
    echo "❌ FastAPI server failed to start"
    cleanup
    exit 1
fi



# Wait for user to stop
wait $API_PID 