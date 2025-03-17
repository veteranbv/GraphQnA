"""Document embedding utilities for generating vector representations."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from neo4j_graphrag.embeddings import OpenAIEmbeddings

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase, VectorIndex
from graphqna.models.document import Document, DocumentChunk

logger = logging.getLogger(__name__)


class ChunkEmbedder:
    """
    Creates embeddings for document chunks.
    
    This class handles generating vector representations of text chunks
    using OpenAI's embeddings API and storing them in Neo4j.
    """

    def __init__(
        self, 
        db: Optional[Neo4jDatabase] = None, 
        vector_index: Optional[VectorIndex] = None,
        settings: Optional[Settings] = None
    ):
        """
        Initialize the chunk embedder.
        
        Args:
            db: Neo4j database connection (optional)
            vector_index: Vector index manager (optional)
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()
        self.db = db or Neo4jDatabase()
        self.vector_index = vector_index or VectorIndex(db=self.db, settings=self.settings)
        
        # Initialize the embedder
        self.embedder = OpenAIEmbeddings(
            model=self.settings.llm.embedding_model,
            api_key=self.settings.llm.api_key,
        )
        
    def embed_document(self, document: Document) -> Document:
        """
        Create embeddings for all chunks in a document.
        
        Args:
            document: Document with chunks to embed
            
        Returns:
            Document with embeddings added to chunks
        """
        if not document.chunks:
            logger.warning("Document has no chunks to embed")
            return document
            
        # Get text from each chunk
        texts = [chunk.text for chunk in document.chunks]
        
        # Generate embeddings for all texts at once (more efficient)
        embeddings = self.embedder.embed_documents(texts)
        
        # Add embeddings to chunks
        for i, embedding in enumerate(embeddings):
            document.chunks[i].embedding = embedding
            
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")
        return document
        
    async def embed_document_async(self, document: Document) -> Document:
        """
        Create embeddings for all chunks in a document asynchronously.
        
        Args:
            document: Document with chunks to embed
            
        Returns:
            Document with embeddings added to chunks
        """
        if not document.chunks:
            logger.warning("Document has no chunks to embed")
            return document
            
        # Process chunks in batches to avoid rate limits
        batch_size = 20
        for i in range(0, len(document.chunks), batch_size):
            batch = document.chunks[i:i+batch_size]
            
            # Create tasks for embedding generation
            tasks = []
            for chunk in batch:
                task = asyncio.create_task(self._embed_text_async(chunk.text))
                tasks.append((chunk, task))
                
            # Wait for all tasks to complete
            for chunk, task in tasks:
                embedding = await task
                chunk.embedding = embedding
                
            logger.info(f"Embedded batch of {len(batch)} chunks")
            
            # Small delay to prevent rate limiting
            await asyncio.sleep(0.5)
            
        logger.info(f"Generated embeddings for {len(document.chunks)} chunks")
        return document
        
    async def _embed_text_async(self, text: str) -> List[float]:
        """
        Embed a single text asynchronously.
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding
        """
        # Since OpenAIEmbeddings doesn't have a native async API, 
        # we'll run it in a thread pool
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, self.embedder.embed_query, text
        )
        return embedding
        
    def embed_query(self, query: str) -> List[float]:
        """
        Create an embedding for a query string.
        
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
        
    def store_document_embeddings(self, document: Document) -> Dict[str, Any]:
        """
        Store document chunks and their embeddings in Neo4j.
        
        Args:
            document: Document with embedded chunks
            
        Returns:
            Dict with statistics about the operation
        """
        # Ensure vector index exists
        if not self.vector_index.ensure_index_exists():
            logger.error("Failed to ensure vector index exists")
            return {"status": "error", "message": "Failed to ensure vector index exists"}
            
        # Create document node
        document_query = """
        CREATE (d:Document {
            title: $title,
            source: $source,
            source_type: $source_type,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        RETURN elementId(d) as document_id
        """
        
        document_params = {
            "title": document.metadata.title or "Untitled",
            "source": document.metadata.source,
            "source_type": document.metadata.source_type,
            "created_at": document.metadata.created_at.isoformat() if document.metadata.created_at else None,
            "updated_at": document.metadata.updated_at.isoformat() if document.metadata.updated_at else None,
        }
        
        # Execute document creation
        document_result = self.db.execute_write(document_query, document_params)
        if not document_result or "document_id" not in document_result:
            logger.error("Failed to create document node")
            return {"status": "error", "message": "Failed to create document node"}
            
        document_id = document_result["document_id"]
        
        # Create chunk nodes and link to document
        chunks_created = 0
        chunks_with_embeddings = 0
        
        chunk_label = self.settings.graph.chunk_label
        document_label = self.settings.graph.document_label
        next_chunk_rel = self.settings.graph.next_chunk_rel
        part_of_document_rel = self.settings.graph.part_of_document_rel
        
        # Process chunks
        previous_chunk_id = None
        
        for chunk in document.chunks:
            # Create chunk query
            chunk_query = f"""
            CREATE (c:{chunk_label} {{
                text: $text,
                index: $index,
                start_char: $start_char,
                end_char: $end_char
            }})
            WITH c
            MATCH (d:{document_label}) WHERE elementId(d) = $document_id
            CREATE (c)-[:{part_of_document_rel}]->(d)
            """
            
            # Add connection to previous chunk if it exists
            if previous_chunk_id is not None:
                chunk_query += f"""
                WITH c
                MATCH (prev) WHERE elementId(prev) = $previous_chunk_id
                CREATE (prev)-[:{next_chunk_rel}]->(c)
                """
                
            # Return the chunk ID
            chunk_query += """
            RETURN elementId(c) as chunk_id
            """
            
            # Chunk parameters
            chunk_params = {
                "text": chunk.text,
                "index": chunk.index,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "document_id": document_id,
                "previous_chunk_id": previous_chunk_id,
            }
            
            # Execute chunk creation
            chunk_result = self.db.execute_write(chunk_query, chunk_params)
            if not chunk_result or "chunk_id" not in chunk_result:
                logger.error(f"Failed to create chunk node for index {chunk.index}")
                continue
                
            chunk_id = chunk_result["chunk_id"]
            chunks_created += 1
            previous_chunk_id = chunk_id
            
            # Store embedding if available
            if chunk.embedding:
                if self.vector_index.upsert_node_embedding(chunk_id, chunk.embedding):
                    chunks_with_embeddings += 1
                else:
                    logger.error(f"Failed to store embedding for chunk {chunk_id}")
        
        logger.info(f"Stored {chunks_created} chunks with {chunks_with_embeddings} embeddings for document {document_id}")
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_created": chunks_created,
            "chunks_with_embeddings": chunks_with_embeddings,
        }