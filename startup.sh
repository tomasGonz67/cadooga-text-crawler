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



# Wait for user to stop
wait $API_PID 