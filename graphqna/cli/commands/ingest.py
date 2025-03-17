"""Ingest command for the CLI."""

import argparse
import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from graphqna.config import get_settings
from graphqna.ingest import IngestionPipeline

logger = logging.getLogger(__name__)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """
    Configure the argument parser for the ingest command.
    
    Args:
        parser: The parser to configure
    """
    parser.add_argument(
        "--file", "-f", 
        help="Path to a document file to ingest"
    )
    parser.add_argument(
        "--directory", "-d", 
        help="Path to a directory containing documents to ingest"
    )
    parser.add_argument(
        "--pattern", "-p", default="*.md",
        help="File pattern to use when ingesting a directory (default: *.md)"
    )
    parser.add_argument(
        "--clear", "-c", action="store_true", 
        help="Clear the database before ingestion"
    )
    parser.add_argument(
        "--append", "-a", action="store_true",
        help="Append to existing knowledge base (default if --clear not specified)"
    )
    parser.add_argument(
        "--simple", "-s", action="store_true",
        help="Use simple mode without schema enforcement"
    )
    parser.add_argument(
        "--move-processed", "-m", action="store_true",
        help="Move successfully processed files to the processed directory"
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip files that have already been processed"
    )
    parser.add_argument(
        "--batch-size", type=int, default=5,
        help="Maximum number of files to process in a batch (default: 5)"
    )


def execute(args: argparse.Namespace) -> int:
    """
    Execute the ingest command.
    
    Args:
        args: The parsed arguments
        
    Returns:
        Exit code
    """
    if not args.file and not args.directory:
        print("Error: Either --file or --directory must be specified")
        return 1
        
    # Get list of files to process
    files_to_process = []
    settings = get_settings()
    
    if args.file:
        # Single file mode
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return 1
        files_to_process.append(file_path)
    
    if args.directory:
        # Directory mode
        dir_path = Path(args.directory)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"Error: Directory not found: {dir_path}")
            return 1
            
        pattern = args.pattern
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                files_to_process.append(file_path)
                
        if not files_to_process:
            print(f"No files matching pattern '{pattern}' found in {dir_path}")
            return 1
    
    # Skip files that have been processed if requested
    if args.skip_existing:
        processed_dir = settings.data_dir / "processed"
        processed_files = set()
        if processed_dir.exists():
            processed_files = {f.stem for f in processed_dir.glob("*") if f.is_file()}
            
        files_to_process = [
            f for f in files_to_process 
            if f.stem not in processed_files
        ]
        
        if not files_to_process:
            print("All files have already been processed")
            return 0
    
    # Sort files by modification time (newest first)
    files_to_process.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Create ingestion pipeline
    pipeline = IngestionPipeline()
    
    # Process files
    success_count = 0
    error_count = 0
    total_files = len(files_to_process)
    
    print(f"Processing {total_files} files...")
    
    # Clear database if requested (only once)
    if args.clear and files_to_process:
        try:
            print("Clearing database...")
            pipeline.db.clear_database()
            print("Database cleared successfully")
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            return 1
    
    # Process files in batches
    batch_size = args.batch_size
    for i in range(0, len(files_to_process), batch_size):
        batch = files_to_process[i:i+batch_size]
        
        print(f"\nProcessing batch {i//batch_size + 1}/{(len(files_to_process)+batch_size-1)//batch_size}...")
        
        # Process batch
        batch_results = asyncio.run(process_batch(pipeline, batch, args))
        
        # Count results
        for result in batch_results:
            if result["status"] == "success":
                success_count += 1
                
                # Move to processed directory if requested
                if args.move_processed:
                    try:
                        source_path = result["file_path"]
                        processed_dir = settings.data_dir / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        
                        # Create target path
                        target_path = processed_dir / source_path.name
                        
                        # Copy file to processed directory
                        import shutil
                        shutil.copy2(source_path, target_path)
                        print(f"Copied {source_path.name} to processed directory")
                    except Exception as e:
                        print(f"Error moving file to processed directory: {str(e)}")
            else:
                error_count += 1
    
    # Print summary
    print("\n===== Ingestion Summary =====")
    print(f"Total files: {total_files}")
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    
    # Show database statistics
    try:
        stats = pipeline.db.get_database_stats()
        vector_stats = pipeline.vector_index.get_index_stats()
        
        print("\n===== Database Statistics =====")
        print(f"Nodes: {stats['total_nodes']}")
        print(f"Relationships: {stats['total_relationships']}")
        
        if "node_counts_by_label" in stats:
            print("\nNode Counts by Label:")
            for label, count in stats["node_counts_by_label"].items():
                if label != "Unknown" and count > 0:
                    print(f"  {label}: {count}")
                    
        print("\nVector Index:")
        print(f"  Name: {vector_stats['index_name']}")
        print(f"  Embeddings: {vector_stats.get('embedding_count', 0)}")
        print(f"  Dimensions: {vector_stats.get('embedding_dimensions', 0)}")
    except Exception as e:
        print(f"Error getting database statistics: {str(e)}")
    
    return 0 if error_count == 0 else 1


async def process_batch(
    pipeline: IngestionPipeline,
    files: List[Path],
    args: argparse.Namespace
) -> List[Dict[str, Any]]:
    """
    Process a batch of files concurrently.
    
    Args:
        pipeline: The ingestion pipeline
        files: List of files to process
        args: The parsed arguments
        
    Returns:
        List of results
    """
    # Create tasks
    tasks = []
    for file_path in files:
        task = asyncio.create_task(process_file(
            pipeline=pipeline,
            file_path=file_path,
            clear_database=False,  # Already cleared once if needed
            advanced_kg=not args.simple,
        ))
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    processed_results = []
    for i, (file_path, result) in enumerate(zip(files, results)):
        if isinstance(result, Exception):
            # Handle exception
            processed_results.append({
                "status": "error",
                "file_path": file_path,
                "message": f"Exception during processing: {str(result)}",
            })
        else:
            # Add file path to result
            result["file_path"] = file_path
            processed_results.append(result)
    
    return processed_results


async def process_file(
    pipeline: IngestionPipeline,
    file_path: Path,
    clear_database: bool = False,
    advanced_kg: bool = True,
) -> Dict[str, Any]:
    """
    Process a single file.
    
    Args:
        pipeline: The ingestion pipeline
        file_path: Path to the file
        clear_database: Whether to clear the database before ingestion
        advanced_kg: Whether to use advanced knowledge graph features
        
    Returns:
        Result of the ingestion
    """
    start_time = time.time()
    
    print(f"Processing {file_path.name}...")
    
    try:
        # Ingest document
        result = await pipeline.ingest_document(
            file_path=file_path,
            clear_database=clear_database,
            advanced_kg=advanced_kg,
        )
        
        # Add timing information
        if "time_taken" not in result:
            result["time_taken"] = time.time() - start_time
        
        # Print result
        if result["status"] == "success":
            print(f"✅ {file_path.name} successfully processed in {result['time_taken']:.2f} seconds")
        else:
            print(f"❌ {file_path.name} failed: {result.get('message', 'Unknown error')}")
            if "detail" in result:
                print(f"  Detail: {result['detail']}")
        
        return result
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error during processing: {str(e)}",
            "time_taken": time.time() - start_time,
        }