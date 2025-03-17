"""Settings management for GraphQnA using dependency injection pattern."""

import os
import importlib.util
import sys
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Import domain configuration
# First check if the domain_config.py file exists
domain_config_path = Path(__file__).parent / "domain_config.py"
domain_config_example_path = Path(__file__).parent / "domain_config_example.py"

# Import the appropriate configuration module
if domain_config_path.exists():
    try:
        spec = importlib.util.spec_from_file_location("domain_config", domain_config_path)
        domain_config = importlib.util.module_from_spec(spec)
        sys.modules["domain_config"] = domain_config
        spec.loader.exec_module(domain_config)
    except Exception as e:
        # Fallback to the example config if there's an error
        print(f"Error loading domain_config.py: {str(e)}. Falling back to example config.")
        spec = importlib.util.spec_from_file_location("domain_config_example", domain_config_example_path)
        domain_config = importlib.util.module_from_spec(spec)
        sys.modules["domain_config_example"] = domain_config
        spec.loader.exec_module(domain_config)
else:
    # Use the example config if the domain_config.py doesn't exist
    spec = importlib.util.spec_from_file_location("domain_config_example", domain_config_example_path)
    domain_config = importlib.util.module_from_spec(spec)
    sys.modules["domain_config_example"] = domain_config
    spec.loader.exec_module(domain_config)


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Neo4jSettings(BaseModel):
    """Neo4j connection settings."""

    uri: str = Field(..., description="Neo4j connection URI")
    username: str = Field(..., description="Neo4j username")
    password: str = Field(..., description="Neo4j password")
    database: str = Field("neo4j", description="Neo4j database name")


class LLMSettings(BaseModel):
    """LLM settings."""

    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field("gpt-4o", description="LLM model name")
    embedding_model: str = Field(
        "text-embedding-3-large", description="Embedding model name"
    )
    temperature: float = Field(0.0, description="LLM temperature")
    max_tokens: int = Field(2000, description="Maximum tokens for LLM response")


class VectorSettings(BaseModel):
    """Vector index settings."""

    index_name: str = Field("document-chunks", description="Vector index name")
    embedding_property: str = Field("embedding", description="Embedding property name")
    dimensions: int = Field(1536, description="Embedding dimensions")
    similarity_function: str = Field("cosine", description="Similarity function")


class ChunkSettings(BaseModel):
    """Chunking settings."""

    chunk_size: int = Field(1000, description="Chunk size")
    chunk_overlap: int = Field(200, description="Chunk overlap")
    vector_top_k: int = Field(5, description="Number of chunks to retrieve")


class GraphSettings(BaseModel):
    """Knowledge graph settings."""

    document_label: str = Field("Document", description="Document node label")
    chunk_label: str = Field("Chunk", description="Chunk node label")
    entity_base_label: str = Field("Entity", description="Base entity label")
    next_chunk_rel: str = Field("NEXT_CHUNK", description="Next chunk relationship")
    part_of_document_rel: str = Field(
        "PART_OF_DOCUMENT", description="Part of document relationship"
    )
    from_chunk_rel: str = Field("FROM_CHUNK", description="From chunk relationship")


