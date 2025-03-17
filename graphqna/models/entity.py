"""Entity models for knowledge graph."""

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator


class Entity(BaseModel):
    """Entity in the knowledge graph."""

    labels: List[str] = Field(..., description="Node labels")
    properties: Dict[str, Any] = Field(..., description="Node properties")
    node_id: Optional[int] = Field(None, description="Neo4j node ID")
    
    @property
    def primary_label(self) -> str:
        """Get the primary (first) label of the entity."""
        return self.labels[0] if self.labels else "Unknown"
    
    @property
    def name(self) -> str:
        """Get the name property of the entity."""
        return str(self.properties.get("name", ""))
    
    @property
    def description(self) -> str:
        """Get the description property of the entity."""
        return str(self.properties.get("description", ""))
    
    @validator("labels")
    def validate_labels(cls, v):
        """Validate the labels field."""
        if not v:
            raise ValueError("Entity must have at least one label")
        return v
    
    @validator("properties")
    def validate_properties(cls, v):
        """Validate the properties field."""
        if not v:
            raise ValueError("Entity must have at least one property")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary format for Neo4j."""
        return {
            "labels": self.labels,
            "properties": self.properties,
        }
    
    @classmethod
    def from_neo4j_record(cls, record: Dict[str, Any]) -> "Entity":
        """
        Create an Entity from a Neo4j record.
        
        Args:
            record: Neo4j record dictionary
            
        Returns:
            Entity: Created entity
        """
        # Extract node ID if available
        node_id = record.get("id")
        
        # Extract labels - handle different formats from Neo4j
        labels: List[str] = []
        if "labels" in record:
            # Direct labels field
            labels = record["labels"]
        elif "label" in record:
            # Single label field
            labels = [record["label"]]
        elif "type" in record and isinstance(record["type"], list):
            # Type field as list
            labels = record["type"]
            
        # Extract properties
        properties = {}
        if "properties" in record:
            # Properties in dedicated field
            properties = record["properties"]
        else:
            # Try to find properties directly in record
            for key, value in record.items():
                if key not in ["id", "labels", "label", "type"]:
                    properties[key] = value
                    
        return cls(
            labels=labels,
            properties=properties,
            node_id=node_id,
        )


class Relationship(BaseModel):
    """Relationship in the knowledge graph."""

    type: str = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(default={}, description="Relationship properties")
    source: Entity = Field(..., description="Source entity")
    target: Entity = Field(..., description="Target entity")
    relationship_id: Optional[int] = Field(None, description="Neo4j relationship ID")
    
    @validator("type")
    def validate_type(cls, v):
        """Validate the type field."""
        if not v:
            raise ValueError("Relationship must have a type")
        return v
    
    @validator("source")
    def validate_source(cls, v):
        """Validate the source field."""
        if not v:
            raise ValueError("Relationship must have a source entity")
        return v
    
    @validator("target")
    def validate_target(cls, v):
        """Validate the target field."""
        if not v:
            raise ValueError("Relationship must have a target entity")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary format for Neo4j."""
        return {
            "type": self.type,
            "properties": self.properties,
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
        }
    
    @classmethod
    def from_neo4j_record(cls, record: Dict[str, Any]) -> "Relationship":
        """
        Create a Relationship from a Neo4j record.
        
        Args:
            record: Neo4j record dictionary
            
        Returns:
            Relationship: Created relationship
        """
        # Extract relationship ID if available
        rel_id = record.get("id")
        
        # Extract relationship type
        rel_type = record.get("type") or record.get("relationship")
        if not rel_type:
            raise ValueError("Record missing relationship type")
            
        # Extract properties
        properties = record.get("properties", {})
        
        # Extract source and target entities
        source_data = record.get("source") or record.get("source_node") or {}
        target_data = record.get("target") or record.get("target_node") or {}
        
        if not source_data or not target_data:
            raise ValueError("Record missing source or target data")
            
        source = Entity.from_neo4j_record(source_data)
        target = Entity.from_neo4j_record(target_data)
            
        return cls(
            type=rel_type,
            properties=properties,
            source=source,
            target=target,
            relationship_id=rel_id,
        )