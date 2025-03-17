"""Query command for the CLI."""

import argparse
import json
import logging
import time
from typing import Any, Dict, Optional

from graphqna.config import get_settings
from graphqna.retrieval import RetrievalService, RetrievalMethod
from graphqna.models.response import QueryResponse

logger = logging.getLogger(__name__)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """
    Configure the argument parser for the query command.
    
    Args:
        parser: The parser to configure
    """
    parser.add_argument(
        "query", nargs="?", 
        help="Question to ask (not needed if --interactive or --file is used)"
    )
    parser.add_argument(
        "--method", "-m", 
        default="graphrag", choices=["vector", "graphrag", "kg", "enhanced_kg", "hybrid"],
        help="Retrieval method to use (default: graphrag)"
    )
    parser.add_argument(
        "--top-k", "-k", type=int,
        help="Number of results to retrieve"
    )
    parser.add_argument(
        "--context", "-c", action="store_true",
        help="Show retrieved context"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--file", "-f",
        help="Read queries from a file, one per line"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write results to a file in JSON format"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed information about the query process"
    )


def execute(args: argparse.Namespace) -> int:
    """
    Execute the query command.
    
    Args:
        args: The parsed arguments
        
    Returns:
        Exit code
    """
    # Create retrieval service
    service = RetrievalService()
    
    try:
        # Interactive mode
        if args.interactive:
            return interactive_mode(
                service=service,
                method=args.method,
                top_k=args.top_k,
                show_context=args.context,
                verbose=args.verbose,
            )
            
        # File mode
        if args.file:
            return file_mode(
                service=service,
                file_path=args.file,
                method=args.method,
                top_k=args.top_k,
                show_context=args.context,
                output_file=args.output,
                verbose=args.verbose,
            )
            
        # Direct question mode
        if args.query:
            # Process the query
            if args.verbose:
                print("Processing query...")
                start_time = time.time()
                
            # Actually run the query
            response = service.answer_question(
                query=args.query,
                method=args.method,
                top_k=args.top_k,
            )
            
            if args.verbose and response.query_time == 0:
                response.query_time = time.time() - start_time
                
            # Display the response
            if args.output:
                # Write to file
                write_to_file(response, args.output)
                print(f"Result written to {args.output}")
            else:
                # Display to console
                print(format_response(response, show_context=args.context))
                
            return 0
            
        # No action specified
        print("Error: No query provided. Use a query argument, --interactive, or --file.")
        return 1
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            print(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        service.close()


def interactive_mode(
    service: RetrievalService,
    method: str = "graphrag",
    top_k: Optional[int] = None,
    show_context: bool = False,
    verbose: bool = False,
) -> int:
    """
    Run the query system in interactive mode.
    
    Args:
        service: The retrieval service to use
        method: Retrieval method to use
        top_k: Number of results to retrieve
        show_context: Whether to show context
        verbose: Whether to show verbose output
        
    Returns:
        Exit code
    """
    settings = get_settings()
    
    if top_k is None:
        top_k = settings.chunking.vector_top_k
        
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
                print("  'vector', 'graphrag', 'kg': Change retrieval method")
                print("  'context': Toggle showing context in responses")
                print("  'help': Show this help message")
                print("  '!clear': Clear the screen")
                print("  '!save <filename>': Save the next response to a file")
                continue
                
            # Check for clear command
            if query.lower() == "!clear":
                print("\033c", end="")  # Clear screen
                continue
                
            # Check for save command
            save_to_file = None
            if query.lower().startswith("!save "):
                save_to_file = query[6:].strip()
                print(f"Next response will be saved to {save_to_file}")
                query = input("\nQuestion: ").strip()
                
            # Process the query
            print("Thinking...")
            response = service.answer_question(
                query=query,
                method=method,
                top_k=top_k,
            )
            
            # Save to file if requested
            if save_to_file:
                write_to_file(response, save_to_file)
                print(f"Response saved to {save_to_file}")
            
            # Display the response
            print(format_response(response, show_context=show_context))
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            if verbose:
                import traceback
                print(traceback.format_exc())
    
    return 0


def file_mode(
    service: RetrievalService,
    file_path: str,
    method: str = "graphrag",
    top_k: Optional[int] = None,
    show_context: bool = False,
    output_file: Optional[str] = None,
    verbose: bool = False,
) -> int:
    """
    Run the query system in file mode.
    
    Args:
        service: The retrieval service to use
        file_path: Path to the file with queries
        method: Retrieval method to use
        top_k: Number of results to retrieve
        show_context: Whether to show context
        output_file: File to write results to
        verbose: Whether to show verbose output
        
    Returns:
        Exit code
    """
    try:
        # Read queries from file
        with open(file_path, "r") as f:
            queries = [line.strip() for line in f if line.strip()]
            
        if not queries:
            print(f"No queries found in {file_path}")
            return 1
            
        print(f"Processing {len(queries)} queries from {file_path}...")
        
        # Results container
        results = []
        
        # Process each query
        for i, query in enumerate(queries):
            print(f"\nQuery {i+1}/{len(queries)}: {query}")
            
            # Process the query
            try:
                response = service.answer_question(
                    query=query,
                    method=method,
                    top_k=top_k,
                )
                
                # Display the response
                print(format_response(response, show_context=show_context))
                
                # Add to results
                results.append({
                    "query": query,
                    "answer": response.answer,
                    "method": response.retrieval_method,
                    "time": response.query_time,
                })
                
            except Exception as e:
                print(f"Error processing query: {str(e)}")
                if verbose:
                    import traceback
                    print(traceback.format_exc())
                
                # Add error to results
                results.append({
                    "query": query,
                    "error": str(e),
                })
        
        # Write results to file if requested
        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults written to {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"Error in file mode: {str(e)}")
        if verbose:
            import traceback
            print(traceback.format_exc())
        return 1


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


def write_to_file(response: QueryResponse, file_path: str) -> None:
    """
    Write a query response to a file.
    
    Args:
        response: The query response to write
        file_path: Path to the file to write to
    """
    # Convert response to JSON-serializable dict
    response_dict = {
        "query": response.query,
        "answer": response.answer,
        "method": response.retrieval_method,
        "time": response.query_time,
    }
    
    # Add context if available
    if response.context:
        if isinstance(response.context, list):
            # Vector or Graph results
            context_list = []
            for ctx in response.context:
                context_item = {}
                
                # Extract text
                if hasattr(ctx, "text"):
                    context_item["text"] = ctx.text
                elif hasattr(ctx, "chunk_text"):
                    context_item["text"] = ctx.chunk_text
                    
                # Add score
                if hasattr(ctx, "score"):
                    context_item["score"] = ctx.score
                    
                # Add to list
                context_list.append(context_item)
                
            response_dict["context"] = context_list
        else:
            # Knowledge Graph results
            kg_result = response.context
            response_dict["context"] = {
                "query": kg_result.query,
                "result_count": len(kg_result.raw_results) if kg_result.raw_results else 0,
            }
    
    # Write to file
    with open(file_path, "w") as f:
        json.dump(response_dict, f, indent=2)