class Settings(BaseModel):
    """Application settings."""

    # Paths
    base_dir: Path = Field(default=BASE_DIR)
    data_dir: Path = Field(default=DATA_DIR)
    output_dir: Path = Field(default=OUTPUT_DIR)
    logs_dir: Path = Field(default=LOGS_DIR)

    # Neo4j
    neo4j: Neo4jSettings = Field(
        default_factory=lambda: Neo4jSettings(
            uri=os.getenv("NEO4J_URI", ""),
            username=os.getenv("NEO4J_USERNAME", ""),
            password=os.getenv("NEO4J_PASSWORD", ""),
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
        )
    )

    # LLM
    llm: LLMSettings = Field(
        default_factory=lambda: LLMSettings(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
        )
    )

    # Vector
    vector: VectorSettings = Field(
        default_factory=lambda: VectorSettings(
            index_name=os.getenv("VECTOR_INDEX_NAME", "document-chunks"),
            embedding_property=os.getenv("EMBEDDING_PROPERTY", "embedding"),
            dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
            similarity_function=os.getenv("SIMILARITY_FUNCTION", "cosine"),
        )
    )

    # Chunking
    chunking: ChunkSettings = Field(
        default_factory=lambda: ChunkSettings(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            vector_top_k=int(os.getenv("VECTOR_TOP_K", "5")),
        )
    )

    # Graph
    graph: GraphSettings = Field(default_factory=GraphSettings)

    # Logging
    log_level: LogLevel = Field(
        default=os.getenv("LOG_LEVEL", "INFO"), description="Log level"
    )

    # Domain metadata
    domain_name: str = Field(
        default=getattr(domain_config, "DOMAIN_NAME", "Knowledge Domain")
    )
    domain_description: str = Field(
        default=getattr(domain_config, "DOMAIN_DESCRIPTION", "A knowledge graph for documentation")
    )
    
    # Entity definitions from domain config
    entity_definitions: List[Dict] = Field(
        default=getattr(domain_config, "ENTITY_DEFINITIONS", [
            {
                "label": "Entity",
                "description": "A generic entity",
                "properties": [
                    {"name": "name", "type": "STRING"},
                    {"name": "description", "type": "STRING"},
                ],
            }
        ])
    )

    # Relation definitions from domain config
    relation_definitions: List[Dict] = Field(
        default=getattr(domain_config, "RELATION_DEFINITIONS", [
            {
                "label": "RELATES_TO",
                "description": "A generic relationship between entities",
                "properties": [],
            }
        ])
    )

    # Schema triplets from domain config
    schema_triplets: List[List[str]] = Field(
        default=getattr(domain_config, "SCHEMA_TRIPLETS", [
            ["Entity", "RELATES_TO", "Entity"]
        ])
    )
    
    # Domain-specific prompts
    domain_prompts: Dict = Field(
        default=getattr(domain_config, "PROMPTS", {})
    )
    
    # Example queries for documentation and testing
    example_queries: Dict = Field(
        default=getattr(domain_config, "EXAMPLE_QUERIES", {})
    )
    
    # Example Cypher queries
    example_cypher_queries: Dict = Field(
        default=getattr(domain_config, "EXAMPLE_CYPHER_QUERIES", {})
    )
    
    # Default node labels
    default_node_labels: List[str] = Field(
        default=getattr(domain_config, "DEFAULT_NODE_LABELS", ["Document", "Chunk", "Entity"])
    )
    
    # Default relationship types
    default_relationship_types: List[str] = Field(
        default=getattr(domain_config, "DEFAULT_RELATIONSHIP_TYPES", ["PART_OF_DOCUMENT", "NEXT_CHUNK", "RELATES_TO"])
    )
    
    # Response templates for consistent messaging
    response_templates: Dict[str, str] = Field(
        default=getattr(domain_config, "RESPONSE_TEMPLATES", {
            "not_applicable": "Not applicable: This information is not available in the {domain_name} knowledge base.",
            "verify_info": "Please verify this information in the {domain_name} documentation for the most up-to-date details.",
            "insufficient_info": "I don't have enough information about this in the {domain_name} knowledge base."
        })
    )
    
    # Fallback queries for when LLM-generated queries fail
    fallback_queries: Dict[str, str] = Field(
        default=getattr(domain_config, "FALLBACK_QUERIES", {
            "default": "MATCH (n) RETURN n.name, n.description LIMIT 10",
            "activity_types": "MATCH (a:ActivityType) RETURN a.name, a.description, a.category",
            "roles": "MATCH (r:Role) RETURN r.name, r.description",
            "processes": "MATCH (p:Process) RETURN p.name, p.description",
            "features": "MATCH (f:Feature) RETURN f.name, f.description, f.category"
        })
    )
    
    # Fallback schema for when schema detection fails
    fallback_schema: str = Field(
        default=getattr(domain_config, "FALLBACK_SCHEMA", """
            Node properties:
            Feature {name: STRING, description: STRING, category: STRING}
            Process {name: STRING, description: STRING}
            Task {name: STRING, description: STRING}
            Role {name: STRING, description: STRING}
            Chunk {text: STRING, index: INTEGER}
            
            The relationships:
            (:Process)-[:HAS_STEP]->(:Task)
            (:Feature)-[:REQUIRES]->(:Feature)
            (:Task)-[:PERFORMED_BY]->(:Role)
            (:Feature)-[:PART_OF]->(:Feature)
            (:Chunk)-[:NEXT_CHUNK]->(:Chunk)
        """)
    )

    @validator("neo4j")
    def validate_neo4j(cls, v):
        """Validate Neo4j settings."""
        if not v.uri:
            raise ValueError("NEO4J_URI is required")
        if not v.username:
            raise ValueError("NEO4J_USERNAME is required")
        if not v.password:
            raise ValueError("NEO4J_PASSWORD is required")
        return v

    @validator("llm")
    def validate_llm(cls, v):
        """Validate LLM settings."""
        if not v.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return v

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        validate_assignment = True


@lru_cache()
def get_settings() -> Settings:
    """Get application settings using dependency injection pattern."""
    return Settings()