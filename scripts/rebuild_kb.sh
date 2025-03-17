#!/bin/bash
# Script to rebuild the knowledge base and demonstrate system functionality

set -e # Exit immediately if a command exits with a non-zero status

echo "===== Knowledge Base Rebuild and Demo ====="
echo "Starting at $(date)"

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Ensure directories exist
mkdir -p logs
mkdir -p output
mkdir -p data/processed

# Step 1: Clear and rebuild the knowledge base
echo ""
echo "Step 1: Clearing database..."
python -m graphqna db --clear --force

echo ""
echo "Step 2: Ingesting documents..."
python -m graphqna ingest --directory data/raw --pattern "*.md" --move-processed

# Step 3: Run database statistics
echo ""
echo "Step 3: Checking database statistics..."
python -m graphqna db --stats

# Step 4: Demo different retrieval methods
echo ""
echo "Step 4: Demonstrating retrieval methods..."

# Get domain name and example queries from domain_config.py
DOMAIN_NAME=$(python -c "from graphqna.config import get_settings; print(get_settings().domain_name)")

# Use domain-specific examples when available, or fall back to generic queries
VECTOR_QUERY=$(python -c "
from graphqna.config import get_settings
settings = get_settings()
example_queries = settings.example_queries
domain_name = settings.domain_name

# Try to get a factual query
if 'factual' in example_queries and example_queries['factual']:
    query = example_queries['factual'][0]
    print(query.format(domain_name=domain_name) if '{domain_name}' in query else query)
else:
    print(f'What is {domain_name} used for?')
")

GRAPH_QUERY=$(python -c "
from graphqna.config import get_settings
settings = get_settings()
example_queries = settings.example_queries
domain_name = settings.domain_name

# Try to get an entity query
if 'entity' in example_queries and example_queries['entity']:
    query = example_queries['entity'][0]
    print(query.format(domain_name=domain_name) if '{domain_name}' in query else query)
else:
    print(f'What types of entities exist in {domain_name}?')
")

KG_QUERY=$(python -c "
from graphqna.config import get_settings
settings = get_settings()
example_queries = settings.example_queries
domain_name = settings.domain_name

# Try to get a relationship query
if 'relationship' in example_queries and example_queries['relationship']:
    query = example_queries['relationship'][0]
    print(query.format(domain_name=domain_name) if '{domain_name}' in query else query)
else:
    print('What relationships exist between different entities?')
")

echo ""
echo "Vector retrieval demo:"
python -m graphqna query "$VECTOR_QUERY" --method vector

echo ""
echo "GraphRAG retrieval demo:"
python -m graphqna query "$GRAPH_QUERY" --method graphrag

echo ""
echo "Knowledge graph retrieval demo:"
python -m graphqna query "$KG_QUERY" --method kg

echo ""
echo "All done! The knowledge base has been rebuilt and the system is ready to use."
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
echo "   python -m graphqna query \"your question here\" --method vector|graphrag|kg|enhanced_kg|hybrid"
echo ""
echo "4. Show retrieved context:"
echo "   python -m graphqna query \"your question here\" --context"
echo ""
echo "5. Run tests:"
echo "   python -m graphqna test --suite basic|full|custom"