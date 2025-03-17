"""Retrieval service for coordinating different retrieval methods."""

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.response import QueryResponse
from graphqna.retrieval.base import BaseRetriever
from graphqna.retrieval.vector import VectorRetriever
from graphqna.retrieval.graph import GraphRetriever
from graphqna.retrieval.kg import KnowledgeGraphRetriever
from graphqna.retrieval.enhanced_kg import EnhancedKGRetriever
from graphqna.retrieval.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)


class RetrievalMethod(str, Enum):
    """Available retrieval methods."""

    VECTOR = "vector"
    GRAPHRAG = "graphrag"
    KG = "kg"
    ENHANCED_KG = "enhanced_kg"
    HYBRID = "hybrid"


class RetrievalService:
    """
    Unified service for retrieving answers using different methods.
    
    This service provides a single interface for all retrieval methods,
    managing the creation and configuration of different retrievers.
    """

    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None
    ):
        """
        Initialize the retrieval service.
        
        Args:
            db: Neo4j database connection (optional)
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()
        self.db = db or Neo4jDatabase()
        
        # Initialize retrievers lazily
        self._vector_retriever = None
        self._graph_retriever = None
        self._kg_retriever = None
        self._enhanced_kg_retriever = None
        self._hybrid_retriever = None
        
    def get_retriever(self, method: Union[str, RetrievalMethod]) -> BaseRetriever:
        """
        Get the appropriate retriever based on the method.
        
        Args:
            method: Retrieval method to use
            
        Returns:
            The corresponding retriever
            
        Raises:
            ValueError: If method is not valid
        """
        # Normalize method to enum
        if isinstance(method, str):
            try:
                method = RetrievalMethod(method.lower())
            except ValueError:
                raise ValueError(f"Invalid retrieval method: {method}")
        
        # Return appropriate retriever
        if method == RetrievalMethod.VECTOR:
            if self._vector_retriever is None:
                self._vector_retriever = VectorRetriever(db=self.db, settings=self.settings)
            return self._vector_retriever
        elif method == RetrievalMethod.GRAPHRAG:
            if self._graph_retriever is None:
                self._graph_retriever = GraphRetriever(db=self.db, settings=self.settings)
            return self._graph_retriever
        elif method == RetrievalMethod.KG:
            if self._kg_retriever is None:
                self._kg_retriever = KnowledgeGraphRetriever(db=self.db, settings=self.settings)
            return self._kg_retriever
        elif method == RetrievalMethod.ENHANCED_KG:
            if self._enhanced_kg_retriever is None:
                self._enhanced_kg_retriever = EnhancedKGRetriever(db=self.db, settings=self.settings)
            return self._enhanced_kg_retriever
        elif method == RetrievalMethod.HYBRID:
            if self._hybrid_retriever is None:
                self._hybrid_retriever = HybridRetriever(
                    db=self.db, 
                    settings=self.settings,
                    vector_retriever=self._vector_retriever,
                    graph_retriever=self._graph_retriever,
                    kg_retriever=self._kg_retriever,
                    enhanced_kg_retriever=self._enhanced_kg_retriever
                )
            return self._hybrid_retriever
        else:
            raise ValueError(f"Unsupported retrieval method: {method}")
            
    def answer_question(
        self, 
        query: str, 
        method: Union[str, RetrievalMethod] = RetrievalMethod.GRAPHRAG,
        top_k: Optional[int] = None,
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using the specified retrieval method.
        
        Args:
            query: The question to answer
            method: Retrieval method to use
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments for the retriever
            
        Returns:
            Query response with answer and context
        """
        start_time = time.time()
        
        try:
            # Get the appropriate retriever
            retriever = self.get_retriever(method)
            
            # Answer the question
            response = retriever.answer_question(
                query=query,
                top_k=top_k,
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Calculate response time for error
            response_time = time.time() - start_time
            
            # Create error response
            return QueryResponse(
                query=query,
                answer=f"Error: {str(e)}",
                retrieval_method=str(method),
                query_time=response_time,
                context=[],
                metadata={"error": str(e)},
            )
            
    def close(self) -> None:
        """Close all resources used by the service."""
        # Make sure to close database connection
        if self.db:
            self.db.close()