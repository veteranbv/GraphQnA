"""Database management command for the CLI."""

import argparse
import logging
import time
from typing import Any, Dict, Optional

from graphqna.db import Neo4jDatabase, VectorIndex

logger = logging.getLogger(__name__)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """
    Configure the argument parser for the db command.
    
    Args:
        parser: The parser to configure
    """
    # Create mutually exclusive group for actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    
    # Database actions
    action_group.add_argument(
        "--clear", "-c", action="store_true",
        help="Clear the database (remove all nodes and relationships)"
    )
    action_group.add_argument(
        "--stats", "-s", action="store_true",
        help="Show database statistics"
    )
    action_group.add_argument(
        "--reset-vector-index", "-r", action="store_true",
        help="Reset the vector index for embeddings"
    )
    action_group.add_argument(
        "--check-connection", action="store_true",
        help="Check the database connection"
    )
    action_group.add_argument(
        "--check-index", action="store_true",
        help="Check the vector index configuration"
    )
    action_group.add_argument(
        "--backup", "-b", 
        help="Create a backup of the database to the specified file path"
    )
    
    # Optional arguments
    parser.add_argument(
        "--force", "-f", action="store_true",
        help="Force destructive operations without confirmation"
    )
    parser.add_argument(
        "--dimensions", type=int,
        help="Specify dimensions when rebuilding vector index"
    )


def execute(args: argparse.Namespace) -> int:
    """
    Execute the db command.
    
    Args:
        args: The parsed arguments
        
    Returns:
        Exit code
    """
    db = Neo4jDatabase()
    vector_index = VectorIndex(db=db)
    
    try:
        # Clear database
        if args.clear:
            if not args.force:
                confirm = input("⚠️ This will delete ALL data in the database. Are you sure? (y/N): ")
                if confirm.lower() != "y":
                    print("Operation cancelled")
                    return 0
            
            print("Clearing database...")
            db.clear_database()
            print("✅ Database cleared successfully")
            return 0
            
        # Show database statistics
        if args.stats:
            print("Getting database statistics...")
            stats = db.get_database_stats()
            
            print("\n===== Database Statistics =====")
            print(f"Nodes: {stats['total_nodes']}")
            print(f"Relationships: {stats['total_relationships']}")
            
            if "node_counts_by_label" in stats:
                print("\nNode Counts by Label:")
                for label, count in stats["node_counts_by_label"].items():
                    if label != "Unknown" and count > 0:
                        print(f"{label}: {count}")
                        
            if "relationship_counts_by_type" in stats:
                print("\nRelationship Counts by Type:")
                for rel_type, count in stats["relationship_counts_by_type"].items():
                    if count > 0:
                        print(f"{rel_type}: {count}")
            
            # Get vector index statistics
            vec_stats = vector_index.get_index_stats()
            
            print("\nVector Index:")
            print(f"Name: {vec_stats['index_name']}")
            print(f"Embeddings: {vec_stats.get('embedding_count', 0)}")
            print(f"Dimensions: {vec_stats.get('embedding_dimensions', 0)}")
            return 0
            
        # Reset vector index
        if args.reset_vector_index:
            if not args.force:
                confirm = input("⚠️ This will delete the vector index. Are you sure? (y/N): ")
                if confirm.lower() != "y":
                    print("Operation cancelled")
                    return 0
            
            print("Dropping vector index...")
            success = vector_index.drop_index()
            
            if success:
                print("✅ Vector index dropped successfully")
                
                # Recreate with specified dimensions
                dimensions = args.dimensions or vector_index.settings.vector.dimensions
                print(f"Creating new vector index with {dimensions} dimensions...")
                
                # Update dimensions in settings first
                vector_index.settings.vector.dimensions = dimensions
                
                # Create index
                success = vector_index.ensure_index_exists()
                
                if success:
                    print("✅ Vector index created successfully")
                    return 0
                else:
                    print("❌ Failed to create vector index")
                    return 1
            else:
                print("❌ Failed to drop vector index")
                return 1
                
        # Check connection
        if args.check_connection:
            print("Checking database connection...")
            
            start_time = time.time()
            connected = db.check_connection()
            duration = time.time() - start_time
            
            if connected:
                print(f"✅ Successfully connected to database in {duration:.2f} seconds")
                connection_info = db.get_connection_info()
                
                print("\nConnection Information:")
                print(f"URI: {connection_info['uri']}")
                print(f"Database: {connection_info['database']}")
                print(f"Version: {connection_info.get('version', 'Unknown')}")
                return 0
            else:
                print("❌ Failed to connect to database")
                return 1
                
        # Check vector index
        if args.check_index:
            print("Checking vector index...")
            
            # Get all indexes using our new method
            indexes = db.get_indexes()
            
            print("\nVector Indexes:")
            vector_indexes = [idx for idx in indexes if idx.get("type") == "VECTOR"]
            
            if vector_indexes:
                for idx in vector_indexes:
                    print(f"Name: {idx.get('name', 'Unknown')}")
                    print(f"Labels/Types: {', '.join(idx.get('labels_or_types', ['Unknown']))}")
                    
                    if "properties" in idx:
                        props = idx.get("properties", [])
                        props_str = ', '.join(props) if props else "Unknown"
                        print(f"Properties: {props_str}")
                    
                    if "dimensions" in idx:
                        print(f"Dimensions: {idx.get('dimensions')}")
                    
                    if "similarity_function" in idx:
                        print(f"Similarity Function: {idx.get('similarity_function')}")
                    
                    print("")
            else:
                print("No vector indexes found")
            
            # Check all indexes if we couldn't identify vector indexes specifically
            if not vector_indexes and indexes:
                print("\nAll Indexes:")
                for idx in indexes:
                    print(f"Name: {idx.get('name', 'Unknown')}")
                    print(f"Type: {idx.get('type', 'Unknown')}")
                    
                    if "labels_or_types" in idx:
                        labels = idx.get("labels_or_types", [])
                        labels_str = ', '.join(labels) if labels else "Unknown"
                        print(f"Labels/Types: {labels_str}")
                    
                    print("")
            
            # Check nodes with embeddings
            vec_stats = vector_index.get_index_stats()
            
            print("\nNodes with Embeddings:")
            if vec_stats.get("embedding_count", 0) > 0:
                print(f"Count: {vec_stats.get('embedding_count', 0)}")
                print(f"Dimensions: {vec_stats.get('embedding_dimensions', 'Unknown')}")
            else:
                print("No nodes with embeddings found")
            
            return 0
            
        # Create backup
        if args.backup:
            backup_path = args.backup
            print(f"Creating database backup to {backup_path}...")
            
            success = db.create_backup(backup_path)
            if success:
                print(f"✅ Backup successfully created at {backup_path}")
                return 0
            else:
                print("❌ Failed to create backup")
                return 1
            
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        db.close()
    
    return 0