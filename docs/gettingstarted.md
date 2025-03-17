# GraphRAG for Python — neo4j-graphrag-python Documentation

This package contains the official Neo4j GraphRAG features for Python.

The purpose of this package is to provide a first party package to developers, where Neo4j can guarantee long term commitment and maintenance as well as being fast to ship new features and high performing patterns and methods.

⚠️ This package is a renamed continuation of neo4j-genai. The package neo4j-genai is deprecated and will no longer be maintained. We encourage all users to migrate to this new package to continue receiving updates and support.

## Neo4j Versions Supported

* Neo4j >=5.18.1
* Neo4j Aura >=5.18.0

## Python Versions Supported

* Python 3.12
* Python 3.11
* Python 3.10
* Python 3.9

## Topics

* [User Guide: RAG](./user_guide_rag.md#user-guide-rag)
* [User Guide: Knowledge Graph Builder](./user_guide_kg_builder.md#user-guide-kg-builder)
* [User Guide: Pipeline](./user_guide_pipeline.md#user-guide-pipeline)
* [API Documentation](./api.md#api-documentation)
* [Types](./types.md#types-documentation)

## Usage

### Installation

This package requires Python (>=3.9).

To install the latest stable version, use:

```bash
pip install neo4j-graphrag
```

> **Note:** It is always recommended to install python packages for user space in a virtual environment.

### Optional Dependencies

Extra dependencies can be installed with:

```bash
pip install "neo4j-graphrag[openai]"
```

List of extra dependencies:

* LLM providers (at least one is required for RAG and KG Builder Pipeline):
  * **ollama**: LLMs from Ollama
  * **openai**: LLMs from OpenAI (including AzureOpenAI)
  * **google**: LLMs from Vertex AI
  * **cohere**: LLMs from Cohere
  * **anthropic**: LLMs from Anthropic
  * **mistralai**: LLMs from MistralAI
* **sentence-transformers**: to use embeddings from the sentence-transformers Python package
* Vector database (to use [External Retrievers](./api.md#external-retrievers)):
  * **weaviate**: store vectors in Weaviate
  * **pinecone**: store vectors in Pinecone
  * **qdrant**: store vectors in Qdrant
* **experimental**: experimental features mainly from the Knowledge Graph creation pipelines.
  * **Warning:** this requires pygraphviz. Installation instructions can be found [here](https://pygraphviz.github.io/documentation/stable/install.html).

## Examples

### Creating a Vector Index

When creating a vector index, make sure you match the number of dimensions in the index with the number of dimensions the embeddings have.

See [the API documentation](./api.md#create-vector-index) for more details.

```python
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_vector_index

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

INDEX_NAME = "vector-index-name"

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Creating the index
create_vector_index(
    driver,
    INDEX_NAME,
    label="Document",
    embedding_property="vectorProperty",
    dimensions=1536,
    similarity_fn="euclidean",
)
```

> **Note:** Assumed Neo4j is running

### Populating the Neo4j Vector Index

Note that the below example is not the only way you can upsert data into your Neo4j database. For example, you could also leverage [the Neo4j Python driver](https://github.com/neo4j/neo4j-python-driver).

```python
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import upsert_vectors
from neo4j_graphrag.types import EntityType

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Upsert the vector
vector = ...
upsert_vectors(
    driver,
    ids=["1234"],
    embedding_property="vectorProperty",
    embeddings=[vector],
    entity_type=EntityType.NODE,
)
```

> **Note:** Assumed Neo4j is running with a defined vector index

### Performing a Similarity Search

While the library has more retrievers than shown here, the following examples should be able to get you started.

```python
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.retrievers import VectorRetriever

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

INDEX_NAME = "vector-index-name"

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Create Embedder object
# Note: An OPENAI_API_KEY environment variable is required here
embedder = OpenAIEmbeddings(model="text-embedding-3-large")

# Initialize the retriever
retriever = VectorRetriever(driver, INDEX_NAME, embedder)

# Run the similarity search
query_text = "How do I do similarity search in Neo4j?"
response = retriever.search(query_text=query_text, top_k=5)
```

> **Note:** Assumed Neo4j is running with populated vector index in place.

## Limitations

The query over the vector index is an _approximate_ nearest neighbor search and may not give exact results. [See this reference for more details](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/#limitations-and-issues).

## Development

### Install Dependencies

```bash
poetry install --all-extras
```

### Getting Started

#### Issues

If you have a bug to report or feature to request, first [search to see if an issue already exists](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-issues-and-pull-requests#search-by-the-title-body-or-comments). If a related issue doesn't exist, please raise a new issue using the relevant [issue form](https://github.com/neo4j/neo4j-graphrag-python/issues/new/choose).

If you're a Neo4j Enterprise customer, you can also reach out to [Customer Support](http://support.neo4j.com/).

If you don't have a bug to report or feature request, but you need a hand with the library; community support is available via [Neo4j Online Community](https://community.neo4j.com/) and/or [Discord](https://discord.gg/neo4j).

#### Make Changes

1. Fork the repository.
2. Install Python and Poetry.
3. Create a working branch from main and start with your changes!

#### Pull Request

When you're finished with your changes, create a pull request, also known as a PR.

* Ensure that you have [signed the CLA](https://neo4j.com/developer/contributing-code/#sign-cla).
* Ensure that the base of your PR is set to main.
* Don't forget to [link your PR to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) if you are solving one.
* Enable the checkbox to [allow maintainer edits](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork) so that maintainers can make any necessary tweaks and update your branch for merge.
* Reviewers may ask for changes to be made before a PR can be merged, either using [suggested changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/incorporating-feedback-in-your-pull-request) or normal pull request comments. You can apply suggested changes directly through the UI, and any other changes can be made in your fork and committed to the PR branch.
* As you update your PR and apply changes, mark each conversation as [resolved](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/commenting-on-a-pull-request#resolving-conversations).

### Run Tests

Open a new virtual environment and then run the tests.

#### Unit Tests

This should run out of the box once the dependencies are installed.

```bash
poetry run pytest tests/unit
```

#### E2E Tests

To run e2e tests you'd need to have some services running locally:

* neo4j
* weaviate
* weaviate-text2vec-transformers

The easiest way to get it up and running is via Docker compose:

```bash
docker compose -f tests/e2e/docker-compose.yml up
```

> **Note:** If you suspect something in the databases are cached, run `docker compose -f tests/e2e/docker-compose.yml down` to remove them completely

Once the services are running, execute the following command to run the e2e tests.

```bash
poetry run pytest tests/e2e
```

## Further Information

* [The official Neo4j Python driver](https://github.com/neo4j/neo4j-python-driver)
* [Neo4j GenAI integrations](https://neo4j.com/docs/cypher-manual/current/genai-integrations/)
