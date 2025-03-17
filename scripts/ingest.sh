#!/bin/bash
# Quick script to ingest documents from the raw directory

set -e # Exit immediately if a command exits with a non-zero status

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Ingest documents from the raw directory
echo "Ingesting documents from data/raw directory..."
python -m graphqna ingest --directory data/raw --pattern "*.md" --move-processed

echo "Done!"