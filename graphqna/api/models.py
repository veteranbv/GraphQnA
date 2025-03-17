"""API models for serialization and validation."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from graphqna.models.response import QueryResponse


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    
    query: str = Field(..., description="The question to answer")
    retrieval_method: str = Field(
        "hybrid", description="Method used for retrieval (vector, graphrag, kg, enhanced_kg, hybrid)"
    )
    top_k: Optional[int] = Field(None, description="Number of results to retrieve")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for response")
    

class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    database_connected: bool = Field(..., description="Database connection status")


class InfoResponse(BaseModel):
    """Response model for info endpoint."""
    
    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Service description")
    database_stats: Dict[str, Any] = Field(
        ..., description="Database statistics (nodes, relationships, etc.)"
    )
    domain_config: Dict[str, Any] = Field(
        ..., description="Current domain configuration"
    )
    retrieval_methods: List[str] = Field(
        ..., description="Available retrieval methods"
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    
    source: str = Field(..., description="Document source (file path or URL)")
    format: Optional[str] = Field(None, description="Document format (pdf, md, txt, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    build_kg: bool = Field(True, description="Whether to build a knowledge graph")


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    
    success: bool = Field(..., description="Whether ingestion was successful")
    document_id: Optional[str] = Field(None, description="ID of the ingested document")
    chunks: Optional[int] = Field(None, description="Number of chunks created")
    entities: Optional[int] = Field(None, description="Number of entities extracted")
    relationships: Optional[int] = Field(None, description="Number of relationships extracted")
    message: Optional[str] = Field(None, description="Additional information")