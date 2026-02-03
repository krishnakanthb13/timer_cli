#!/bin/bash

APP_NAME="Timer CLI"

echo "=== Launching $APP_NAME ==="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python is not installed or not in PATH."
    exit 1
fi

echo "[INFO] Using python: $($PYTHON_CMD --version)"

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Trap SIGINT for graceful shutdown if we spawn background processes
# (Not strictly necessary for a simple foreground CLI, but good practice)
trap 'echo "[INFO] Launcher exiting..."; exit' INT

# Run the application
$PYTHON_CMD -m src.main
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[ERROR] Application exited with code $EXIT_CODE"
    read -p "Press any key to exit..."
fi
