#!/bin/bash
# Script to rebuild the knowledge base and run evaluation tests

set -e # Exit immediately if a command exits with a non-zero status

echo "===== Knowledge Base Rebuild and Test ====="
echo "Starting at $(date)"

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Create logs and output directories if they don't exist
mkdir -p logs
mkdir -p output
mkdir -p data/processed

# Step 1: Clear the database
echo ""
echo "Step 1: Clearing database..."
python -m graphqna db --clear --force

# Step 2: Ingest documents
echo ""
echo "Step 2: Ingesting documents..."
python -m graphqna ingest --directory data/raw --pattern "*.md" --move-processed

# Step 3: Run full test suite
echo ""
echo "Step 3: Running full test suite..."
python -m graphqna test --suite full --method all

echo ""
echo "All done! The knowledge base has been rebuilt and tested."
echo "Completed at $(date)"

# Display information about how to use the system
echo ""
echo "===== How to Use the System ====="
echo "1. Interactive mode:"
echo "   python -m graphqna query --interactive"
echo ""
echo "2. Direct question:"
echo "   python -m graphqna query \"your question here\""
echo ""
echo "3. Choose retrieval method:"
echo "   python -m graphqna query \"your question here\" --method vector|graph|kg"
echo ""
echo "4. Show retrieved context:"
echo "   python -m graphqna query \"your question here\" --context"
echo ""
echo "5. Run tests:"
echo "   python -m graphqna test --suite basic|full|custom"