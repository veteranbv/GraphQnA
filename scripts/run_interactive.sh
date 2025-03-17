#!/bin/bash
# Quick script to run the interactive query interface

set -e # Exit immediately if a command exits with a non-zero status

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run interactive query
echo "Starting interactive query session..."
python -m graphqna query --interactive