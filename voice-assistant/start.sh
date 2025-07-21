#!/bin/bash

# Self-Aware Voice Assistant Startup Script
# This script activates the virtual environment and starts the voice assistant

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Self-Aware Voice Assistant..."
echo "Script directory: $SCRIPT_DIR"

# Change to the voice-assistant directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please create it first with:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Kill any existing processes on port 8000
echo "Checking for existing processes on port 8000..."
EXISTING_PIDS=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$EXISTING_PIDS" ]; then
    echo "Killing existing processes: $EXISTING_PIDS"
    kill $EXISTING_PIDS 2>/dev/null
    sleep 2
fi

# Start the application
echo "Starting voice assistant on http://localhost:8000"
python run.py