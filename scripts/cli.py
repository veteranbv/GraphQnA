#!/usr/bin/env python3
"""
Command-line interface for GraphQnA.

This script provides commands for:
1. Ingesting documents into the knowledge graph
2. Querying the knowledge graph for answers
3. Managing the database and vector indexes
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase, VectorIndex
from graphqna.ingest import IngestionPipeline
from graphqna.retrieval import RetrievalService, RetrievalMethod
from graphqna.models.response import QueryResponse

# Set up logging
settings = get_settings()
LOG_FILE = settings.logs_dir / "graphqna.log"
settings.logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("graphqna.cli")


def format_response(response: QueryResponse, show_context: bool = False) -> str:
    """
    Format a query response for display.
    
    Args:
        response: The query response to format
        show_context: Whether to show the retrieved context
        
    Returns:
        Formatted response as string
    """
    # Start with a separator
    output = "\n" + "=" * 80 + "\n"
    
    # Add the answer
    output += f"📝 Answer:\n{response.answer}\n\n"
    
    # Add timing information
    output += f"⏱️  Response time: {response.query_time:.2f}s\n"
    output += f"🔍 Retrieval method: {response.retrieval_method}\n"
    
    # Add context if requested
    if show_context and response.context:
        output += "\n" + "=" * 40 + "\n"
        output += "Context:\n" + "=" * 40 + "\n"
        
        # Handle different context types
        if isinstance(response.context, list):
            # Vector or Graph results
            for i, ctx in enumerate(response.context[:3]):  # Limit to first 3 for brevity
                output += f"Chunk {i+1}:\n"
                
                # Extract text based on context type
                if hasattr(ctx, "text"):
                    text = ctx.text
                elif hasattr(ctx, "chunk_text"):
                    text = ctx.chunk_text
                else:
                    text = str(ctx)
                    
                # Add score if available
                if hasattr(ctx, "score"):
                    output += f"Score: {ctx.score:.4f}\n"
                    
                # Add text
                output += f"{text[:300]}{'...' if len(text) > 300 else ''}\n"
                
                # Add entities if available
                if hasattr(ctx, "entities") and ctx.entities:
                    output += "Entities:\n"
                    for entity in ctx.entities[:5]:  # Limit entities
                        output += f"  - {entity.primary_label}: {entity.name}\n"
                        
                output += "-" * 40 + "\n"
        else:
            # Knowledge Graph results
            kg_result = response.context
            output += f"Generated Cypher query:\n{kg_result.query}\n\n"
            
            if kg_result.entities:
                output += "Entities found:\n"
                for entity in kg_result.entities[:5]:  # Limit entities
                    output += f"  - {entity.primary_label}: {entity.name}\n"
            
            if kg_result.raw_results:
                output += f"\nResults: {len(kg_result.raw_results)} records returned\n"
    
    # End with a separator
    output += "=" * 80
    
    return output


def interactive_mode(service: RetrievalService, **kwargs):
    """
    Run the query system in interactive mode.
    
    Args:
        service: The retrieval service to use
        **kwargs: Additional keyword arguments
    """
    method = kwargs.get("method", RetrievalMethod.GRAPHRAG)
    top_k = kwargs.get("top_k", settings.chunking.vector_top_k)
    show_context = kwargs.get("show_context", False)
    
    print("\n=== GraphQnA - Knowledge Graph QA System ===")
    print("Type 'exit', 'quit', or 'q' to exit.")
    print("Type 'vector', 'graphrag', 'kg', 'enhanced_kg', or 'hybrid' to change retrieval method.")
    print(f"Current method: {method}")
    print("Type 'context' to toggle showing context in responses.")
    print(f"Show context: {show_context}")
    print("Type 'help' for more information.")
    
    while True:
        try:
            # Get user input
            query = input("\nQuestion: ").strip()
            
            # Skip empty queries
            if not query:
                continue
                
            # Check for exit command
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break
                
            # Check for method change command
            if query.lower() in ["vector", "graphrag", "kg", "enhanced_kg", "hybrid"]:
                method = query.lower()
                print(f"Retrieval method changed to: {method}")
                continue
                
            # Check for context toggle command
            if query.lower() == "context":
                show_context = not show_context
                print(f"Show context: {show_context}")
                continue
                
            # Check for help command
            if query.lower() == "help":
                print("\n=== Help ===")
                print("Commands:")
                print("  'exit', 'quit', 'q': Exit the program")
                print("  'vector', 'graphrag', 'kg', 'enhanced_kg', 'hybrid': Change retrieval method")
                print("  'context': Toggle showing context in responses")
                print("  'help': Show this help message")
                continue
                
            # Process the query
            print("Thinking...")
            response = service.answer_question(
                query=query,
                method=method,
                top_k=top_k,
            )
            
            # Display the response
            print(format_response(response, show_context=show_context))
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


async def ingest_command(args):
    """
    Handle the 'ingest' command.
    
    Args:
        args: Command-line arguments
    """
    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    # Create ingestion pipeline
    pipeline = IngestionPipeline()
    
    try:
        # Process the document
        print(f"Ingesting document: {file_path}")
        result = await pipeline.ingest_document(
            file_path=file_path,
            clear_database=args.clear,
            advanced_kg=not args.simple,
        )
        
        # Display the result
        if result["status"] == "success":
            print("\n✅ Document ingestion completed successfully!")
            print(f"Time taken: {result['time_taken']:.2f} seconds")
            
            # Display database statistics
            if "database_stats" in result:
                stats = result["database_stats"]
                print("\nDatabase Statistics:")
                print(f"  Nodes: {stats['total_nodes']}")
                print(f"  Relationships: {stats['total_relationships']}")
                
                # Display node counts by label
                if "node_counts_by_label" in stats:
                    print("\nNode Counts by Label:")
                    for label, count in stats["node_counts_by_label"].items():
                        if label != "Unknown" and count > 0:
                            print(f"  {label}: {count}")
            
            # Display vector index statistics
            if "vector_index" in result:
                vec_stats = result["vector_index"]
                print("\nVector Index:")
                print(f"  Name: {vec_stats['index_name']}")
                print(f"  Embeddings: {vec_stats.get('embedding_count', 0)}")
                print(f"  Dimensions: {vec_stats.get('embedding_dimensions', 0)}")
            
            return 0
        else:
            print(f"\n❌ Document ingestion failed: {result.get('message', 'Unknown error')}")
            if "detail" in result:
                print(f"Detail: {result['detail']}")
            return 1
    except Exception as e:
        print(f"\n❌ Error during ingestion: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        pipeline.db.close()


def query_command(args):
    """
    Handle the 'query' command.
    
    Args:
        args: Command-line arguments
    """
    # Create retrieval service
    service = RetrievalService()
    
    try:
        # Interactive mode
        if args.interactive:
            interactive_mode(
                service=service,
                method=args.method,
                top_k=args.top_k,
                show_context=args.context,
            )
            return 0
            
        # Direct question mode
        if args.query:
            # Process the query
            print("Processing query...")
            response = service.answer_question(
                query=args.query,
                method=args.method,
                top_k=args.top_k,
            )
            
            # Display the response
            print(format_response(response, show_context=args.context))
            return 0
        else:
            print("Error: No query provided. Use --query or --interactive.")
            return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        service.close()


def db_command(args):
    """
    Handle the 'db' command.
    
    Args:
        args: Command-line arguments
    """
    # Create database connection
    db = Neo4jDatabase()
    
    try:
        # Clear database
        if args.clear:
            print("Clearing database...")
            db.clear_database()
            print("Database cleared successfully!")
            return 0
            
        # Show database statistics
        if args.stats:
            print("Getting database statistics...")
            stats = db.get_database_stats()
            
            print("\nDatabase Statistics:")
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
            vector_index = VectorIndex(db=db)
            vec_stats = vector_index.get_index_stats()
            
            print("\nVector Index:")
            print(f"Name: {vec_stats['index_name']}")
            print(f"Embeddings: {vec_stats.get('embedding_count', 0)}")
            print(f"Dimensions: {vec_stats.get('embedding_dimensions', 0)}")
            
            return 0
            
        # Default action for db command
        print("No action specified. Use --clear or --stats.")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        db.close()


def main():
    """Main entry point for the CLI."""
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="GraphQnA - Knowledge Graph Question Answering System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create parser for the "ingest" command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest a document into the knowledge graph"
    )
    ingest_parser.add_argument(
        "--file", "-f", required=True, help="Path to the document file"
    )
    ingest_parser.add_argument(
        "--clear", "-c", action="store_true", help="Clear the database before ingestion"
    )
    ingest_parser.add_argument(
        "--simple", "-s", action="store_true", help="Use simple mode without schema enforcement"
    )
    
    # Create parser for the "query" command
    query_parser = subparsers.add_parser(
        "query", help="Query the knowledge graph for answers"
    )
    query_parser.add_argument(
        "query", nargs="?", help="Question to ask"
    )
    query_parser.add_argument(
        "--method", "-m", default="graphrag", choices=["vector", "graphrag", "kg", "enhanced_kg", "hybrid"],
        help="Retrieval method to use"
    )
    query_parser.add_argument(
        "--top-k", "-k", type=int, help="Number of results to retrieve"
    )
    query_parser.add_argument(
        "--context", "-c", action="store_true", help="Show retrieved context"
    )
    query_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    
    # Create parser for the "db" command
    db_parser = subparsers.add_parser(
        "db", help="Database management commands"
    )
    db_parser.add_argument(
        "--clear", action="store_true", help="Clear the database"
    )
    db_parser.add_argument(
        "--stats", action="store_true", help="Show database statistics"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "ingest":
        return asyncio.run(ingest_command(args))
    elif args.command == "query":
        return query_command(args)
    elif args.command == "db":
        return db_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())