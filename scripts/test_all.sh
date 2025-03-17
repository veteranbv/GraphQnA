#!/bin/bash
# Script to test a variety of questions using the integrated test framework

set -e # Exit immediately if a command exits with a non-zero status

# Get domain name from domain_config.py
DOMAIN_NAME=$(python -c "from graphqna.config import get_settings; print(get_settings().domain_name)")

echo "===== Testing $DOMAIN_NAME Knowledge Base ====="
echo "Starting at $(date)"

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Ensure virtual environment is activated
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Create logs and output directories if they don't exist
mkdir -p logs
mkdir -p output

# Run the CLI test command with different options
echo ""
echo "===== Running Basic Test Suite ====="
python -m graphqna test --suite basic --method graphrag

echo ""
echo "===== Running Full Test Suite ====="
python -m graphqna test --suite full --method all --output output/test_results.json

echo ""
echo "All done! Tests completed."
echo "Completed at $(date)"

# Show how to run more tests
echo ""
echo "===== Additional Testing Options ====="
echo "To run tests with specific options:"
echo ""
echo "1. Basic test suite with vector retrieval:"
echo "   python -m graphqna test --suite basic --method vector"
echo ""
echo "2. Full test suite with all methods:"
echo "   python -m graphqna test --suite full --method all"
echo ""
echo "3. Custom tests from your own file:"
echo "   python -m graphqna test --suite custom --file path/to/questions.md"
echo ""
echo "4. Show detailed results including full answers:"
echo "   python -m graphqna test --verbose"
echo ""
echo "5. Rebuild the knowledge base before running tests:"
echo "   python -m graphqna test --rebuild"