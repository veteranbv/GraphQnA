"""Base retriever interface."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from neo4j_graphrag.embeddings import OpenAIEmbeddings

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.response import QueryResponse

logger = logging.getLogger(__name__)


class BaseRetriever(ABC):
    """
    Base class for all retrievers.
    
    This abstract class defines the interface that all retrievers must implement.
    """

    def __init__(
        self, 
        db: Optional[Neo4jDatabase] = None,
        embedder: Optional[OpenAIEmbeddings] = None,
        settings: Optional[Settings] = None
    ):
        """
        Initialize the base retriever.
        
        Args:
            db: Neo4j database connection (optional)
            embedder: Embeddings generator (optional)
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()
        self.db = db or Neo4jDatabase()
        
        # Initialize embedder if not provided
        if embedder:
            self.embedder = embedder
        else:
            self.embedder = OpenAIEmbeddings(
                model=self.settings.llm.embedding_model,
                api_key=self.settings.llm.api_key,
            )
            
    def embed_query(self, query: str) -> List[float]:
        """
        Create an embedding for a query string, ensuring it matches the expected dimensions.
        
        Args:
            query: Query text to embed
            
        Returns:
            Vector embedding truncated to the correct dimensions
        """
        # Get raw embedding
        embedding = self.embedder.embed_query(query)
        
        # Truncate or pad embedding to match expected dimensions
        expected_dimensions = self.settings.vector.dimensions
        current_dimensions = len(embedding)
        
        if current_dimensions > expected_dimensions:
            logger.warning(f"Truncating embedding from {current_dimensions} to {expected_dimensions} dimensions")
            embedding = embedding[:expected_dimensions]
        elif current_dimensions < expected_dimensions:
            logger.warning(f"Padding embedding from {current_dimensions} to {expected_dimensions} dimensions")
            embedding.extend([0.0] * (expected_dimensions - current_dimensions))
        
        return embedding
        
    @abstractmethod
    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: The query text
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments
            
        Returns:
            List of retrieved context items
        """
        pass
        
    @abstractmethod
    def answer_question(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using the retriever.
        
        Args:
            query: The question to answer
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments
            
        Returns:
            Query response with answer and context
        """
        pass