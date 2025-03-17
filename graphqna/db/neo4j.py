"""Neo4j database interface with connection management and error handling."""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union, Generator, Callable, TypeVar, cast

from neo4j import (
    Driver,
    GraphDatabase,
    Session,
    Result,
    Transaction,
    AsyncDriver,
    AsyncSession,
    AsyncTransaction,
)

from graphqna.config import Settings, get_settings

# Type variables for generic functions
T = TypeVar("T")
R = TypeVar("R")

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base class for all database-related errors."""

    pass


class ConnectionError(DatabaseError):
    """Raised when connection to the database fails."""

    pass


class QueryError(DatabaseError):
    """Raised when a query fails."""

    pass


class Neo4jDatabase:
    """
    Neo4j database interface with connection management and error handling.
    
    This class follows the Singleton pattern to ensure only one database connection
    exists throughout the application lifecycle.
    """

    _instance = None
    _driver = None
    _async_driver = None
    
    def is_connected(self) -> bool:
        """
        Check if database is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if self._driver is None:
                self.connect()
            self._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False
            
    def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results as a list of dictionaries.
        
        Args:
            query: Cypher query to execute
            params: Parameters for the query (optional)
            
        Returns:
            List of record dictionaries
        """
        return self.execute_read(query, params)

    def __new__(cls, settings: Optional[Settings] = None):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Neo4jDatabase, cls).__new__(cls)
            cls._settings = settings or get_settings()
            cls._driver = None
            cls._async_driver = None
        return cls._instance

    def connect(self) -> Driver:
        """
        Establish connection to Neo4j database.
        
        Returns:
            Driver: Neo4j driver instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    self._settings.neo4j.uri,
                    auth=(self._settings.neo4j.username, self._settings.neo4j.password),
                )
                # Verify connectivity
                self._driver.verify_connectivity()
                logger.info("✅ Successfully connected to Neo4j database")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Neo4j database: {str(e)}")
                raise ConnectionError(f"Failed to connect to Neo4j: {str(e)}") from e
        return self._driver

    async def connect_async(self) -> AsyncDriver:
        """
        Establish async connection to Neo4j database.
        
        Returns:
            AsyncDriver: Neo4j async driver instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._async_driver is None:
            try:
                self._async_driver = GraphDatabase.driver(
                    self._settings.neo4j.uri,
                    auth=(self._settings.neo4j.username, self._settings.neo4j.password),
                )
                # Test connectivity
                await self._async_driver.verify_connectivity()
                logger.info("✅ Successfully connected to Neo4j database (async)")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Neo4j database (async): {str(e)}")
                raise ConnectionError(f"Failed to connect to Neo4j: {str(e)}") from e
        return self._async_driver

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
            
        if self._async_driver is not None:
            self._async_driver.close()
            self._async_driver = None
            logger.info("Neo4j async connection closed")

    def get_driver(self) -> Driver:
        """
        Get the Neo4j driver instance, establishing connection if needed.
        
        Returns:
            Driver: Neo4j driver instance
        """
        if self._driver is None:
            return self.connect()
        return self._driver

    async def get_async_driver(self) -> AsyncDriver:
        """
        Get the Neo4j async driver instance, establishing connection if needed.
        
        Returns:
            AsyncDriver: Neo4j async driver instance
        """
        if self._async_driver is None:
            return await self.connect_async()
        return self._async_driver

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Get a database session using context manager pattern.
        
        Yields:
            Session: Neo4j session
            
        Example:
            ```python
            with db.session() as session:
                result = session.run("MATCH (n) RETURN count(n)")
            ```
        """
        session = self.get_driver().session(database=self._settings.neo4j.database)
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def transaction(self) -> Generator[Transaction, None, None]:
        """
        Execute operations in a transaction.
        
        Yields:
            Transaction: Neo4j transaction
            
        Example:
            ```python
            with db.transaction() as tx:
                tx.run("CREATE (n:Node {name: $name})", name="Test")
            ```
        """
        with self.session() as session:
            tx = session.begin_transaction()
            try:
                yield tx
                tx.commit()
            except Exception as e:
                tx.rollback()
                raise QueryError(f"Transaction failed: {str(e)}") from e

    def execute_read(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query and return results as a list of dictionaries.
        
        Args:
            query: Cypher query to execute
            params: Parameters for the query (optional)
            
        Returns:
            List of record dictionaries
            
        Raises:
            QueryError: If query execution fails
        """
        try:
            with self.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def execute_write(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a write query and return the last record if available.
        
        Args:
            query: Cypher query to execute
            params: Parameters for the query (optional)
            
        Returns:
            Last record as dictionary or None
            
        Raises:
            QueryError: If query execution fails
        """
        try:
            with self.session() as session:
                result = session.run(query, params or {})
                records = list(result)
                return records[-1].data() if records else None
        except Exception as e:
            error_msg = f"Write operation failed: {str(e)}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def run_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Result:
        """
        Run a Cypher query and return the results.
        
        Args:
            query: Cypher query to execute
            params: Parameters for the query (optional)
            
        Returns:
            Result: Neo4j result object
            
        Raises:
            QueryError: If query execution fails
        """
        try:
            with self.session() as session:
                return session.run(query, params or {})
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def count_nodes(self, label: Optional[str] = None) -> int:
        """
        Count nodes in the database, optionally filtered by label.
        
        Args:
            label: Node label to filter by (optional)
            
        Returns:
            int: Number of nodes
        """
        query = "MATCH (n{}) RETURN count(n) as count"
        label_part = f":{label}" if label else ""
        query = query.format(label_part)
        
        with self.session() as session:
            result = session.run(query)
            return result.single()["count"]

    def count_relationships(self, type_name: Optional[str] = None) -> int:
        """
        Count relationships in the database, optionally filtered by type.
        
        Args:
            type_name: Relationship type to filter by (optional)
            
        Returns:
            int: Number of relationships
        """
        query = "MATCH ()-[r{}]->() RETURN count(r) as count"
        type_part = f":{type_name}" if type_name else ""
        query = query.format(type_part)
        
        with self.session() as session:
            result = session.run(query)
            return result.single()["count"]

    def clear_database(self) -> None:
        """
        Clear all data from the database.
        
        Raises:
            QueryError: If operation fails
        """
        try:
            # First count nodes to confirm what we're deleting
            with self.session() as session:
                node_count = self.count_nodes()
                rel_count = self.count_relationships()

                logger.info(f"Found {node_count} nodes and {rel_count} relationships to delete.")

                # Delete all data
                session.run("MATCH (n) DETACH DELETE n")

                # Verify deletion
                remaining = self.count_nodes()

                if remaining == 0:
                    logger.info("✅ Database successfully cleared!")
                else:
                    warning_msg = f"⚠️ Database clear incomplete. {remaining} nodes remaining."
                    logger.warning(warning_msg)
                    raise QueryError(warning_msg)
        except Exception as e:
            if not isinstance(e, QueryError):
                error_msg = f"Error clearing database: {str(e)}"
                logger.error(error_msg)
                raise QueryError(error_msg) from e
            raise

    def check_index_exists(self, index_name: str) -> bool:
        """
        Check if a vector index exists in the database.
        
        Args:
            index_name: Name of the index to check
            
        Returns:
            bool: True if index exists, False otherwise
        """
        try:
            with self.session() as session:
                # Try for Neo4j 4.x and later
                try:
                    result = session.run(
                        "SHOW INDEXES WHERE name = $index_name",
                        index_name=index_name,
                    )
                    indexes = list(result)
                    if indexes:
                        return True
                except Exception:
                    # Try alternative for Neo4j 3.x
                    try:
                        result = session.run(
                            "CALL db.indexes() YIELD name, type WHERE name = $index_name RETURN count(*) as count",
                            index_name=index_name,
                        )
                        count = result.single()["count"]
                        return count > 0
                    except Exception:
                        # Fall back to a general query
                        result = session.run("CALL db.indexes()")
                        for record in result:
                            if index_name in str(record):
                                return True
            return False
        except Exception as e:
            logger.error(f"Error checking for index existence: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database.
        
        Returns:
            Dict with database statistics
        """
        try:
            # Node label counts
            node_query = """
            MATCH (n)
            RETURN labels(n) AS labels, count(*) AS count
            """
            
            # Relationship type counts
            rel_query = """
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(*) AS count
            """
            
            with self.session() as session:
                # Get node counts by label
                node_results = session.run(node_query).data()
                
                # Get relationship counts by type
                rel_results = session.run(rel_query).data()
                
            # Process node label counts
            node_counts = {}
            for record in node_results:
                for label in record.get("labels", []):
                    if label not in node_counts:
                        node_counts[label] = 0
                    node_counts[label] += record.get("count", 0)
            
            # Process relationship type counts
            rel_counts = {}
            for record in rel_results:
                rel_type = record.get("type")
                if rel_type:
                    rel_counts[rel_type] = record.get("count", 0)
            
            # Calculate totals
            total_nodes = sum(node_counts.values())
            total_relationships = sum(rel_counts.values())
            
            return {
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
                "node_counts_by_label": node_counts,
                "relationship_counts_by_type": rel_counts,
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {
                "error": str(e),
                "total_nodes": 0,
                "total_relationships": 0,
                "node_counts_by_label": {},
                "relationship_counts_by_type": {},
            }
            
    def check_connection(self) -> bool:
        """
        Check if connection to the database is successful.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            driver = self.get_driver()
            driver.verify_connectivity()
            
            # Run a simple query to verify database access
            with self.session() as session:
                result = session.run("RETURN 1 as test").single()
                return result is not None and result.get("test") == 1
                
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False
            
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the database connection.
        
        Returns:
            Dict with connection information
        """
        try:
            connection_info = {
                "uri": self._settings.neo4j.uri,
                "database": self._settings.neo4j.database,
                "username": self._settings.neo4j.username,
                "connected": False,
                "version": "Unknown",
                "edition": "Unknown",
            }
            
            # Check connection and get version info
            if self._driver:
                try:
                    # Get Neo4j version
                    with self.session() as session:
                        result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN * LIMIT 1").single()
                        if result:
                            connection_info["version"] = result.get("versions", ["Unknown"])[0]
                            connection_info["edition"] = result.get("edition", "Unknown")
                            connection_info["connected"] = True
                except:
                    # Try alternative query for older Neo4j versions
                    try:
                        with self.session() as session:
                            result = session.run("CALL dbms.getTXMetaData()").consume()
                            connection_info["connected"] = True
                    except Exception as e:
                        logger.warning(f"Could not get Neo4j version info: {str(e)}")
            
            return connection_info
            
        except Exception as e:
            logger.error(f"Error getting connection info: {str(e)}")
            return {
                "uri": self._settings.neo4j.uri,
                "database": self._settings.neo4j.database,
                "connected": False,
                "error": str(e)
            }
            
    def get_indexes(self) -> List[Dict[str, Any]]:
        """
        Get list of all indexes in the database.
        
        Returns:
            List of dictionaries with index information
        """
        try:
            indexes = []
            
            with self.session() as session:
                # Try Neo4j 4.x+ approach
                try:
                    result = session.run("""
                        SHOW INDEXES
                        YIELD name, type, labelsOrTypes, properties, options
                        RETURN *
                    """).data()
                    
                    for idx in result:
                        index_info = {
                            "name": idx.get("name", "Unknown"),
                            "type": idx.get("type", "Unknown"),
                            "labels_or_types": idx.get("labelsOrTypes", []),
                            "properties": idx.get("properties", []),
                        }
                        
                        # Extract additional info from options
                        options = idx.get("options", {})
                        if "indexConfig" in options:
                            config = options["indexConfig"]
                            if "vector.dimensions" in config:
                                index_info["dimensions"] = config["vector.dimensions"]
                            if "vector.similarity_function" in config:
                                index_info["similarity_function"] = config["vector.similarity_function"]
                                
                        indexes.append(index_info)
                        
                except Exception as e1:
                    logger.debug(f"Could not get indexes with SHOW INDEXES: {str(e1)}")
                    
                    # Try Neo4j 3.x approach
                    try:
                        result = session.run("""
                            CALL db.indexes()
                            YIELD description, label, properties, state
                            RETURN *
                        """).data()
                        
                        for idx in result:
                            indexes.append({
                                "name": idx.get("description", "Unknown"),
                                "type": "Unknown",  # Not available in this format
                                "labels_or_types": [idx.get("label", "Unknown")],
                                "properties": idx.get("properties", []),
                                "state": idx.get("state", "Unknown")
                            })
                            
                    except Exception as e2:
                        logger.debug(f"Could not get indexes with db.indexes(): {str(e2)}")
                        
                        # Last resort for any Neo4j version
                        try:
                            # Just get a list of all indexes as strings
                            result = session.run("CALL db.indexes()").data()
                            for idx in result:
                                indexes.append({
                                    "name": str(idx),
                                    "raw_data": idx
                                })
                        except Exception as e3:
                            logger.error(f"All methods to get indexes failed: {str(e3)}")
            
            return indexes
            
        except Exception as e:
            logger.error(f"Error getting indexes: {str(e)}")
            return []
            
    def create_backup(self, output_path: str) -> bool:
        """
        Create a backup of the database.
        
        This exports all nodes and relationships as Cypher statements that can be
        reimported later. It does not use the Neo4j dump functionality, which would
        require admin access to the database server.
        
        Args:
            output_path: Path to save the backup file
            
        Returns:
            bool: True if backup was successful, False otherwise
        """
        try:
            logger.info(f"Creating database backup to {output_path}")
            
            # Count total nodes and relationships first
            total_nodes = self.count_nodes()
            total_relationships = self.count_relationships()
            
            logger.info(f"Backing up {total_nodes} nodes and {total_relationships} relationships")
            
            # Get all node labels
            with self.session() as session:
                node_labels_result = session.run("""
                    CALL db.labels() YIELD label
                    RETURN collect(label) AS labels
                """).single()
                
                node_labels = node_labels_result["labels"] if node_labels_result else []
                
                # Get all relationship types
                rel_types_result = session.run("""
                    CALL db.relationshipTypes() YIELD relationshipType
                    RETURN collect(relationshipType) AS types
                """).single()
                
                rel_types = rel_types_result["types"] if rel_types_result else []
            
            # Open file for writing
            with open(output_path, "w") as f:
                # Write header with metadata
                f.write("// Neo4j Graph Backup\n")
                f.write(f"// Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// Database: {self._settings.neo4j.database}\n")
                f.write(f"// Total Nodes: {total_nodes}\n")
                f.write(f"// Total Relationships: {total_relationships}\n\n")
                
                # Export nodes by label
                nodes_exported = 0
                for label in node_labels:
                    # Get nodes for this label
                    with self.session() as session:
                        # Query for nodes with this label, 1000 at a time
                        f.write(f"// Exporting nodes with label: {label}\n")
                        
                        # Use SKIP/LIMIT for batching
                        batch_size = 1000
                        skip = 0
                        
                        while True:
                            result = session.run(f"""
                                MATCH (n:{label})
                                RETURN n
                                SKIP {skip} LIMIT {batch_size}
                            """).data()
                            
                            if not result:
                                break
                                
                            # Write CREATE statements for each node
                            for record in result:
                                node = record["n"]
                                # Get node properties as a dictionary
                                props = dict(node)
                                
                                # Skip large properties (like embeddings) to keep backup manageable
                                if "embedding" in props and isinstance(props["embedding"], list) and len(props["embedding"]) > 20:
                                    f.write(f"// Skipping embedding property with {len(props['embedding'])} dimensions\n")
                                    del props["embedding"]
                                
                                # Create Cypher statement for this node
                                props_str = ", ".join([f"{k}: {repr(v)}" for k, v in props.items()])
                                node_id = node.element_id  # Use element_id instead of id
                                
                                f.write(f"CREATE (n_{node_id}:{label} {{{props_str}}});\n")
                                nodes_exported += 1
                                
                            skip += batch_size
                            
                            # Log progress
                            if skip % 5000 == 0:
                                logger.info(f"Exported {nodes_exported} nodes so far...")
                    
                    f.write("\n")
                
                # Export relationship types
                rels_exported = 0
                for rel_type in rel_types:
                    # Get relationships for this type
                    with self.session() as session:
                        # Query for relationships with this type, 1000 at a time
                        f.write(f"// Exporting relationships with type: {rel_type}\n")
                        
                        # Use SKIP/LIMIT for batching
                        batch_size = 1000
                        skip = 0
                        
                        while True:
                            result = session.run(f"""
                                MATCH (s)-[r:{rel_type}]->(t)
                                RETURN elementId(s) as source_id, elementId(t) as target_id, r
                                SKIP {skip} LIMIT {batch_size}
                            """).data()
                            
                            if not result:
                                break
                                
                            # Write CREATE statements for each relationship
                            for record in result:
                                rel = record["r"]
                                source_id = record["source_id"]
                                target_id = record["target_id"]
                                
                                # Get relationship properties as a dictionary
                                props = dict(rel)
                                
                                # Skip large properties to keep backup manageable
                                if "embedding" in props and isinstance(props["embedding"], list) and len(props["embedding"]) > 20:
                                    f.write(f"// Skipping embedding property with {len(props['embedding'])} dimensions\n")
                                    del props["embedding"]
                                
                                # Create Cypher statement for this relationship
                                props_str = ", ".join([f"{k}: {repr(v)}" for k, v in props.items()])
                                
                                f.write(f"MATCH (s) WHERE elementId(s) = {source_id}\n")
                                f.write(f"MATCH (t) WHERE elementId(t) = {target_id}\n")
                                f.write(f"CREATE (s)-[:{rel_type} {{{props_str}}}]->(t);\n\n")
                                rels_exported += 1
                                
                            skip += batch_size
                            
                            # Log progress
                            if skip % 5000 == 0:
                                logger.info(f"Exported {rels_exported} relationships so far...")
                    
                    f.write("\n")
                
                # Write summary
                f.write(f"// Backup complete: {nodes_exported} nodes and {rels_exported} relationships exported\n")
            
            logger.info(f"✅ Backup completed successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating database backup: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False