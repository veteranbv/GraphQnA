"""Vector index management for Neo4j."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from neo4j_graphrag.indexes import (
    create_vector_index,
    drop_index_if_exists,
    upsert_vectors,
)
from neo4j_graphrag.types import EntityType

from graphqna.config import Settings, get_settings
from graphqna.db.neo4j import DatabaseError, Neo4jDatabase

logger = logging.getLogger(__name__)


class VectorIndexError(DatabaseError):
    """Base class for vector index errors."""

    pass


class VectorIndex:
    """
    Manages Neo4j vector indexes for embeddings.
    
    This class provides methods to create, update, and delete vector indexes,
    as well as to upsert vectors for nodes and relationships.
    """

    def __init__(
        self, 
        db: Optional[Neo4jDatabase] = None, 
        settings: Optional[Settings] = None
    ):
        """
        Initialize the vector index manager.
        
        Args:
            db: Neo4j database connection (optional)
            settings: Application settings (optional)
        """
        self.db = db or Neo4jDatabase()
        self.settings = settings or get_settings()
        
    def ensure_index_exists(self) -> bool:
        """
        Ensure the vector index exists, creating it if necessary.
        
        Returns:
            bool: True if index exists or was created, False otherwise
        """
        try:
            # Check if index exists
            index_name = self.settings.vector.index_name
            
            if self.db.check_index_exists(index_name):
                logger.info(f"Vector index '{index_name}' already exists")
                return True
                
            # Create index if it doesn't exist
            create_vector_index(
                self.db.get_driver(),
                index_name,
                label=self.settings.graph.chunk_label,
                embedding_property=self.settings.vector.embedding_property,
                dimensions=self.settings.vector.dimensions,
                similarity_fn=self.settings.vector.similarity_function,
            )
            logger.info(f"✅ Successfully created vector index '{index_name}'")
            return True
        except Exception as e:
            logger.error(f"❌ Error ensuring vector index: {str(e)}")
            return False
            
    def drop_index(self) -> bool:
        """
        Drop the vector index if it exists.
        
        Returns:
            bool: True if index was dropped or didn't exist, False on error
        """
        try:
            index_name = self.settings.vector.index_name
            drop_index_if_exists(self.db.get_driver(), index_name)
            logger.info(f"Vector index '{index_name}' dropped")
            return True
        except Exception as e:
            logger.error(f"❌ Error dropping vector index: {str(e)}")
            return False
            
    def upsert_node_embedding(
        self, 
        node_id: Union[int, str], 
        embedding: List[float]
    ) -> bool:
        """
        Upsert an embedding for a node.
        
        Args:
            node_id: The ID of the node
            embedding: The embedding vector
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            upsert_vectors(
                self.db.get_driver(),
                ids=[str(node_id)],
                embedding_property=self.settings.vector.embedding_property,
                embeddings=[embedding],
                entity_type=EntityType.NODE,
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error upserting node embedding: {str(e)}")
            return False
            
    def upsert_relationship_embedding(
        self, 
        relationship_id: Union[int, str], 
        embedding: List[float]
    ) -> bool:
        """
        Upsert an embedding for a relationship.
        
        Args:
            relationship_id: The ID of the relationship
            embedding: The embedding vector
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            upsert_vectors(
                self.db.get_driver(),
                ids=[str(relationship_id)],
                embedding_property=self.settings.vector.embedding_property,
                embeddings=[embedding],
                entity_type=EntityType.RELATIONSHIP,
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error upserting relationship embedding: {str(e)}")
            return False
            
    def batch_upsert_embeddings(
        self, 
        entity_ids: List[Union[int, str]], 
        embeddings: List[List[float]], 
        entity_type: EntityType = EntityType.NODE
    ) -> Tuple[int, int]:
        """
        Batch upsert embeddings for multiple entities.
        
        Args:
            entity_ids: List of entity IDs
            embeddings: List of embedding vectors
            entity_type: Type of entity (NODE or RELATIONSHIP)
            
        Returns:
            Tuple of (successful_count, total_count)
        """
        if len(entity_ids) != len(embeddings):
            raise ValueError("Number of IDs must match number of embeddings")
            
        # Convert all IDs to strings
        str_ids = [str(entity_id) for entity_id in entity_ids]
        
        try:
            upsert_vectors(
                self.db.get_driver(),
                ids=str_ids,
                embedding_property=self.settings.vector.embedding_property,
                embeddings=embeddings,
                entity_type=entity_type,
            )
            return (len(str_ids), len(str_ids))
        except Exception as e:
            logger.error(f"❌ Error in batch upserting embeddings: {str(e)}")
            
            # If batch failed, try one by one to save at least some
            successful = 0
            for i, (entity_id, embedding) in enumerate(zip(str_ids, embeddings)):
                try:
                    upsert_vectors(
                        self.db.get_driver(),
                        ids=[entity_id],
                        embedding_property=self.settings.vector.embedding_property,
                        embeddings=[embedding],
                        entity_type=entity_type,
                    )
                    successful += 1
                except Exception as e2:
                    logger.error(f"❌ Error upserting embedding for entity {entity_id}: {str(e2)}")
                    
            return (successful, len(str_ids))
            
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector index.
        
        Returns:
            Dict with index statistics
        """
        # Get total count of nodes with embeddings
        embedding_query = f"""
        MATCH (n:{self.settings.graph.chunk_label})
        WHERE n.{self.settings.vector.embedding_property} IS NOT NULL
        RETURN count(n) as count, 
               size(n.{self.settings.vector.embedding_property}) as dimensions
        LIMIT 1
        """
        
        try:
            with self.db.session() as session:
                result = session.run(embedding_query).data()
                
                if result and result[0]:
                    return {
                        "index_name": self.settings.vector.index_name,
                        "node_label": self.settings.graph.chunk_label,
                        "embedding_property": self.settings.vector.embedding_property,
                        "embedding_count": result[0].get("count", 0),
                        "embedding_dimensions": result[0].get("dimensions"),
                        "similarity_function": self.settings.vector.similarity_function,
                    }
                else:
                    return {
                        "index_name": self.settings.vector.index_name,
                        "node_label": self.settings.graph.chunk_label,
                        "embedding_property": self.settings.vector.embedding_property,
                        "embedding_count": 0,
                        "embedding_dimensions": self.settings.vector.dimensions,
                        "similarity_function": self.settings.vector.similarity_function,
                    }
        except Exception as e:
            logger.error(f"❌ Error getting vector index statistics: {str(e)}")
            return {
                "index_name": self.settings.vector.index_name,
                "error": str(e),
            }