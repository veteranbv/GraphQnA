"""Example domain configuration file.

Copy this file to domain_config.py and customize for your knowledge domain.
This file defines domain-specific settings, entities, relationships, and prompts.
"""

from typing import Dict, List

# Domain metadata
DOMAIN_NAME = "YourDomain"
DOMAIN_DESCRIPTION = "A knowledge graph for YourDomain documentation"

# Entity definitions for the knowledge graph
ENTITY_DEFINITIONS = [
    {
        "label": "Feature",
        "description": "A product feature or capability",
        "properties": [
            {"name": "name", "type": "STRING"},
            {"name": "description", "type": "STRING"},
            {"name": "category", "type": "STRING"},
        ],
    },
    {
        "label": "Process",
        "description": "A business process or workflow",
        "properties": [
            {"name": "name", "type": "STRING"},
            {"name": "description", "type": "STRING"},
            {"name": "frequency", "type": "STRING"},
        ],
    },
    {
        "label": "Task",
        "description": "A specific task that users perform",
        "properties": [
            {"name": "name", "type": "STRING"},
            {"name": "description", "type": "STRING"},
            {"name": "importance", "type": "STRING"},
        ],
    },
    {
        "label": "Role",
        "description": "A user role or job function",
        "properties": [
            {"name": "name", "type": "STRING"},
            {"name": "description", "type": "STRING"},
            {"name": "responsibilities", "type": "STRING"},
        ],
    },
    {
        "label": "Category",
        "description": "A category of functionality",
        "properties": [
            {"name": "name", "type": "STRING"},
            {"name": "description", "type": "STRING"},
        ],
    },
]

# Relationship definitions for the knowledge graph
RELATION_DEFINITIONS = [
    {
        "label": "HAS_STEP",
        "description": "A process has a step or sub-process",
        "properties": [{"name": "order", "type": "STRING"}],
    },
    {
        "label": "REQUIRES",
        "description": "An entity requires another entity",
        "properties": [{"name": "reason", "type": "STRING"}],
    },
    {
        "label": "PERFORMED_BY",
        "description": "A task is performed by a role",
        "properties": [{"name": "frequency", "type": "STRING"}],
    },
    {
        "label": "PART_OF",
        "description": "An entity is part of another entity",
        "properties": [],
    },
    {
        "label": "APPLICABLE_TO",
        "description": "A concept is applicable to a specific scenario",
        "properties": [
            {"name": "suitability", "type": "STRING"},
            {"name": "priority", "type": "STRING"},
        ],
    },
]

# Schema triplets (valid combinations of entities and relationships)
SCHEMA_TRIPLETS = [
    ["Process", "HAS_STEP", "Task"],
    ["Process", "HAS_STEP", "Process"],
    ["Feature", "REQUIRES", "Feature"],
    ["Task", "REQUIRES", "Feature"],
    ["Process", "REQUIRES", "Feature"],
    ["Task", "PERFORMED_BY", "Role"],
    ["Feature", "PART_OF", "Feature"],
    ["Task", "PART_OF", "Process"],
    ["Category", "APPLICABLE_TO", "Feature"],
    ["Role", "PART_OF", "Category"],
]

# Default entity types/labels
DEFAULT_NODE_LABELS = [
    "Document", "Chunk", "Feature", "Process", "Task",
    "Role", "Category", "ActivityType"
]

# Default relationship types
DEFAULT_RELATIONSHIP_TYPES = [
    "PART_OF_DOCUMENT", "NEXT_CHUNK", "FROM_CHUNK",
    "HAS_STEP", "REQUIRES", "PERFORMED_BY", "PART_OF",
    "APPLICABLE_TO"
]

# Response templates for consistent messaging
RESPONSE_TEMPLATES = {
    "not_applicable": "Not applicable: This information is not available in the {domain_name} knowledge base.",
    "verify_info": "Please verify this information in the {domain_name} documentation for the most up-to-date details.",
    "insufficient_info": "I don't have enough information about this in the {domain_name} knowledge base."
}

# Fallback queries for when the LLM-generated query fails
FALLBACK_QUERIES = {
    "default": "MATCH (n) RETURN n.name, n.description LIMIT 10",
    "activity_types": "MATCH (a:ActivityType) RETURN a.name, a.description, a.category",
    "roles": "MATCH (r:Role) RETURN r.name, r.description",
    "processes": "MATCH (p:Process) RETURN p.name, p.description",
    "features": "MATCH (f:Feature) RETURN f.name, f.description, f.category"
}

# Fallback schema for knowledge graph when schema detection fails
FALLBACK_SCHEMA = """
Node properties:
Feature {name: STRING, description: STRING, category: STRING}
Process {name: STRING, description: STRING}
Task {name: STRING, description: STRING}
Role {name: STRING, description: STRING}
ActivityType {name: STRING, category: STRING, description: STRING}
Scenario {name: STRING, description: STRING}
Chunk {text: STRING, index: INTEGER}

The relationships:
(:Process)-[:HAS_STEP]->(:Task)
(:Feature)-[:REQUIRES]->(:Feature)
(:Task)-[:PERFORMED_BY]->(:Role)
(:Feature)-[:PART_OF]->(:Feature)
(:Chunk)-[:NEXT_CHUNK]->(:Chunk)
(:Entity)-[:FROM_CHUNK]->(:Chunk)
"""

