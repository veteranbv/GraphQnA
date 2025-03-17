"""Vector-based retrieval for question answering."""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from neo4j_graphrag.generation import GraphRAG, RagTemplate
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorRetriever as GraphRAGVectorRetriever

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.response import QueryResponse, VectorQueryResult
from graphqna.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)


class CustomVectorRetriever(GraphRAGVectorRetriever):
    """Custom VectorRetriever that handles embeddings correctly."""
    
    def __init__(self, *args, index_dimensions: int = 1536, **kwargs):
        """Initialize with index dimensions."""
        super().__init__(*args, **kwargs)
        self.index_dimensions = index_dimensions
        
    def _get_embeddings(self, query_text=None, query_vector=None):
        """Override to handle embedding dimensions."""
        if query_vector is not None:
            # Truncate or pad to match index dimensions
            current_dims = len(query_vector)
            if current_dims > self.index_dimensions:
                logger.warning(f"Truncating embedding from {current_dims} to {self.index_dimensions}")
                return query_vector[:self.index_dimensions]
            elif current_dims < self.index_dimensions:
                logger.warning(f"Padding embedding from {current_dims} to {self.index_dimensions}")
                padded = query_vector.copy()
                padded.extend([0.0] * (self.index_dimensions - current_dims))
                return padded
            return query_vector
        
        # Otherwise, use the default implementation
        return super()._get_embeddings(query_text, query_vector)


class VectorRetriever(BaseRetriever):
    """
    Vector-based retriever for semantic similarity search.
    
    This retriever uses vector embeddings to find semantically similar
    chunks of text to the user's query.
    """

    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None,
        **kwargs
    ):
        """
        Initialize the vector retriever.
        
        Args:
            db: Neo4j database connection (optional)
            settings: Application settings (optional)
            **kwargs: Additional keyword arguments passed to the parent class
        """
        super().__init__(db=db, settings=settings, **kwargs)
        
        # Create the LLM for answering questions
        self.llm = OpenAILLM(
            model_name=self.settings.llm.model,
            api_key=self.settings.llm.api_key,
            model_params={
                "temperature": self.settings.llm.temperature,
            }
        )
        
        # First check if the vector index exists using our own database connection
        logger.info(f"Initializing VectorRetriever with vector index name: {self.settings.vector.index_name}")
        
        # Verify index exists and get its actual name (in case there's a case sensitivity issue)
        index_name = self.settings.vector.index_name
        chunk_label = self.settings.graph.chunk_label
        embedding_property = self.settings.vector.embedding_property
        
        # Run a query to list all vector indexes
        index_query = """
        SHOW VECTOR INDEXES
        YIELD name, labelsOrTypes, properties, options
        WHERE labelsOrTypes CONTAINS $label
          AND properties CONTAINS $property
        RETURN name, labelsOrTypes, properties, options
        """
        
        index_dimensions = self.settings.vector.dimensions
        
        try:
            with self.db.session() as session:
                result = session.run(
                    index_query, 
                    label=chunk_label, 
                    property=embedding_property
                ).data()
                
                if result and len(result) > 0:
                    # Use the actual index name from the database
                    actual_index_name = result[0]["name"]
                    logger.info(f"Found vector index in database: {actual_index_name}")
                    
                    # Check for index dimensions
                    options = result[0].get("options", {})
                    if "indexConfig" in options and "vector.dimensions" in options["indexConfig"]:
                        index_dimensions = int(options["indexConfig"]["vector.dimensions"])
                        logger.info(f"Index dimensions: {index_dimensions}")
                    
                    # Log warning if names don't match
                    if actual_index_name != index_name:
                        logger.warning(f"Vector index name mismatch! Config: {index_name}, Actual: {actual_index_name}")
                        index_name = actual_index_name
                else:
                    logger.warning(f"No vector index found for label {chunk_label} and property {embedding_property}")
        except Exception as e:
            logger.error(f"Error checking vector index: {str(e)}")
        
        # Initialize the GraphRAG vector retriever with the verified index name
        self.vector_retriever = CustomVectorRetriever(
            driver=self.db.get_driver(),
            index_name=index_name,  # Use the verified index name
            embedder=self.embedder,
            return_properties=["text", "index"],
            index_dimensions=index_dimensions,  # Pass dimensions to custom retriever
        )
        
        # Create the prompt template for vector-based retrieval
        self.prompt_template = RagTemplate(
            template="""
            Answer the following question based solely on the information from the retrieved content:
            
            Question: {query_text}
            
            Context: {context}
            
            Guidelines:
            1. Use ONLY information that is EXPLICITLY stated in the retrieved content.
            2. If the information is insufficient for a complete answer, only provide what can be directly verified.
            3. If no relevant information is found, respond with "Not applicable: This information is not available in the Hero by Vivun knowledge base."
            4. DO NOT use your general knowledge - rely SOLELY on the retrieved content.
            5. Do not invent details not present in the retrieved content.
            6. End with: "Please verify this information in the Hero by Vivun documentation for the most up-to-date details."
            """,
            expected_inputs=["context", "query_text"]
        )
        
    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query using vector similarity.
        
        Args:
            query: The query text
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments
            
        Returns:
            List of retrieved context items
        """
        # Set default top_k if not provided
        if top_k is None:
            top_k = self.settings.chunking.vector_top_k
            
        try:
            # Get vector embedding for the query, with proper dimensions
            query_embedding = self.embed_query(query)
            
            # Perform vector search
            retriever_results = self.vector_retriever.search(
                query_vector=query_embedding,
                top_k=top_k,
                filters=kwargs.get("filters")
            )
            
            # Convert to list of dictionaries
            results = []
            for item in retriever_results.items:
                result_dict = {
                    "text": item.content,
                    "score": item.metadata.get("score", 0.0),
                    "chunk_index": item.metadata.get("index"),
                }
                results.append(result_dict)
                
            return results
        except Exception as e:
            logger.error(f"Error in vector retrieval: {str(e)}")
            # Return empty results on error
            return []
            
    def answer_question(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using vector-based retrieval.
        
        Args:
            query: The question to answer
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments
            
        Returns:
            Query response with answer and context
        """
        start_time = time.time()
        
        try:
            # Create GraphRAG pipeline for vector-based retrieval
            rag = GraphRAG(
                retriever=self.vector_retriever, 
                llm=self.llm,
                prompt_template=self.prompt_template
            )

            # Set default top_k if not provided
            if top_k is None:
                top_k = self.settings.chunking.vector_top_k
                
            # Run the RAG pipeline
            rag_result = rag.search(
                query_text=query, 
                retriever_config={"top_k": top_k}
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Convert context to VectorQueryResult objects
            context = []
            if hasattr(rag_result, "retrieval_context"):
                for item in rag_result.retrieval_context:
                    context.append(
                        VectorQueryResult(
                            text=item.get("text", ""),
                            chunk_index=item.get("index"),
                            score=item.get("score", 0.0),
                            metadata={}
                        )
                    )
            
            # Create response
            return QueryResponse(
                query=query,
                answer=rag_result.answer,
                retrieval_method="vector",
                query_time=response_time,
                context=context,
            )
        except Exception as e:
            logger.error(f"Error answering question with vector retrieval: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Calculate response time even for errors
            response_time = time.time() - start_time
            
            # Return error response
            return QueryResponse(
                query=query,
                answer=f"Error retrieving answer: {str(e)}",
                retrieval_method="vector",
                query_time=response_time,
                context=[],
                metadata={"error": str(e)},
            )