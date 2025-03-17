"""Response models for queries."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from graphqna.models.entity import Entity, Relationship


class VectorQueryResult(BaseModel):
    """Result from a vector-based query."""

    text: str = Field(..., description="Text content of the matching chunk")
    chunk_index: Optional[int] = Field(None, description="Index of the chunk in the document")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class GraphQueryResult(BaseModel):
    """Result from a graph-enhanced query."""

    text: str = Field(..., description="Text content of the matching chunk")
    chunk_index: Optional[int] = Field(None, description="Index of the chunk in the document")
    score: float = Field(..., description="Similarity score")
    entities: List[Entity] = Field(default=[], description="Related entities")
    relationships: List[Relationship] = Field(default=[], description="Related relationships")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class KnowledgeGraphQueryResult(BaseModel):
    """Result from a knowledge graph query."""

    query: str = Field(..., description="The Cypher query executed")
    entities: List[Entity] = Field(default=[], description="Matched entities")
    relationships: List[Relationship] = Field(default=[], description="Matched relationships")
    raw_results: List[Dict[str, Any]] = Field(default=[], description="Raw query results")


class QueryResponse(BaseModel):
    """Response to a user query."""

    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Answer to the query")
    retrieval_method: str = Field(
        ..., description="Method used for retrieval (vector, graphrag, graph, kg, enhanced_kg, hybrid)"
    )
    query_time: float = Field(..., description="Time taken to generate the answer in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time of the response")
    context: Union[
        List[VectorQueryResult],
        List[GraphQueryResult],
        Optional[KnowledgeGraphQueryResult],
    ] = Field(
        None, description="Context used to generate the answer"
    )
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    @validator("answer")
    def validate_answer(cls, v):
        """Validate the answer field."""
        if not v or not v.strip():
            return "I don't have enough information to answer this question based on the available data."
        return v
    
    @validator("retrieval_method")
    def validate_retrieval_method(cls, v):
        """Validate the retrieval_method field."""
        valid_methods = ["vector", "graphrag", "graph", "kg", "enhanced_kg", "hybrid"]
        if v not in valid_methods:
            raise ValueError(f"Invalid retrieval method: {v}. Must be one of {valid_methods}")
        return v