"""GraphRAG-based retrieval for question answering."""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from neo4j_graphrag.generation import GraphRAG, RagTemplate
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorCypherRetriever

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.entity import Entity, Relationship
from graphqna.models.response import GraphQueryResult, QueryResponse
from graphqna.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)


class CustomVectorCypherRetriever(VectorCypherRetriever):
    """Custom VectorCypherRetriever that handles embeddings correctly."""
    
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


class GraphRetriever(BaseRetriever):
    """
    GraphRAG-based retriever for semantic search with graph context.
    
    This retriever leverages the Neo4j GraphRAG framework to combine vector search 
    with graph traversal to provide richer context for answering questions.
    """

    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None,
        **kwargs
    ):
        """
        Initialize the graph retriever.
        
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
        
        # Define the retrieval query for GraphRAG search
        retrieval_query = """
        // Start with the main chunk node that matched the vector search
        MATCH (chunk:Chunk)
        WHERE chunk = node
        
        // Get connected entity nodes
        OPTIONAL MATCH (entity)-[:FROM_CHUNK]->(chunk)
        WHERE NOT entity:Document
        
        // Get related entities that are 1-hop away
        OPTIONAL MATCH (entity)-[rel]-(related)
        WHERE NOT related:Document AND NOT related:Chunk
        
        // Return all the information in a structured format
        RETURN 
            chunk.text as chunk_text,
            chunk.index as chunk_index,
            collect(DISTINCT {
                type: labels(entity),
                properties: properties(entity),
                id: elementId(entity)
            }) as entities,
            collect(DISTINCT {
                source_type: labels(entity),
                source: properties(entity),
                source_id: elementId(entity),
                relationship: type(rel),
                target_type: labels(related),
                target: properties(related),
                target_id: elementId(related)
            }) as relationships,
            score
        """
        
        # First check if the vector index exists using our own database connection
        logger.info(f"Initializing GraphRetriever with vector index name: {self.settings.vector.index_name}")
        
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
        
        # Initialize the GraphRAG vector-cypher retriever with the verified index name
        self.graph_retriever = CustomVectorCypherRetriever(
            driver=self.db.get_driver(),
            index_name=index_name,  # Use the verified index name
            embedder=self.embedder,
            retrieval_query=retrieval_query,
            index_dimensions=index_dimensions,  # Pass dimensions to custom retriever
        )
        
        # Create the prompt template for GraphRAG retrieval
        self.prompt_template = RagTemplate(
            template="""
            Answer the following question using the information from both the text chunks and the knowledge graph entities and relationships:
            
            Question: {query_text}
            
            Context: {context}
            
            Guidelines:
            1. Use ONLY information that is explicitly stated in the retrieved content or can be directly inferred from the entity relationships.
            2. Pay special attention to the entities, their types, properties, and relationships between them.
            3. If the information is insufficient for a complete answer, only provide what can be directly verified.
            4. If no relevant information is found, respond with "Not applicable: This information is not available in the Hero by Vivun knowledge base."
            5. DO NOT use your general knowledge - rely SOLELY on the retrieved content and entity relationships.
            6. End with: "Please verify this information in the Hero by Vivun documentation for the most up-to-date details."
            
            When answering questions about Activity Types, be sure to include:
            - The full name of the Activity Type (including its category)
            - When this Activity Type should be used
            - Any specific scenarios where it's most appropriate
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
        Retrieve relevant context for a query using GraphRAG retrieval.
        
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
            
            # Perform GraphRAG search
            retriever_results = self.graph_retriever.search(
                query_vector=query_embedding,
                top_k=top_k,
                filters=kwargs.get("filters")
            )
            
            # Convert to list of dictionaries
            results = []
            for item in retriever_results.items:
                # Extract main content and score
                content = item.content
                score = item.metadata.get("score", 0.0)
                
                # Create result dictionary
                result_dict = {
                    "chunk_text": content.get("chunk_text", ""),
                    "chunk_index": content.get("chunk_index"),
                    "score": score,
                    "entities": content.get("entities", []),
                    "relationships": content.get("relationships", []),
                }
                results.append(result_dict)
                
            return results
        except Exception as e:
            logger.error(f"Error in GraphRAG retrieval: {str(e)}")
            # Return empty results on error
            return []
            
    def answer_question(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using GraphRAG retrieval.
        
        Args:
            query: The question to answer
            top_k: Number of results to retrieve (optional)
            **kwargs: Additional keyword arguments
            
        Returns:
            Query response with answer and context
        """
        start_time = time.time()
        
        try:
            # Create GraphRAG pipeline for retrieval
            rag = GraphRAG(
                retriever=self.graph_retriever, 
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
            
            # Convert context to GraphQueryResult objects
            context = []
            if hasattr(rag_result, "retrieval_context"):
                for item in rag_result.retrieval_context:
                    # Parse entities
                    entities = []
                    for entity_data in item.get("entities", []):
                        try:
                            entity = Entity(
                                labels=entity_data.get("type", []),
                                properties=entity_data.get("properties", {}),
                                node_id=entity_data.get("id")
                            )
                            entities.append(entity)
                        except Exception as e:
                            logger.warning(f"Error parsing entity: {str(e)}")
                            
                    # Parse relationships
                    relationships = []
                    for rel_data in item.get("relationships", []):
                        try:
                            # Create source and target entities
                            source = Entity(
                                labels=rel_data.get("source_type", []),
                                properties=rel_data.get("source", {}),
                                node_id=rel_data.get("source_id")
                            )
                            
                            target = Entity(
                                labels=rel_data.get("target_type", []),
                                properties=rel_data.get("target", {}),
                                node_id=rel_data.get("target_id")
                            )
                            
                            # Create relationship
                            relationship = Relationship(
                                type=rel_data.get("relationship", "RELATED_TO"),
                                properties={},
                                source=source,
                                target=target
                            )
                            relationships.append(relationship)
                        except Exception as e:
                            logger.warning(f"Error parsing relationship: {str(e)}")
                    
                    # Create GraphQueryResult
                    graph_result = GraphQueryResult(
                        text=item.get("chunk_text", ""),
                        chunk_index=item.get("chunk_index"),
                        score=item.get("score", 0.0),
                        entities=entities,
                        relationships=relationships,
                        metadata={}
                    )
                    context.append(graph_result)
            
            # Create response
            return QueryResponse(
                query=query,
                answer=rag_result.answer,
                retrieval_method="graphrag",
                query_time=response_time,
                context=context,
            )
        except Exception as e:
            logger.error(f"Error answering question with GraphRAG retrieval: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Calculate response time even for errors
            response_time = time.time() - start_time
            
            # Return error response
            return QueryResponse(
                query=query,
                answer=f"Error retrieving answer: {str(e)}",
                retrieval_method="graphrag",
                query_time=response_time,
                context=[],
                metadata={"error": str(e)},
            )