# Prompts for knowledge graph extraction, query generation, and answer generation
PROMPTS = {
    # Enhanced KG Retriever prompts
    "kg_cypher_generation": """
        You are an expert in writing Cypher queries for Neo4j and a knowledge assistant for {domain_name}.

        Your task is to convert the user's question into a Cypher query that queries a Neo4j database of {domain_name} knowledge.

        The knowledge graph has the following node types:
        {node_labels_str}

        Relationship types include:
        {rel_types_str}

        This is a specialized domain for {domain_name}. Questions will be related to:
        - Features and capabilities
        - Processes and workflows
        - Tasks that users can perform
        - Roles and responsibilities
        - Categories of functionality

        Example Cypher queries:

        Question: What features are available in the product?
        Cypher: MATCH (f:Feature) RETURN f.name, f.description, f.category

        Question: What are the different steps in the onboarding process?
        Cypher: MATCH (p:Process {{name: "Onboarding"}})-[:HAS_STEP]->(s) RETURN s.name, s.description ORDER BY s.index

        Question: Which roles can perform administration tasks?
        Cypher: MATCH (t:Task)-[:PERFORMED_BY]->(r:Role) WHERE toLower(t.name) CONTAINS "admin" OR toLower(t.description) CONTAINS "admin" RETURN t.name, r.name, r.description

        IMPORTANT: Generate a Cypher query that would find the answer to the user's question.
        ONLY output the Cypher query without any explanation.
        Focus on querying specific entity types rather than text chunks when possible.
        Always start your query with a valid Cypher keyword like MATCH, RETURN, CALL, or CREATE.
        If you don't know how to convert the question to a Cypher query, respond with "UNKNOWN".

        Question: {query}

        Cypher Query:
    """,
    
    "kg_answer_generation": """
        Use the following knowledge graph query results to answer the question.

        Question: {query}

        {context}

        Answer the question based on the provided information. If the information doesn't directly answer the question,
        say "Not applicable: This information is not available in the {domain_name} knowledge base."

        End with: "Please verify this information in the {domain_name} documentation for the most up-to-date details."
    """,
    
    # Knowledge Graph Schema Detection prompt
    "schema_detection": """
        You are an expert in schema extraction, especially for extracting graph schema information 
        from various formats. Generate the generalized graph schema based on input text. 
        Identify key entities and their relationships and provide a generalized label for the 
        overall context. Only return the string types for nodes and relationships. 
        Don't return attributes.

        IMPORTANT RULES:
        1. Node labels MUST be in PascalCase with no spaces (e.g., 'Person', 'SalesProcess', not 'Sales Process')
        2. Relationship types MUST be in UPPER_SNAKE_CASE with no spaces (e.g., 'WORKS_FOR', not 'Works For')
        3. Do not use multi-word labels with spaces
    """,
    
    # Knowledge Graph Extraction prompt
    "kg_extraction": """# Knowledge Graph Extraction

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
    """,
    
    # Query Classification prompt
    "query_classification": """
        Classify this question into exactly one of these types:
        - factual: Seeking basic information or facts (e.g., "What is {domain_name}?")
        - procedural: Asking how to do something (e.g., "How do I create a report?")
        - entity: Asking about specific entities, their attributes, or types (e.g., "What features are available?")
        - relationship: Asking about relationships between entities (e.g., "Which roles can perform X?")
        
        Question: {query}
        
        Classification (just respond with one word from the list above):
    """,
    
    # Not applicable response template
    "not_applicable": "Not applicable: This information is not available in the {domain_name} knowledge base. Please verify this information in the {domain_name} documentation for the most up-to-date details.",
}

# Example queries for each type - used in documentation and testing
EXAMPLE_QUERIES = {
    "factual": [
        "What is {domain_name}?",
        "What are the main features of {domain_name}?",
        "When was {domain_name} launched?",
    ],
    "procedural": [
        "How do I create a new project?",
        "What's the process for creating a report?",
        "How can I invite team members?",
    ],
    "entity": [
        "What types of reports are available?",
        "What features are included in the premium plan?",
        "What user roles exist in the system?",
    ],
    "relationship": [
        "Which roles can create projects?",
        "What features are required for reporting?",
        "Who has access to admin settings?",
    ],
}

# Example Cypher queries for different query types
EXAMPLE_CYPHER_QUERIES = {
    "entity": [
        ("What features are available?", "MATCH (f:Feature) RETURN f.name, f.description, f.category"),
        ("What user roles exist in the system?", "MATCH (r:Role) RETURN r.name, r.description"),
    ],
    "relationship": [
        ("Which roles can create projects?", "MATCH (t:Task {name: 'Create Project'})-[:PERFORMED_BY]->(r:Role) RETURN r.name, r.description"),
        ("What features are required for reporting?", "MATCH (f:Feature {category: 'Reporting'})-[:REQUIRES]->(r:Feature) RETURN f.name, r.name, r.description"),
    ],
}