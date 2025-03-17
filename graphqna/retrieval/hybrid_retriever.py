"""Hybrid retrieval orchestrator for combining multiple retrieval methods."""

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple

from langchain_openai import ChatOpenAI

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.response import QueryResponse
from graphqna.retrieval.base import BaseRetriever
from graphqna.retrieval.vector import VectorRetriever
from graphqna.retrieval.graph import GraphRetriever
from graphqna.retrieval.kg import KnowledgeGraphRetriever
from graphqna.retrieval.enhanced_kg import EnhancedKGRetriever

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of queries for classification."""
    
    FACTUAL = "factual"           # General factual query
    PROCEDURAL = "procedural"     # How-to queries
    ENTITY = "entity"             # Queries about specific entities
    RELATIONSHIP = "relationship" # Queries about relationships between entities


class QueryClassifier:
    """Classifies queries to determine the best retrieval method."""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the query classifier.
        
        Args:
            llm: LLM to use for classification (optional)
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()
        
        # Initialize LLM for classification
        self.llm = llm or ChatOpenAI(
            model=self.settings.llm.model,
            api_key=self.settings.llm.api_key,
            temperature=0.0,  # Use low temperature for deterministic classification
        )
        
        # Load domain-specific settings
        self.domain_name = self.settings.domain_name
        self.domain_prompts = self.settings.domain_prompts
        
    def classify(self, query: str) -> QueryType:
        """
        Determine query type to select the best retrieval method.
        
        Args:
            query: The query to classify
            
        Returns:
            QueryType: Classified query type
        """
        # Get the query classification prompt from domain_prompts
        if "query_classification" in self.domain_prompts:
            prompt_template = self.domain_prompts["query_classification"]
            # Format the template with query and domain name
            prompt = prompt_template.format(
                domain_name=self.domain_name,
                query=query
            )
        else:
            # Fallback to a basic prompt if not defined in domain config
            prompt = f"""
            Classify this question into exactly one of these types:
            - factual: Seeking basic information or facts (e.g., "What is {self.domain_name}?")
            - procedural: Asking how to do something (e.g., "How do I create a report?")
            - entity: Asking about specific entities, their attributes, or types (e.g., "What features are available?")
            - relationship: Asking about relationships between entities (e.g., "Which roles can perform X?")
            
            Question: {query}
            
            Classification (just respond with one word from the list above):
            """
        
        try:
            result = self.llm.invoke(prompt)
            response = result.content.strip().lower()
            
            # Match the response to a QueryType enum
            for query_type in QueryType:
                if query_type.value in response:
                    return query_type
                    
            # Default to factual if no match
            return QueryType.FACTUAL
        except Exception as e:
            logger.error(f"Error classifying query: {str(e)}")
            return QueryType.FACTUAL


class HybridRetriever(BaseRetriever):
    """Orchestrates multiple retrieval methods for optimal results."""
    
    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None,
        vector_retriever: Optional[VectorRetriever] = None,
        graph_retriever: Optional[GraphRetriever] = None,
        kg_retriever: Optional[KnowledgeGraphRetriever] = None,
        enhanced_kg_retriever: Optional[EnhancedKGRetriever] = None,
        classifier: Optional[QueryClassifier] = None,
        **kwargs
    ):
        """
        Initialize the hybrid retriever.
        
        Args:
            db: Neo4j database connection (optional)
            settings: Application settings (optional)
            vector_retriever: Vector retriever (optional)
            graph_retriever: GraphRAG retriever (optional)
            kg_retriever: Knowledge graph retriever (optional)
            enhanced_kg_retriever: Enhanced knowledge graph retriever (optional)
            classifier: Query classifier (optional)
            **kwargs: Additional keyword arguments passed to the parent class
        """
        super().__init__(db=db, settings=settings, **kwargs)
        
        # Load domain-specific settings
        self.domain_name = self.settings.domain_name
        self.domain_prompts = self.settings.domain_prompts
        
        # Initialize retrievers
        self.vector_retriever = vector_retriever or VectorRetriever(db=self.db, settings=self.settings)
        self.graph_retriever = graph_retriever or GraphRetriever(db=self.db, settings=self.settings)
        self.kg_retriever = kg_retriever or KnowledgeGraphRetriever(db=self.db, settings=self.settings)
        self.enhanced_kg_retriever = enhanced_kg_retriever or EnhancedKGRetriever(db=self.db, settings=self.settings)
        
        # Initialize classifier
        self.classifier = classifier or QueryClassifier(settings=self.settings)
        
        # Map of retriever methods
        self.retrievers = {
            "vector": self.vector_retriever,
            "graphrag": self.graph_retriever,
            "kg": self.kg_retriever,
            "enhanced_kg": self.enhanced_kg_retriever,
        }
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve information using the optimal method based on query type.
        
        Args:
            query: The query text
            top_k: Number of results to retrieve
            **kwargs: Additional keyword arguments
            
        Returns:
            List of retrieved data
        """
        # Get the best retrieval method for this query
        retrieval_plan = self._get_retrieval_plan(query)
        
        # Try the primary method
        primary_method = retrieval_plan["primary"]
        fallback_method = retrieval_plan["fallback"]
        
        logger.info(f"Using primary retrieval method: {primary_method}")
        
        try:
            results = self.retrievers[primary_method].retrieve(query, top_k=top_k, **kwargs)
            
            # If the primary method returned good results, use them
            if self._has_good_results(results, primary_method):
                return results
                
            # Otherwise, try the fallback method
            logger.info(f"Primary method returned insufficient results, trying fallback: {fallback_method}")
        except Exception as e:
            logger.error(f"Error with primary retrieval method {primary_method}: {str(e)}")
            logger.info(f"Falling back to {fallback_method}")
        
        # Use the fallback method
        try:
            return self.retrievers[fallback_method].retrieve(query, top_k=top_k, **kwargs)
        except Exception as e:
            logger.error(f"Error with fallback retrieval method {fallback_method}: {str(e)}")
            # Last resort, try vector retrieval
            if fallback_method != "vector":
                logger.info("Falling back to vector retrieval as last resort")
                return self.vector_retriever.retrieve(query, top_k=top_k, **kwargs)
            return []
    
    def _get_retrieval_plan(self, query: str) -> Dict[str, str]:
        """
        Determine the best retrieval methods for a query.
        
        Args:
            query: The query to plan for
            
        Returns:
            Dict containing primary and fallback methods
        """
        # Classify the query
        query_type = self.classifier.classify(query)
        
        # Select retrievers based on query type
        if query_type == QueryType.ENTITY:
            return {
                "primary": "enhanced_kg",
                "fallback": "graphrag"
            }
        elif query_type == QueryType.RELATIONSHIP:
            return {
                "primary": "enhanced_kg",
                "fallback": "kg"
            }
        elif query_type == QueryType.PROCEDURAL:
            return {
                "primary": "graphrag",
                "fallback": "vector"
            }
        else:  # FACTUAL and default
            return {
                "primary": "graphrag",
                "fallback": "vector"
            }
    
    def _has_good_results(self, results: List[Dict[str, Any]], method: str) -> bool:
        """
        Check if retrieval results are good enough.
        
        Args:
            results: The retrieval results to check
            method: The retrieval method used
            
        Returns:
            bool: True if the results are good, False otherwise
        """
        # No results means it's not good
        if not results:
            return False
            
        # For KG methods, we need at least one meaningful result
        if method in ["kg", "enhanced_kg"]:
            # Check if there are non-empty values in the results
            for result in results:
                if any(value for value in result.values() if value):
                    return True
            return False
            
        # For vector/graph methods, we need at least 3 results for good context
        return len(results) >= 3
    
    def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using the optimal retrieval method.
        
        Args:
            query: The question to answer
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments
            
        Returns:
            QueryResponse with answer and context
        """
        start_time = time.time()
        
        # Get the best retrieval method for this query
        retrieval_plan = self._get_retrieval_plan(query)
        primary_method = retrieval_plan["primary"]
        fallback_method = retrieval_plan["fallback"]
        
        logger.info(f"Answering using primary retrieval method: {primary_method}")
        
        try:
            # Try the primary method
            response = self.retrievers[primary_method].answer_question(
                query=query,
                top_k=top_k,
                **kwargs
            )
            
            # If the answer is a fallback/generic response, try the fallback method
            if "Not applicable:" in response.answer:
                logger.info(f"Primary method returned generic answer, trying fallback: {fallback_method}")
                fallback_response = self.retrievers[fallback_method].answer_question(
                    query=query,
                    top_k=top_k,
                    **kwargs
                )
                
                # If the fallback has a better answer, use it
                if "Not applicable:" not in fallback_response.answer:
                    return fallback_response
            
            # Otherwise, use the primary method response
            return response
            
        except Exception as e:
            logger.error(f"Error with primary method {primary_method}: {str(e)}")
            
            try:
                # Try the fallback method
                logger.info(f"Falling back to {fallback_method}")
                return self.retrievers[fallback_method].answer_question(
                    query=query,
                    top_k=top_k,
                    **kwargs
                )
            except Exception as e2:
                logger.error(f"Error with fallback method {fallback_method}: {str(e2)}")
                
                # Calculate response time for error
                response_time = time.time() - start_time
                
                # Return a generic error response
                return QueryResponse(
                    query=query,
                    answer=f"I apologize, but I encountered an error while searching for information. Please try a different question or rephrase your query.",
                    retrieval_method="hybrid",
                    query_time=response_time,
                    context=[],
                    metadata={"error": str(e), "fallback_error": str(e2)},
                )