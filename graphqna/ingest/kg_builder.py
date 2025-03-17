"""Knowledge graph builder with automated entity and relationship extraction."""

import logging
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from graphqna.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Property(BaseModel):
    """A single property consisting of key and value."""
    key: str = Field(..., description="Property key (use camelCase)")
    value: str = Field(..., description="Property value")


class Node(BaseModel):
    """Node in the knowledge graph."""
    id: str = Field(..., description="Node identifier (human-readable)")
    type: str = Field(..., description="Node label/type")
    properties: Optional[List[Property]] = Field(
        None, description="List of node properties"
    )


class Relationship(BaseModel):
    """Relationship in the knowledge graph."""
    source: Node = Field(..., description="Source node")
    target: Node = Field(..., description="Target node")
    type: str = Field(..., description="Relationship type")
    properties: Optional[List[Property]] = Field(
        None, description="List of relationship properties"
    )


class KnowledgeGraph(BaseModel):
    """Complete knowledge graph with nodes and relationships."""
    nodes: List[Node] = Field(
        ..., description="List of nodes in the knowledge graph")
    relationships: List[Relationship] = Field(
        ..., description="List of relationships in the knowledge graph"
    )


class Schema(BaseModel):
    """Knowledge Graph Schema."""
    labels: List[str] = Field(description="List of node labels or types in a graph schema")
    relationshipTypes: List[str] = Field(description="List of relationship types in a graph schema")


class KnowledgeGraphBuilder:
    """
    Automated knowledge graph builder using LLMs for entity and relationship extraction.
    
    This class extracts structured knowledge graph information from text using
    large language models, with or without a predefined schema.
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        model: str = "gpt-4o",
        temperature: float = 0.0,
    ):
        """
        Initialize the knowledge graph builder.
        
        Args:
            settings: Application settings
            model: LLM model to use
            temperature: Temperature for LLM generation
        """
        self.settings = settings or get_settings()
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            api_key=self.settings.llm.api_key,
            model=model,
            temperature=temperature,
        )
        
        # Load domain-specific settings
        self.domain_name = self.settings.domain_name
        self.domain_prompts = self.settings.domain_prompts
        
        # Default schema (empty means automatic extraction)
        self.schema = None
        
    def detect_schema(self, text: str) -> Schema:
        """
        Detect schema from text samples.
        
        Args:
            text: Text to analyze for schema detection
            
        Returns:
            Schema: Detected schema with labels and relationship types
        """
        # Get the schema detection prompt from domain_prompts
        if "schema_detection" in self.domain_prompts:
            system_prompt = self.domain_prompts["schema_detection"]
        else:
            # Fallback to a basic prompt if not defined in domain config
            system_prompt = (
                "You are an expert in schema extraction, especially for extracting graph schema information "
                "from various formats. Generate the generalized graph schema based on input text. "
                "Identify key entities and their relationships and provide a generalized label for the "
                "overall context. Only return the string types for nodes and relationships. "
                "Don't return attributes.\n\n"
                "IMPORTANT RULES:\n"
                "1. Node labels MUST be in PascalCase with no spaces (e.g., 'Person', 'SalesProcess', not 'Sales Process')\n"
                "2. Relationship types MUST be in UPPER_SNAKE_CASE with no spaces (e.g., 'WORKS_FOR', not 'Works For')\n"
                "3. Do not use multi-word labels with spaces"
            )
        
        user_prompt = f"Analyze this text and extract the schema for a knowledge graph:\n\n{text}"
        
        try:
            # Build messages for the LLM
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Invoke the LLM with structured output
            result = self.llm.with_structured_output(Schema).invoke(messages)
            
            # Format the labels and relationship types
            formatted_labels = [self._format_node_label(label) for label in result.labels]
            formatted_rel_types = [self._format_rel_type(rel_type) for rel_type in result.relationshipTypes]
            
            # Create a new schema with the formatted types
            formatted_schema = Schema(
                labels=formatted_labels,
                relationshipTypes=formatted_rel_types
            )
            
            self.schema = formatted_schema
            logger.info(f"Detected schema: Labels={formatted_schema.labels}, Relationships={formatted_schema.relationshipTypes}")
            return formatted_schema
        except Exception as e:
            logger.error(f"Error detecting schema: {str(e)}")
            # Return a minimal default schema
            return Schema(labels=["Entity"], relationshipTypes=["RELATES_TO"])
            
    def _format_node_label(self, label: str) -> str:
        """
        Format a node label to be Neo4j-compatible.
        
        Args:
            label: The node label to format
            
        Returns:
            str: Formatted node label
        """
        if ' ' in label:
            # Convert "Technical Sales Process" to "TechnicalSalesProcess"
            return ''.join(word.capitalize() for word in label.split())
        
        # Ensure the label starts with an uppercase letter
        if label and label[0].islower():
            return label[0].upper() + label[1:]
            
        return label
        
    def _format_rel_type(self, rel_type: str) -> str:
        """
        Format a relationship type to be Neo4j-compatible.
        
        Args:
            rel_type: The relationship type to format
            
        Returns:
            str: Formatted relationship type
        """
        if ' ' in rel_type:
            # Convert "Has Access Method" to "HAS_ACCESS_METHOD"
            return '_'.join(word.upper() for word in rel_type.split())
        
        # Ensure the relationship type is all uppercase
        return rel_type.upper()
    
    def extract_knowledge_graph(self, text: str, schema: Optional[Schema] = None) -> KnowledgeGraph:
        """
        Extract knowledge graph from text.
        
        Args:
            text: Text to extract knowledge graph from
            schema: Optional schema to guide extraction
            
        Returns:
            KnowledgeGraph: Extracted knowledge graph
        """
        # Use provided schema or the class instance schema
        schema_to_use = schema or self.schema
        
        # Build the system prompt
        system_prompt = self._build_extraction_prompt(schema_to_use)
        
        user_prompt = f"Extract a knowledge graph from this text:\n\n{text}"
        
        try:
            # Build messages for the LLM
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Invoke the LLM with structured output
            result = self.llm.with_structured_output(KnowledgeGraph).invoke(messages)
            
            logger.info(f"Extracted knowledge graph: {len(result.nodes)} nodes, {len(result.relationships)} relationships")
            return result
        except Exception as e:
            logger.error(f"Error extracting knowledge graph: {str(e)}")
            # Return an empty knowledge graph
            return KnowledgeGraph(nodes=[], relationships=[])
    
    def _build_extraction_prompt(self, schema: Optional[Schema] = None) -> str:
        """
        Build the prompt for knowledge graph extraction.
        
        Args:
            schema: Optional schema to include in the prompt
            
        Returns:
            str: System prompt for knowledge graph extraction
        """
        # Build schema guidance if schema is provided
        schema_guidance = ""
        if schema and schema.labels and schema.relationshipTypes:
            schema_guidance = (
                f"## Schema to follow:\n"
                f"Node Types: {', '.join(schema.labels)}\n"
                f"Relationship Types: {', '.join(schema.relationshipTypes)}\n\n"
                f"Strictly use these node and relationship types from the schema."
            )
        
        # Get the knowledge graph extraction prompt from domain_prompts
        if "kg_extraction" in self.domain_prompts:
            # Format the template with schema guidance
            return self.domain_prompts["kg_extraction"].format(
                domain_name=self.domain_name,
                schema_guidance=schema_guidance
            )
        else:
            # Fallback to a basic prompt if not defined in domain config
            return f"""# Knowledge Graph Extraction

