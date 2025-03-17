#!/bin/bash
# Quick script to clear the database

set -e # Exit immediately if a command exits with a non-zero status

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Clear the database
echo "Clearing the database..."
python -m graphqna db --clear

echo "Done!"