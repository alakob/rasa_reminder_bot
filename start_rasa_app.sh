#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
WEBUI_DIR="webui"
WEBUI_PORT=8888 # Port for the static file server
PID_FILE="$WEBUI_DIR/.serverpid"

# --- Functions ---
cleanup() {
  echo "Stopping services..."
  docker-compose down
  if [ -f "$PID_FILE" ]; then
    echo "Stopping Web UI server (PID: $(cat $PID_FILE))..."
    kill "$(cat $PID_FILE)" &> /dev/null || true # Ignore errors if already stopped
    rm -f "$PID_FILE"
  fi
  echo "Cleanup complete."
}

# Trap SIGINT (Ctrl+C) and SIGTERM to run cleanup
trap cleanup SIGINT SIGTERM

# --- Main Script ---

echo "Starting Rasa Docker services..."

# Check if docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    echo "Error: docker-compose.yml not found in the current directory."
    echo "Please run this script from the project root."
    exit 1
fi

# Start Docker containers in detached mode
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker services."
    exit 1
fi
echo "Docker services started successfully."
echo "----------------------------------------"

echo "Starting Web UI server..."

# Check if webui directory and index.html exist
if [ ! -d "$WEBUI_DIR" ] || [ ! -f "$WEBUI_DIR/index.html" ]; then
    echo "Error: '$WEBUI_DIR' directory or '$WEBUI_DIR/index.html' not found."
    echo "Make sure the Web UI files are present."
    cleanup # Stop docker services if web ui fails
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required to serve the Web UI but was not found."
    cleanup
    exit 1
fi

# Start Python's simple HTTP server in the background from the webui directory
echo "Serving files from '$WEBUI_DIR' on port $WEBUI_PORT..."
(cd "$WEBUI_DIR" && python3 -m http.server $WEBUI_PORT & echo $! > "$PID_FILE")

# Check if server started (very basic check - assumes it starts quickly if no error)
sleep 1 # Give it a moment to potentially fail
if ! kill -0 "$(cat $PID_FILE)" &> /dev/null; then
    echo "Error: Failed to start Python HTTP server on port $WEBUI_PORT."
    echo "Check if the port is already in use or if there are other errors."
    rm -f "$PID_FILE"
    cleanup
    exit 1
fi

echo "Web UI server started (PID: $(cat $PID_FILE))."
echo "----------------------------------------"
echo "Rasa Application Started Successfully!"
echo ""
echo "Access points:"
echo "  - Rasa HTTP API: http://localhost:5005"
echo "  - Action Server: http://localhost:5055 (usually not accessed directly)"
echo "  - Web UI Chat:   http://localhost:$WEBUI_PORT"
echo ""
echo "Press Ctrl+C to stop all services (Docker containers and Web UI server)."
echo "----------------------------------------"

# Keep the script alive to allow Ctrl+C trap to function
while true; do
    sleep 1
done

# The script will only exit via the trap now 