You are a top-tier knowledge graph extraction system designed to create structured data from text.

## Guidelines:
1. **Nodes** represent entities and concepts.
   - Each node must have a type/label, ID, and optional properties
   - Node IDs should be human-readable identifiers found in the text
   - Use basic types for node labels (e.g., "Person", "Organization", "Event")
   - VERY IMPORTANT: Do not use spaces in node type names. Instead of "Technical Sales Process", use "TechnicalSalesProcess"
   - Always use PascalCase (camel case starting with capital letter) for node types

2. **Relationships** connect nodes
   - Each relationship has a source node, target node, type, and optional properties
   - Use clear relationship names (e.g., "WORKS_FOR", "LOCATED_IN")
   - Always use UPPER_SNAKE_CASE for relationship types

3. **Properties**
   - Use camelCase for property keys (e.g., "birthDate", "fullName")
   - Don't use escaped quotes within property values
   - Don't create separate nodes for dates or numbers - use them as properties

4. **Entity Consistency**
   - When the same entity is mentioned multiple times, use the most complete identifier
   - Resolve coreferences (e.g., "John", "he", "Mr. Smith" → use "John Smith" consistently)

{schema_guidance}

Make every effort to extract a rich, connected knowledge graph from the text.
REMEMBER: DO NOT use spaces in node or relationship type names!
"""

    def props_to_dict(self, props: Optional[List[Property]]) -> Dict[str, Any]:
        """
        Convert properties to a dictionary.
        
        Args:
            props: List of Property objects
            
        Returns:
            Dict: Properties as a dictionary
        """
        properties = {}
        if not props:
            return properties
            
        for p in props:
            # Format the key to camelCase if needed
            key = self._format_property_key(p.key)
            properties[key] = p.value
            
        return properties
    
    def _format_property_key(self, key: str) -> str:
        """
        Format property key to camelCase.
        
        Args:
            key: Property key to format
            
        Returns:
            str: Formatted property key
        """
        words = key.split()
        if not words:
            return key
            
        first_word = words[0].lower()
        capitalized_words = [word.capitalize() for word in words[1:]]
        return "".join([first_word] + capitalized_words)