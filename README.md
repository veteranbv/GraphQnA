# GraphQnA: Graph-Enhanced Question Answering Powered by Neo4j

![GraphQnA Logo](docs/images/icon-graphqna.jpg)

GraphQnA is a powerful domain-agnostic question-answering system built on Neo4j's GraphRAG framework. It combines vector search, knowledge graph traversal, and LLM reasoning to provide accurate, context-aware answers to complex questions about your domain knowledge.

## Table of Contents

- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Domain Configuration](#domain-configuration)
- [Ingesting Documents](#ingesting-documents)
- [Asking Questions](#asking-questions)
- [API and Slack Integration](#api-and-slack-integration)
- [CLI Reference](#cli-reference)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Key Features

- **Hybrid Retrieval Orchestration** - Automatically selects the optimal retrieval method based on query type
- **Domain-Agnostic Design** - Works with any knowledge domain through centralized configuration
- **Intelligent Knowledge Graph Building** - LLM-powered extraction of entities and relationships
- **Multiple Retrieval Strategies**:
  - **Vector Retrieval** - Semantic similarity search for factual information
  - **GraphRAG** - Enhanced retrieval leveraging graph structure for context
  - **Knowledge Graph (KG)** - Direct Cypher query generation
  - **Enhanced KG** - Schema-guided retrieval for complex questions
- **REST API & Slack Bot** - Multiple interfaces for easy integration
- **Comprehensive Testing** - Domain-specific test suites with detailed metrics
- **Enterprise-Class CLI** - Full command-line tools for all operations

## Quick Start

```bash
# Clone the repository
git clone https://github.com/veteranbv/graphqna.git
cd graphqna

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure your environment
cp .env.example .env
# Edit .env with your Neo4j and OpenAI credentials

# Create domain configuration
cp graphqna/config/domain_config_example.py graphqna/config/domain_config.py
# Edit domain_config.py to customize for your domain

# Ingest documents
./scripts/ingest.sh

# Try the demo
python scripts/hybrid_qa_demo.py
```

## Architecture Overview

GraphQnA employs a sophisticated hybrid architecture that combines multiple retrieval methods:

### Retrieval Methods Overview

1. **Vector Retrieval**: Uses embedding similarity to find relevant document chunks
   - Best for: Factual questions and information retrieval
   - Implementation: `VectorRetriever` in `graphqna/retrieval/vector.py`

2. **GraphRAG**: Combines vector similarity with graph traversal
   - Best for: General questions requiring contextual awareness
   - Implementation: `GraphRetriever` in `graphqna/retrieval/graph.py`

3. **Knowledge Graph**: Converts questions directly to Cypher queries
   - Best for: Simple entity and relationship questions
   - Implementation: `KnowledgeGraphRetriever` in `graphqna/retrieval/kg.py`

4. **Enhanced Knowledge Graph**: Schema-aware Cypher generation
   - Best for: Complex entity and relationship questions
   - Implementation: `EnhancedKGRetriever` in `graphqna/retrieval/enhanced_kg.py`

### Hybrid Retrieval Orchestration

The hybrid retriever (`HybridRetriever` in `graphqna/retrieval/hybrid_retriever.py`) automatically selects the best method for each question:

1. **Query Classification**: Analyzes the question type (factual, procedural, entity, relationship)
2. **Method Selection**:
   - Factual questions → GraphRAG (with Vector fallback)
   - Procedural questions → GraphRAG (with Vector fallback)
   - Entity questions → Enhanced KG (with GraphRAG fallback)
   - Relationship questions → Enhanced KG (with KG fallback)
3. **Fallback Mechanisms**: If the primary method fails or returns a generic answer, alternative methods are tried

### Knowledge Graph Visualization

The ingestion process creates a rich knowledge graph with entities and relationships. Here's a visualization of an example knowledge graph created by GraphQnA, viewed in Neo4j Bloom:

![Knowledge Graph Visualization](docs/images/graphqna-bloom-visualisation.jpg)

*A Neo4j Bloom visualization showing entities (nodes) and relationships extracted from documents. Different node types are color-coded, revealing the rich semantic structure that enhances question answering.*

### Processing Pipeline

Documents are processed through a multi-stage pipeline:

1. **Document Loading**: Support for various formats (markdown, PDF, etc.)
2. **Chunking**: Text is split into manageable chunks
3. **Embedding**: Chunks are embedded using OpenAI models
4. **Schema Detection**: LLM identifies entity and relationship types
5. **Knowledge Graph Extraction**: Entities and relationships are extracted from text
6. **Graph Import**: Knowledge is imported into Neo4j

## Installation

### Prerequisites

- **Python 3.9+**
- **Neo4j Database** (Neo4j Aura or self-hosted)
- **OpenAI API key** (for GPT-4 and embeddings)

### Step-by-Step Setup

1. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up Neo4j**:

   - For Neo4j Aura (recommended):
     - Create an account at [Neo4j Aura](https://neo4j.com/cloud/aura/)
     - Create a new database instance
     - Save the connection URI, username, and password

   - For self-hosted Neo4j:
     - Install Neo4j (version 5.0+)
     - Configure authentication

3. **Configure environment variables**:

   Create a `.env` file with:

   ```bash
   NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   NEO4J_DATABASE=neo4j
   OPENAI_API_KEY=your-openai-api-key
   EMBEDDING_DIMENSIONS=3072  # For text-embedding-3-large
   ```

4. **Create domain configuration**:

   ```bash
   cp graphqna/config/domain_config_example.py graphqna/config/domain_config.py
   # Edit domain_config.py to customize for your domain
   ```

5. **Verify installation**:

   ```bash
   python -m graphqna db --check-connection
   python -m graphqna db --check-index
   ```

## Domain Configuration

GraphQnA is designed to be domain-agnostic through a centralized configuration system.

### Key Domain Settings

Your domain configuration (`domain_config.py`) includes:

- **Domain Metadata**: Name and description
- **Entity Definitions**: Types of objects in your domain
- **Relationship Definitions**: How entities relate to each other
- **Schema Triplets**: Valid entity-relationship-entity combinations
- **Response Templates**: Consistent messaging
- **Fallback Queries**: Backup database queries
- **LLM Prompts**: Domain-specific instructions for various components

### Domain Configuration Example

```python
# Domain metadata
DOMAIN_NAME = "HealthcareKnowledge"
DOMAIN_DESCRIPTION = "A knowledge graph for healthcare documentation"

# Entity definitions
ENTITY_DEFINITIONS = [
    {
        "label": "Condition",
        "description": "A medical condition or diagnosis",
        "properties": [
            {"name": "name", "type": "STRING"},
            {"name": "description", "type": "STRING"},
            {"name": "icd10_code", "type": "STRING"},
        ],
    },
    # More entity definitions...
]

# Relationship definitions
RELATION_DEFINITIONS = [
    {
        "label": "TREATS",
        "description": "A treatment that addresses a condition",
        "properties": [{"name": "effectiveness", "type": "STRING"}],
    },
    # More relationship definitions...
]
```

## Ingesting Documents

The ingestion process converts documents into a knowledge graph with embeddings, entities, and relationships.

### File Organization

- **Raw Data**: Place source files in `data/raw/`
- **Processed Data**: Successfully processed files move to `data/processed/`
- **Logs**: System logs are stored in `logs/`
- **Output**: Generated outputs appear in `output/`

### Ingestion Methods

#### Using the CLI

```bash
# Process a single file
python -m graphqna ingest --file path/to/document.md

# Process all files in a directory
python -m graphqna ingest --directory data/raw --pattern "*.md"

# Clear database before ingestion
python -m graphqna ingest --file path/to/document.md --clear

# Move processed files
python -m graphqna ingest --directory data/raw --move-processed

# Skip already processed files
python -m graphqna ingest --directory data/raw --skip-existing
```

#### Using the Convenience Script

```bash
./scripts/ingest.sh
```

This handles common ingestion scenarios automatically.

### Behind the Scenes

The ingestion pipeline (`graphqna/ingest/pipeline.py`) orchestrates:

1. Document chunking with specified size and overlap
2. Embedding generation using OpenAI models
3. Schema detection from document content
4. Knowledge graph extraction using LLMs
5. Importing entities and relationships into Neo4j
6. Creating a vector index for similarity search

## Asking Questions

### CLI Query Interface

```bash
# Ask a simple question
python -m graphqna query "What is GraphQnA?"

# Specify retrieval method
python -m graphqna query "How do I configure the system?" --method vector

# Show retrieved context
python -m graphqna query "What are the key features?" --context

# Process multiple questions
python -m graphqna query --file path/to/questions.txt

# Save responses to files
python -m graphqna query --file questions.txt --output-dir output/results
```

### Interactive Mode

```bash
# Start interactive session
python -m graphqna query --interactive
# Or use the convenience script
./scripts/run_interactive.sh
```

In interactive mode:

- Type questions to get answers
- Type `vector`, `graphrag`, `kg`, `enhanced_kg`, or `hybrid` to change methods
- Type `context` to toggle context display
- Type `exit`, `quit`, or `q` to exit

### Retrieval Methods

- **hybrid** (default): Automatically selects the best method
- **vector**: Pure vector similarity search
- **graphrag**: Neo4j's GraphRAG framework
- **kg**: Knowledge graph query generation
- **enhanced_kg**: Schema-guided Cypher generation

### Hybrid Retrieval Demo

Try the demo script to compare all retrieval methods:

```bash
python scripts/hybrid_qa_demo.py
```

This demo offers three modes:

1. Compare all retrieval methods on a single query
2. Run example questions for each query type
3. Try your own question with the hybrid retriever

## API and Slack Integration

GraphQnA includes both a REST API and Slack bot for easy integration.

### REST API

#### Starting the API Server

```bash
python scripts/run_api.py
```

#### Available Endpoints

- `GET /api/health` - Check service health
- `GET /api/info` - Get service information
- `POST /api/query` - Answer a question
- `POST /api/ingest` - Ingest a document (placeholder)

#### Example API Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is GraphQnA?",
    "retrieval_method": "hybrid"
  }'
```

### Slack Bot Integration

The Slack bot integration allows teams to ask questions directly in Slack channels or via direct messages.

![Slack Bot Integration](docs/images/graphqna-slackbot.jpg)

*Screenshot showing a sample interaction with the GraphQnA Slack bot. The bot provides comprehensive answers with source information and feedback buttons.*

#### Setup and Configuration

```bash
# Set environment variables
export SLACK_BOT_TOKEN=xoxb-your-bot-token
export SLACK_APP_TOKEN=xapp-your-app-token
export SLACK_SIGNING_SECRET=your-signing-secret

# Start the Slack bot
python scripts/run_slack_bot.py
```

#### Slack Bot Features

- **Direct Messages**: Send questions directly to the bot
- **Channel Mentions**: Mention the bot in a channel
- **Monitored Channels**: Bot can listen in specific channels
- **Feedback Collection**: Users can provide feedback on answers
- **Threaded Responses**: Keeps conversations organized
- **Confidence Filtering**: Only responds when confident in non-primary channels

### Production Deployment

For production deployment, GraphQnA includes systemd service files:

Located in `deployment/systemd/`, these files allow you to run the API and Slack bot as system services:

```bash
# Copy service files to systemd directory
sudo cp deployment/systemd/graphqna-api.service /etc/systemd/system/
sudo cp deployment/systemd/graphqna-slackbot.service /etc/systemd/system/

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable graphqna-api
sudo systemctl start graphqna-api
sudo systemctl enable graphqna-slackbot
sudo systemctl start graphqna-slackbot
```

The service files are configured to:
- Run the API and Slack bot as system services
- Automatically restart on failure
- Load environment variables from your `.env` file
- Run as a dedicated system user for security
- Output logs to the system journal

## CLI Reference

GraphQnA provides a comprehensive command-line interface:

```bash
# Show help information
python -m graphqna --help
```

### Main Commands

- `ingest` - Process documents into the knowledge graph
- `query` - Ask questions using the knowledge graph
- `db` - Manage the Neo4j database
- `test` - Run test suites to evaluate system performance

### Database Management

```bash
# Show database statistics
python -m graphqna db --stats

# Clear the database
python -m graphqna db --clear

# Check database connection
python -m graphqna db --check-connection

# Reset vector index
python -m graphqna db --reset-vector-index --dimensions 3072

# Check vector index configuration
python -m graphqna db --check-index

# Create database backup
python -m graphqna db --backup output/database_backup.cypher
```

### Testing

GraphQnA includes extensive testing capabilities:

```bash
# Run basic test suite
python -m graphqna test

# Run full test suite with all methods
python -m graphqna test --suite full --method all

# Run custom tests from a file
python -m graphqna test --suite custom --file path/to/test_questions.md

# Write test results to a file
python -m graphqna test --output output/test_results.json

# Show detailed information
python -m graphqna test --verbose
```

#### Domain-Specific Testing

Create domain-specific test questions:

```bash
cp tests/resources/test_questions_template.md tests/resources/test_questions_domain.md
```

Then customize these questions to match your domain's terminology and use cases.

## Configuration Options

GraphQnA can be configured through environment variables or the `.env` file:

| Option | Description | Default |
|--------|-------------|---------|
| `NEO4J_URI` | Neo4j database connection URI | - |
| `NEO4J_USERNAME` | Neo4j database username | - |
| `NEO4J_PASSWORD` | Neo4j database password | - |
| `NEO4J_DATABASE` | Neo4j database name | `neo4j` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `LLM_MODEL` | OpenAI model to use | `gpt-4o` |
| `LLM_TEMPERATURE` | Temperature for LLM generation | `0.0` |
| `LLM_MAX_TOKENS` | Maximum tokens for LLM responses | `2000` |
| `EMBEDDING_MODEL` | Embedding model to use | `text-embedding-3-large` |
| `EMBEDDING_DIMENSIONS` | Dimensions of embedding vectors | `3072` |
| `CHUNK_SIZE` | Text chunk size for processing | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `VECTOR_TOP_K` | Number of chunks to retrieve | `5` |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | `INFO` |
| `VECTOR_INDEX_NAME` | Name of the vector index in Neo4j | `document-chunks` |

## Troubleshooting

### Vector Dimension Mismatch

If you encounter "Index query vector has X dimensions, but indexed vectors have Y dimensions":

1. **Check settings**:

   ```bash
   cat .env | grep DIMENSIONS
   python -m graphqna db --check-index
   ```

2. **Reset the index**:

   ```bash
   python -m graphqna db --reset-vector-index --dimensions 3072
   ```

3. **Re-ingest documents**:

   ```bash
   python -m graphqna ingest --directory data/raw --clear
   ```

### Database Connection Issues

If you have trouble connecting to Neo4j:

1. **Verify connection**:

   ```bash
   python -m graphqna db --check-connection
   ```

2. **Check credentials** in `.env`

3. **For Neo4j Aura**: Ensure your IP is on the allowlist

### Ingestion Problems

If document processing fails:

1. **Check the logs** in `logs/graphqna.log`

2. **Process a single file** to isolate issues:

   ```bash
   python -m graphqna ingest --file path/to/document.md
   ```

3. **Verify vector index**:

   ```bash
   python -m graphqna db --check-index
   ```

## Development

### Project Structure

```bash
/
├── graphqna/              # Core package
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Module entry point
│   ├── api/               # API implementation
│   │   ├── server.py      # FastAPI server
│   │   └── slack_bot.py   # Slack integration
│   ├── cli/               # Command-line interface
│   │   ├── main.py        # CLI entry point
│   │   └── commands/      # Command modules
│   ├── config/            # Configuration management
│   │   ├── settings.py    # Settings handler
│   │   └── domain_config*.py # Domain configuration
│   ├── db/                # Database connectivity
│   │   ├── neo4j.py       # Neo4j connection
│   │   └── vector_index.py # Vector index management
│   ├── ingest/            # Document ingestion
│   │   ├── chunker.py     # Text chunking
│   │   ├── embedder.py    # Vector embedding
│   │   ├── kg_builder.py  # Knowledge graph builder
│   │   └── pipeline.py    # End-to-end pipeline
│   ├── models/            # Data models
│   └── retrieval/         # Retrieval strategies
│       ├── base.py        # Base retriever
│       ├── vector.py      # Vector retrieval
│       ├── graph.py       # GraphRAG retrieval
│       ├── kg.py          # Knowledge graph retrieval
│       ├── enhanced_kg.py # Enhanced KG retrieval
│       ├── hybrid_retriever.py # Hybrid orchestrator
│       └── service.py     # Unified service
├── scripts/               # Utility scripts
├── data/                  # Data files
├── docs/                  # Documentation
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   ├── resources/         # Test resources
│   └── unit/              # Unit tests
└── requirements.txt       # Dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=graphqna
```

## License

Licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
