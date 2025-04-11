#!/bin/bash

# Simple startup script for Rasa Reminder Bot

# Configuration
WEB_INTERFACE_PORT=8080

# --- Functions ---
cleanup() {
    echo "[INFO] Cleaning up background processes..."
    # Find PIDs of the background jobs started by this script and kill them
    # Using pkill with a specific pattern might be safer if processes are managed elsewhere
    if [ -n "$ACTION_SERVER_PID" ]; then kill $ACTION_SERVER_PID; fi
    if [ -n "$RASA_SERVER_PID" ]; then kill $RASA_SERVER_PID; fi
    if [ -n "$HTTP_SERVER_PID" ]; then kill $HTTP_SERVER_PID; fi
    echo "[INFO] Cleanup finished."
    exit 0
}

check_port() {
    if lsof -i :$1 > /dev/null; then
        echo "[ERROR] Port $1 is already in use. Please free it up or choose a different port." >&2
        exit 1
    fi
}

# --- Main Script ---

# Trap SIGINT (Ctrl+C) and SIGTERM to run cleanup
trap cleanup SIGINT SIGTERM

# 1. Activate Virtual Environment
echo "[INFO] Activating virtual environment..."
if [ -f "rasa_venv/bin/activate" ]; then
    source rasa_venv/bin/activate
else
    echo "[ERROR] Virtual environment 'rasa_venv' not found. Please create it first." >&2
    exit 1
fi

# 2. Kill previous Rasa processes (use pkill for broader cleanup)
echo "[INFO] Attempting to kill previously running Rasa processes..."
pkill -f "rasa run"
# Give a moment for processes to terminate
sleep 1

# Check if required ports are free
echo "[INFO] Checking required ports..."
check_port 5055 # Action Server
check_port 5005 # Rasa Server
check_port $WEB_INTERFACE_PORT # Web Interface

# 3. Start Action Server in background
echo "[INFO] Starting Rasa Action Server on port 5055..."
rasa run actions --debug & # Remove --debug for less verbose logs
ACTION_SERVER_PID=$!
sleep 2 # Give it a moment to start

# Check if Action Server started successfully (basic check)
if ! kill -0 $ACTION_SERVER_PID 2>/dev/null; then
    echo "[ERROR] Failed to start Rasa Action Server." >&2
    exit 1
fi
echo "[INFO] Action Server PID: $ACTION_SERVER_PID"

# 4. Start Rasa Server in background
echo "[INFO] Starting Rasa Server on port 5005..."
rasa run --enable-api --cors "*" --debug --endpoints endpoints.yml --credentials credentials.yml & # Remove --debug for less verbose logs
RASA_SERVER_PID=$!
sleep 5 # Give it more time as it loads the model

# Check if Rasa Server started successfully (basic check)
if ! kill -0 $RASA_SERVER_PID 2>/dev/null; then
    echo "[ERROR] Failed to start Rasa Server." >&2
    cleanup # Attempt cleanup before exiting
    exit 1
fi
echo "[INFO] Rasa Server PID: $RASA_SERVER_PID"


# 5. Start Simple HTTP server for index.html
echo "[INFO] Starting HTTP server for web interface on port $WEB_INTERFACE_PORT..."
if [ -f "index.html" ]; then
    python3 -m http.server $WEB_INTERFACE_PORT &
    HTTP_SERVER_PID=$!
    sleep 1
else
    echo "[WARNING] index.html not found. Web interface will not be available." >&2
    HTTP_SERVER_PID=""
fi

if [ -n "$HTTP_SERVER_PID" ]; then
    if ! kill -0 $HTTP_SERVER_PID 2>/dev/null; then
        echo "[ERROR] Failed to start HTTP server for web interface." >&2
        cleanup
        exit 1
    fi
    echo "[INFO] HTTP Server PID: $HTTP_SERVER_PID"
fi

# 6. Provide output
echo ""
echo "--------------------------------------------------"
echo "Rasa Reminder Bot Startup Complete!"
echo "--------------------------------------------------"
echo "  - Rasa Server API: http://localhost:5005"
if [ -n "$HTTP_SERVER_PID" ]; then
    echo "  - Web Interface:   http://localhost:$WEB_INTERFACE_PORT"
else
    echo "  - Web Interface: Not started (index.html not found)"
fi
echo "  - Action Server: Running (PID: $ACTION_SERVER_PID)"
echo ""
echo "Press Ctrl+C to stop all services."

# Keep the script running to wait for background processes
wait $RASA_SERVER_PID $ACTION_SERVER_PID $HTTP_SERVER_PID 