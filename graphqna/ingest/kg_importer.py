"""Knowledge graph importer for Neo4j."""

import logging
from typing import Dict, List, Optional, Any, Tuple

from neo4j import Result

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.ingest.kg_builder import KnowledgeGraph, Node, Relationship, Property

logger = logging.getLogger(__name__)


class KnowledgeGraphImporter:
    """
    Import knowledge graphs into Neo4j.
    
    This class handles importing nodes and relationships from a knowledge graph
    into a Neo4j database.
    """
    
    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the knowledge graph importer.
        
        Args:
            db: Neo4j database connection
            settings: Application settings
        """
        self.db = db or Neo4jDatabase()
        self.settings = settings or get_settings()
        
    def import_knowledge_graph(self, kg: KnowledgeGraph, source_id: Optional[str] = None) -> Tuple[int, int]:
        """
        Import a knowledge graph into Neo4j.
        
        Args:
            kg: The knowledge graph to import
            source_id: Optional source identifier (e.g., document ID)
            
        Returns:
            Tuple of (nodes_imported, relationships_imported)
        """
        nodes_imported = 0
        rels_imported = 0
        
        try:
            # Import nodes first
            for node in kg.nodes:
                if self._import_node(node, source_id):
                    nodes_imported += 1
                
            # Then import relationships
            for rel in kg.relationships:
                if self._import_relationship(rel, source_id):
                    rels_imported += 1
                    
            logger.info(f"Imported {nodes_imported} nodes and {rels_imported} relationships")
            return (nodes_imported, rels_imported)
        except Exception as e:
            logger.error(f"Error importing knowledge graph: {str(e)}")
            return (nodes_imported, rels_imported)
    
    def _import_node(self, node: Node, source_id: Optional[str] = None) -> bool:
        """
        Import a node into Neo4j.
        
        Args:
            node: The node to import
            source_id: Optional source identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert properties to a dictionary
        properties = self._node_properties_to_dict(node, source_id)
        
        # Fix node type name - remove spaces and ensure valid format
        node_type = self._format_node_type(node.type)
        
        # Create Cypher query for merge operation
        query = f"""
        MERGE (n:{node_type} {{id: $id}})
        ON CREATE SET n += $properties
        ON MATCH SET n += $properties
        RETURN n
        """
        
        try:
            with self.db.session() as session:
                result = session.run(
                    query,
                    id=node.id,
                    properties=properties,
                )
                # Check if node was created
                summary = result.consume()
                return summary.counters.nodes_created > 0 or summary.counters.properties_set > 0
        except Exception as e:
            logger.error(f"Error importing node {node.id}: {str(e)}")
            return False
            
    def _format_node_type(self, node_type: str) -> str:
        """
        Format node type to be Neo4j-compatible.
        
        Args:
            node_type: Node type/label to format
            
        Returns:
            str: Formatted node type
        """
        # Replace spaces with nothing to create CamelCase
        if ' ' in node_type:
            words = node_type.split()
            return ''.join(word.capitalize() for word in words)
        return node_type
    
    def _import_relationship(self, rel: Relationship, source_id: Optional[str] = None) -> bool:
        """
        Import a relationship into Neo4j.
        
        Args:
            rel: The relationship to import
            source_id: Optional source identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert properties to a dictionary
        properties = self._rel_properties_to_dict(rel, source_id)
        
        # Format node and relationship types to be Neo4j-compatible
        source_type = self._format_node_type(rel.source.type)
        target_type = self._format_node_type(rel.target.type)
        rel_type = self._format_rel_type(rel.type)
        
        # Create Cypher query for merge operation
        query = f"""
        MATCH (source:{source_type} {{id: $source_id}})
        MATCH (target:{target_type} {{id: $target_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        ON CREATE SET r += $properties
        ON MATCH SET r += $properties
        RETURN r
        """
        
        try:
            with self.db.session() as session:
                result = session.run(
                    query,
                    source_id=rel.source.id,
                    target_id=rel.target.id,
                    properties=properties,
                )
                # Check if relationship was created
                summary = result.consume()
                return summary.counters.relationships_created > 0 or summary.counters.properties_set > 0
        except Exception as e:
            logger.error(f"Error importing relationship from {rel.source.id} to {rel.target.id}: {str(e)}")
            return False
            
    def _format_rel_type(self, rel_type: str) -> str:
        """
        Format relationship type to be Neo4j-compatible.
        
        Args:
            rel_type: Relationship type to format
            
        Returns:
            str: Formatted relationship type
        """
        # Convert to uppercase and replace spaces with underscores
        if ' ' in rel_type:
            return rel_type.replace(' ', '_').upper()
        return rel_type.upper()
    
    def _node_properties_to_dict(self, node: Node, source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert node properties to a dictionary.
        
        Args:
            node: The node with properties
            source_id: Optional source identifier
            
        Returns:
            Dict: Node properties as a dictionary
        """
        # Start with ID and name properties
        properties = {
            "id": node.id,
            "name": node.id,  # Use ID as name by default
        }
        
        # Add source ID if provided
        if source_id:
            properties["sourceId"] = source_id
            
        # Add custom properties
        if node.properties:
            for prop in node.properties:
                key = self._format_property_key(prop.key)
                properties[key] = prop.value
                
                # If there's a name property, update the name
                if key.lower() == "name":
                    properties["name"] = prop.value
                    
        return properties
    
    def _rel_properties_to_dict(self, rel: Relationship, source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert relationship properties to a dictionary.
        
        Args:
            rel: The relationship with properties
            source_id: Optional source identifier
            
        Returns:
            Dict: Relationship properties as a dictionary
        """
        # Start with basic properties
        properties = {}
        
        # Add source ID if provided
        if source_id:
            properties["sourceId"] = source_id
            
        # Add custom properties
        if rel.properties:
            for prop in rel.properties:
                key = self._format_property_key(prop.key)
                properties[key] = prop.value
                    
        return properties
    
    def _format_property_key(self, key: str) -> str:
        """
        Format property key to camelCase.
        
        Args:
            key: Property key to format
            
        Returns:
            str: Formatted property key
        """
        words = key.split()
        if not words:
            return key
            
        first_word = words[0].lower()
        capitalized_words = [word.capitalize() for word in words[1:]]
        return "".join([first_word] + capitalized_words)