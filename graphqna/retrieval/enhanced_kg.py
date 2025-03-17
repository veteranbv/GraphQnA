"""Enhanced knowledge graph retrieval for question answering."""

import logging
import time
from typing import Any, Dict, List, Optional, Union, Tuple

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.response import QueryResponse, KnowledgeGraphQueryResult
from graphqna.models.entity import Entity, Relationship
from graphqna.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)


class EnhancedKGRetriever(BaseRetriever):
    """
    Enhanced knowledge graph retriever for direct cypher generation.

    This retriever dynamically discovers the entities and relationships in the database
    and then converts natural language questions into Cypher queries using this schema.
    """

    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None,
        **kwargs
    ):
        """
        Initialize the enhanced knowledge graph retriever.

        Args:
            db: Neo4j database connection (optional)
            settings: Application settings (optional)
            **kwargs: Additional keyword arguments passed to the parent class
        """
        super().__init__(db=db, settings=settings, **kwargs)

        # Initialize LLM for cypher generation
        self.llm = ChatOpenAI(
            model=self.settings.llm.model,
            api_key=self.settings.llm.api_key,
            temperature=0.0,  # Use low temperature for deterministic cypher generation
        )

        # Discover the database schema
        # Load domain-specific settings
        self.domain_name = self.settings.domain_name
        self.domain_prompts = self.settings.domain_prompts
        
        # Get node labels and relationship types from the database or fallback to defaults
        self.node_labels = self._get_node_labels()
        self.relationship_types = self._get_relationship_types()

        logger.info(f"Discovered {len(self.node_labels)} node labels and {len(self.relationship_types)} relationship types")

    def _get_node_labels(self) -> List[str]:
        """
        Get all node labels from the database.

        Returns:
            List of node labels
        """
        try:
            with self.db.session() as session:
                result = session.run("CALL db.labels()")
                return [record["label"] for record in result.data()]
        except Exception as e:
            logger.error(f"Error getting node labels: {str(e)}")
            # Use domain-specific default labels from settings
            return self.settings.default_node_labels

    def _get_relationship_types(self) -> List[str]:
        """
        Get all relationship types from the database.

        Returns:
            List of relationship types
        """
        try:
            with self.db.session() as session:
                result = session.run("CALL db.relationshipTypes()")
                return [record["relationshipType"] for record in result.data()]
        except Exception as e:
            logger.error(f"Error getting relationship types: {str(e)}")
            # Use domain-specific default relationship types from settings
            return self.settings.default_relationship_types

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information from the knowledge graph using Cypher.

        Args:
            query: The query text
            top_k: Number of results to retrieve (not used here, included for API compatibility)
            **kwargs: Additional keyword arguments

        Returns:
            List of retrieved data
        """
        # Generate a Cypher query
        cypher = self._generate_cypher(query)

        if not cypher or cypher.strip() == "UNKNOWN":
            logger.warning(f"Could not generate Cypher query for: {query}")
            return []

        # Execute the Cypher query against Neo4j
        try:
            return self._execute_cypher(cypher)
        except Exception as e:
            logger.error(f"Error executing Cypher query: {str(e)}")
            logger.error(f"Generated query: {cypher}")
            return []

    def _generate_cypher(self, query: str) -> str:
        """
        Generate a Cypher query from a natural language query.

        Args:
            query: Natural language query

        Returns:
            str: Cypher query or UNKNOWN if generation fails
        """
        try:
            # Filter out system node labels
            filtered_labels = [
                label for label in self.node_labels
                if label not in ["Chunk", "Document"] and not label.startswith("__")
            ]

            # Filter out system relationship types
            filtered_rel_types = [
                rel_type for rel_type in self.relationship_types
                if not rel_type.startswith("__")
            ]

            # Format node labels and relationship types for the prompt
            node_labels_str = ", ".join([f"(:{label})" for label in filtered_labels])
            rel_types_str = ", ".join([f"-[:{rel_type}]->" for rel_type in filtered_rel_types])

            # Get the cypher generation prompt from domain_prompts
            if "kg_cypher_generation" in self.domain_prompts:
                prompt_template = self.domain_prompts["kg_cypher_generation"]
            else:
                # Fallback to a basic prompt if not defined in domain config
                prompt_template = """
                You are an expert in writing Cypher queries for Neo4j and a knowledge assistant.
                
                Your task is to convert the user's question into a Cypher query that queries a Neo4j database of knowledge.
                
                The knowledge graph has the following node types:
                {node_labels_str}
                
                Relationship types include:
                {rel_types_str}
                
                IMPORTANT: Generate a Cypher query that would find the answer to the user's question.
                ONLY output the Cypher query without any explanation.
                Always start your query with a valid Cypher keyword like MATCH, RETURN, CALL, or CREATE.
                If you don't know how to convert the question to a Cypher query, respond with "UNKNOWN".
                
                Question: {query}
                
                Cypher Query:
                """
            
            # Format the prompt template with context
            prompt = prompt_template.format(
                domain_name=self.domain_name,
                node_labels_str=node_labels_str,
                rel_types_str=rel_types_str,
                query=query
            )

            # Generate the cypher query
            result = self.llm.invoke(prompt)
            cypher = result.content.strip()

            # Remove any markdown code block markers
            if cypher.startswith("```cypher"):
                cypher = cypher[8:]
            if cypher.startswith("```"):
                cypher = cypher[3:]
            if cypher.endswith("```"):
                cypher = cypher[:-3]

            # Clean and validate the query
            return self._clean_and_validate_cypher(cypher.strip())
        except Exception as e:
            logger.error(f"Error generating Cypher query: {str(e)}")
            return self._build_fallback_query(query)

    def _clean_and_validate_cypher(self, cypher: str) -> str:
        """
        Clean and validate a Cypher query.
        
        Args:
            cypher: The Cypher query to clean and validate
            
        Returns:
            str: Cleaned and validated Cypher query or fallback
        """
        # Check if the query is valid
        if not cypher or cypher == "UNKNOWN":
            return "UNKNOWN"
        
        # Remove any 'r' prefix that might be added erroneously
        if cypher.startswith('r') and len(cypher) > 1 and not cypher.lower().startswith('return'):
            cypher = cypher[1:].strip()
        
        # Check if the query starts with a valid Cypher clause
        valid_starts = ["MATCH", "RETURN", "WITH", "CALL", "CREATE", "MERGE", "OPTIONAL"]
        if not any(cypher.upper().startswith(start) for start in valid_starts):
            logger.warning(f"Invalid Cypher query: {cypher}")
            return "UNKNOWN"
        
        return cypher
    
    def _build_fallback_query(self, query: str) -> str:
        """
        Build a fallback query based on keywords in the user query.
        
        Args:
            query: The original user query
            
        Returns:
            str: A simple Cypher query based on keywords
        """
        # Extract keywords from the query
        keywords = self._extract_keywords(query)
        
        # Use domain config fallback queries if available
        fallback_queries = {}
        if hasattr(self.settings, 'fallback_queries'):
            fallback_queries = self.settings.fallback_queries
        else:
            # Backward compatibility
            fallback_queries = self.domain_prompts.get("fallback_queries", {
                "default": "MATCH (n) RETURN n.name, n.description LIMIT 10",
                "activity_types": "MATCH (a:ActivityType) RETURN a.name, a.description, a.category",
                "roles": "MATCH (r:Role) RETURN r.name, r.description",
                "processes": "MATCH (p:Process) RETURN p.name, p.description"
            })
        
        if not keywords:
            # Default query if no keywords found
            return fallback_queries.get("default", "MATCH (n) RETURN n.name, n.description LIMIT 10")
        
        # Look for activity type keywords
        activity_keywords = [k for k in keywords if k in ["activity", "activities", "type", "types", "task", "category"]]
        if activity_keywords:
            return fallback_queries.get("activity_types", "MATCH (a:ActivityType) RETURN a.name, a.description, a.category")
        
        # Look for role keywords
        role_keywords = [k for k in keywords if k in ["role", "roles", "person", "user", "perform"]]
        if role_keywords:
            return fallback_queries.get("roles", "MATCH (r:Role) RETURN r.name, r.description")
        
        # Look for process keywords
        process_keywords = [k for k in keywords if k in ["process", "stage", "workflow", "steps", "procedure"]]
        if process_keywords:
            return fallback_queries.get("processes", "MATCH (p:Process) RETURN p.name, p.description")
        
        # Look for specific entity related to the query
        conditions = " OR ".join([f"toLower(n.name) CONTAINS '{k}' OR toLower(n.description) CONTAINS '{k}'" for k in keywords])
        return f"MATCH (n) WHERE {conditions} RETURN n.name, labels(n) as type, n.description LIMIT 10"
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract relevant keywords from a query.
        
        Args:
            query: The query to extract keywords from
            
        Returns:
            List[str]: List of keywords
        """
        # Convert to lowercase
        text = query.lower()
        
        # Remove stopwords
        stopwords = ["a", "an", "the", "in", "on", "at", "by", "for", "with", "about", "to", "of", "is", "are", "what", "who", "when", "where", "why", "how", "which", "should", "would", "could", "and", "or", "but", "if", "then", "that", "this", "these", "those"]
        
        # Split into words and filter out stopwords and short words
        words = [word.strip('.,?!()[]{}":;') for word in text.split()]
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords

    def _execute_cypher(self, cypher: str) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.

        Args:
            cypher: Cypher query to execute

        Returns:
            List of query results as dictionaries
        """
        try:
            with self.db.session() as session:
                result = session.run(cypher)
                return result.data()
        except Exception as e:
            logger.error(f"Error executing Cypher query: {str(e)}")
            raise

    def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using knowledge graph retrieval.

        Args:
            query: The question to answer
            top_k: Number of results to retrieve (unused, for API compatibility)
            **kwargs: Additional keyword arguments

        Returns:
            QueryResponse with answer and context
        """
        start_time = time.time()

        try:
            # Generate a Cypher query
            cypher = self._generate_cypher(query)

            if not cypher or cypher.strip() == "UNKNOWN":
                # Get domain-specific "not applicable" message
                not_applicable_msg = self.domain_prompts.get(
                    "not_applicable", 
                    f"Not applicable: This information is not available in the {self.domain_name} knowledge base. Please verify this information in the {self.domain_name} documentation for the most up-to-date details."
                )
                
                # Format the message with domain name
                not_applicable_msg = not_applicable_msg.format(domain_name=self.domain_name)
                
                # Fall back to a generic response
                return QueryResponse(
                    query=query,
                    answer=not_applicable_msg,
                    retrieval_method="kg",
                    query_time=time.time() - start_time,
                    context=KnowledgeGraphQueryResult(
                        query="",
                        entities=[],
                        relationships=[],
                        raw_results=[]
                    ),
                    metadata={"cypher": "UNKNOWN"},
                )

            # Execute the query and get results
            results = self._execute_cypher(cypher)

            # Generate answer from results
            answer = self._generate_answer(query, results, cypher)

            # Extract entities from results
            entities, relationships = self._extract_entities_from_results(results)

            # Create KG query result
            kg_result = KnowledgeGraphQueryResult(
                query=cypher,
                entities=entities,
                relationships=relationships,
                raw_results=results
            )

            # Track response time
            response_time = time.time() - start_time

            return QueryResponse(
                query=query,
                answer=answer,
                retrieval_method="kg",
                query_time=response_time,
                context=kg_result,
                metadata={"cypher": cypher, "results": results},
            )
        except Exception as e:
            logger.error(f"Error in KG retrieval: {str(e)}")

            # Calculate response time even for errors
            response_time = time.time() - start_time

            # Get domain-specific "not applicable" message
            not_applicable_msg = self.domain_prompts.get(
                "not_applicable", 
                f"Not applicable: This information is not available in the {self.domain_name} knowledge base. Please verify this information in the {self.domain_name} documentation for the most up-to-date details."
            )
            
            # Format the message with domain name
            not_applicable_msg = not_applicable_msg.format(domain_name=self.domain_name)
            
            # Return a generic error response
            return QueryResponse(
                query=query,
                answer=not_applicable_msg,
                retrieval_method="kg",
                query_time=response_time,
                context=KnowledgeGraphQueryResult(
                    query=cypher if 'cypher' in locals() else "",
                    entities=[],
                    relationships=[],
                    raw_results=[]
                ),
                metadata={"error": str(e)},
            )

    def _extract_entities_from_results(self, results: List[Dict[str, Any]]) -> Tuple[List[Entity], List[Relationship]]:
        """
        Extract entities and relationships from query results.

        Args:
            results: Results from Cypher query

        Returns:
            Tuple of (entities, relationships)
        """
        entities = []
        relationships = []

        # Process each result to extract entities
        for result in results:
            for key, value in result.items():
                if isinstance(value, dict) and "properties" in value:
                    # This looks like a node
                    entity = Entity(
                        labels=[value.get("label", "Entity")],
                        properties=value.get("properties", {}),
                        node_id=value.get("id")
                    )
                    entities.append(entity)
                elif isinstance(value, str) and key.endswith("name"):
                    # Try to create an entity from a name property
                    entity = Entity(
                        labels=[key.replace("name", "").capitalize() or "Entity"],
                        properties={"name": value},
                        node_id=None
                    )
                    entities.append(entity)

        return entities, relationships

    def _generate_answer(
        self,
        query: str,
        results: List[Dict[str, Any]],
        cypher: str,
    ) -> str:
        """
        Generate an answer based on Cypher query results.

        Args:
            query: Original query
            results: Results from Cypher query
            cypher: Executed Cypher query

        Returns:
            str: Generated answer
        """
        # If no results, return the domain-specific "not applicable" message
        if not results:
            if "not_applicable" in self.domain_prompts:
                return self.domain_prompts["not_applicable"].format(domain_name=self.domain_name)
            else:
                return f"Not applicable: This information is not available in the {self.domain_name} knowledge base. Please verify this information in the {self.domain_name} documentation for the most up-to-date details."

        # Build the context for the LLM
        context = "Knowledge Graph Results:\n"

        # Format results as JSON-like text
        for i, record in enumerate(results[:10]):  # Limit to first 10 results
            context += f"Result {i+1}:\n"
            for key, value in record.items():
                context += f"  {key}: {value}\n"
            context += "\n"

        # Get the answer generation prompt from domain_prompts
        if "kg_answer_generation" in self.domain_prompts:
            prompt_template = self.domain_prompts["kg_answer_generation"]
        else:
            # Fallback to a basic prompt if not defined in domain config
            prompt_template = """
            Use the following knowledge graph query results to answer the question.

            Question: {query}

            {context}

            Answer the question based on the provided information. If the information doesn't directly answer the question,
            say "Not applicable: This information is not available in the {domain_name} knowledge base."

            End with: "Please verify this information in the {domain_name} documentation for the most up-to-date details."
            """
            
        # Format the prompt template with context
        prompt = prompt_template.format(
            domain_name=self.domain_name,
            query=query,
            context=context
        )

        # Generate answer with LLM
        try:
            answer = self.llm.invoke(prompt)
            return answer.content.strip()
        except Exception as e:
            logger.error(f"Error generating answer from KG results: {str(e)}")
            # Use domain-specific "not applicable" message for errors
            if "not_applicable" in self.domain_prompts:
                return self.domain_prompts["not_applicable"].format(domain_name=self.domain_name)
            else:
                return f"Not applicable: This information is not available in the {self.domain_name} knowledge base. Please verify this information in the {self.domain_name} documentation for the most up-to-date details."