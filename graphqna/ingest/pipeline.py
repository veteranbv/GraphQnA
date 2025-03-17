"""Ingestion pipeline for processing documents into the knowledge graph."""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm import OpenAILLM

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase, VectorIndex
from graphqna.ingest.chunker import DocumentChunker
from graphqna.ingest.embedder import ChunkEmbedder
from graphqna.ingest.kg_builder import KnowledgeGraphBuilder, Schema
from graphqna.ingest.kg_importer import KnowledgeGraphImporter
from graphqna.models.document import Document

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    End-to-end pipeline for document ingestion into the knowledge graph.
    
    This class orchestrates the entire ingestion process:
    1. Document loading and preprocessing
    2. Chunking the document into manageable pieces
    3. Creating embeddings for chunks
    4. Building the knowledge graph with entities and relationships
    5. Ensuring vector indices for retrieval
    """

    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        chunker: Optional[DocumentChunker] = None,
        embedder: Optional[ChunkEmbedder] = None,
        vector_index: Optional[VectorIndex] = None,
        kg_builder: Optional[KnowledgeGraphBuilder] = None,
        kg_importer: Optional[KnowledgeGraphImporter] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the ingestion pipeline.
        
        Args:
            db: Neo4j database connection (optional)
            chunker: Document chunker (optional)
            embedder: Chunk embedder (optional)
            vector_index: Vector index manager (optional)
            kg_builder: Knowledge graph builder (optional)
            kg_importer: Knowledge graph importer (optional)
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()
        self.db = db or Neo4jDatabase()
        self.chunker = chunker or DocumentChunker(settings=self.settings)
        self.vector_index = vector_index or VectorIndex(db=self.db, settings=self.settings)
        self.embedder = embedder or ChunkEmbedder(
            db=self.db, 
            vector_index=self.vector_index,
            settings=self.settings
        )
        
        # Initialize KG builder and importer
        self.kg_builder = kg_builder or KnowledgeGraphBuilder(settings=self.settings)
        self.kg_importer = kg_importer or KnowledgeGraphImporter(db=self.db, settings=self.settings)
        
        # Initialize the LLM for knowledge graph building (legacy system)
        self.llm = OpenAILLM(
            model_name=self.settings.llm.model,
            api_key=self.settings.llm.api_key,
            model_params={
                "temperature": self.settings.llm.temperature,
                "max_tokens": self.settings.llm.max_tokens,
                "response_format": {"type": "json_object"},
            },
        )
        
        # Schema (will be detected during processing)
        self.detected_schema = None
        
    async def ingest_document(
        self, 
        file_path: Union[str, Path],
        clear_database: bool = False,
        advanced_kg: bool = True,
    ) -> Dict[str, Any]:
        """
        Ingest a document into the knowledge graph.
        
        Args:
            file_path: Path to the document file
            clear_database: Whether to clear the database before ingestion
            advanced_kg: Whether to use advanced knowledge graph features
            
        Returns:
            Dict with statistics about the ingestion
        """
        start_time = time.time()
        
        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
                "time_taken": time.time() - start_time,
            }
            
        # Clear database if requested
        if clear_database:
            logger.info("Clearing database...")
            try:
                self.db.clear_database()
                logger.info("Database cleared successfully")
            except Exception as e:
                logger.error(f"Failed to clear database: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to clear database: {str(e)}",
                    "time_taken": time.time() - start_time,
                }
                
        # Load document
        logger.info(f"Loading document from {file_path}")
        try:
            document = Document.from_file(file_path)
        except Exception as e:
            logger.error(f"Failed to load document: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to load document: {str(e)}",
                "time_taken": time.time() - start_time,
            }
            
        # Process document through the pipeline
        result = await self._process_document(document, advanced_kg)
        
        # Add timing information
        result["time_taken"] = time.time() - start_time
        
        return result
        
    async def _process_document(
        self, 
        document: Document,
        advanced_kg: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a document through the ingestion pipeline.
        
        Args:
            document: Document to process
            advanced_kg: Whether to use advanced knowledge graph features
            
        Returns:
            Dict with statistics about the processing
        """
        # Step 1: Chunk the document
        logger.info("Chunking document...")
        document = self.chunker.chunk_document(document)
        
        # Assign unique IDs to each chunk
        for i, chunk in enumerate(document.chunks):
            chunk.id = f"{document.metadata.source}_{i}"
            
        # Step 2: Generate embeddings for chunks
        logger.info("Generating embeddings...")
        document = await self.embedder.embed_document_async(document)
        
        # Step 3: Store document and chunks
        logger.info("Storing document and chunks...")
        storage_result = self.embedder.store_document_embeddings(document)
        
        if storage_result.get("status") != "success":
            logger.error("Failed to store document embeddings")
            return {
                "status": "error",
                "message": "Failed to store document embeddings",
                "detail": storage_result,
            }
            
        # Step 4: Build knowledge graph with entities and relationships
        logger.info("Building knowledge graph...")
        kg_result = await self._build_knowledge_graph(document, advanced_kg)
        
        if kg_result.get("status") != "success":
            logger.error("Failed to build knowledge graph")
            return {
                "status": "error",
                "message": "Failed to build knowledge graph",
                "detail": kg_result,
                "document": storage_result,
            }
            
        # Step 5: Get database statistics
        stats = self.db.get_database_stats()
        vector_stats = self.vector_index.get_index_stats()
        
        return {
            "status": "success",
            "document": storage_result,
            "knowledge_graph": kg_result,
            "database_stats": stats,
            "vector_index": vector_stats,
        }
        
    async def _build_knowledge_graph(
        self, 
        document: Document,
        advanced_kg: bool = True,
    ) -> Dict[str, Any]:
        """
        Build a knowledge graph from the document.
        
        Args:
            document: Document to process
            advanced_kg: Whether to use advanced knowledge graph features
            
        Returns:
            Dict with statistics about the knowledge graph
        """
        try:
            logger.info("Building knowledge graph using automatic extraction...")
            total_chunks = len(document.chunks)
            logger.info(f"Processing {total_chunks} chunks")
            
            # Auto mode: Use both new and legacy systems with more sophisticated logic
            if advanced_kg:
                # APPROACH 1: Use our new automatic KG builder
                # First, detect schema from the entire document
                if self.detected_schema is None:
                    # For performance, only sample a portion of the document for schema detection
                    sample_text = document.text[:10000]  # Use first 10K chars for schema detection
                    logger.info("Detecting schema from document sample...")
                    self.detected_schema = self.kg_builder.detect_schema(sample_text)
                
                # Track stats
                total_nodes = 0
                total_relationships = 0
                
                # Process each chunk with the schema
                for i, chunk in enumerate(document.chunks):
                    logger.info(f"Processing chunk {i+1}/{total_chunks} with automated KG builder")
                    
                    # Extract knowledge graph from chunk
                    kg = self.kg_builder.extract_knowledge_graph(
                        text=chunk.text,
                        schema=self.detected_schema
                    )
                    
                    # Import into database
                    if kg.nodes or kg.relationships:
                        # Use the chunk ID as the source ID
                        source_id = str(chunk.id)
                        nodes, rels = self.kg_importer.import_knowledge_graph(kg, source_id)
                        total_nodes += nodes
                        total_relationships += rels
                    
                # APPROACH 2: Also use the legacy system as a backup
                # Use the SimpleKGPipeline from neo4j-graphrag
                logger.info("Also using legacy KG builder as a supplement...")
                kg_builder = SimpleKGPipeline(
                    llm=self.llm,
                    driver=self.db.get_driver(),
                    embedder=self.embedder.embedder,
                    from_pdf=document.metadata.mime_type == "application/pdf",
                    entities=self.settings.entity_definitions,
                    relations=self.settings.relation_definitions,
                    potential_schema=self.settings.schema_triplets,
                    perform_entity_resolution=True,
                    neo4j_database=self.settings.neo4j.database,
                    lexical_graph_config={
                        "chunk_node_label": self.settings.graph.chunk_label,
                        "document_node_label": self.settings.graph.document_label,
                        "chunk_to_document_relationship_type": self.settings.graph.part_of_document_rel,
                        "next_chunk_relationship_type": self.settings.graph.next_chunk_rel,
                        "node_to_chunk_relationship_type": self.settings.graph.from_chunk_rel,
                        "chunk_embedding_property": self.settings.vector.embedding_property,
                    }
                )
                
                # Run the legacy pipeline
                await kg_builder.run_async(text=document.text)
                
                logger.info(f"Knowledge graph built successfully with {total_nodes} nodes and {total_relationships} relationships")
                
                return {
                    "status": "success",
                    "message": "Knowledge graph built successfully",
                    "nodes": total_nodes,
                    "relationships": total_relationships,
                }
            else:
                # Simple mode: Use just the legacy system
                logger.info("Using simple KG building mode...")
                kg_builder = SimpleKGPipeline(
                    llm=self.llm,
                    driver=self.db.get_driver(),
                    embedder=self.embedder.embedder,
                    from_pdf=document.metadata.mime_type == "application/pdf",
                    entities=None,
                    relations=None,
                    potential_schema=None,
                    perform_entity_resolution=True,
                    neo4j_database=self.settings.neo4j.database,
                    lexical_graph_config={
                        "chunk_node_label": self.settings.graph.chunk_label,
                        "document_node_label": self.settings.graph.document_label,
                        "chunk_to_document_relationship_type": self.settings.graph.part_of_document_rel,
                        "next_chunk_relationship_type": self.settings.graph.next_chunk_rel,
                        "node_to_chunk_relationship_type": self.settings.graph.from_chunk_rel,
                        "chunk_embedding_property": self.settings.vector.embedding_property,
                    }
                )
                
                # Run the legacy pipeline
                await kg_builder.run_async(text=document.text)
                
                logger.info("Knowledge graph built successfully")
                
                return {
                    "status": "success",
                    "message": "Knowledge graph built successfully",
                }
        except Exception as e:
            logger.error(f"Error building knowledge graph: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            return {
                "status": "error",
                "message": f"Error building knowledge graph: {str(e)}",
            }