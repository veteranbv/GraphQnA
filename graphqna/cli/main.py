"""Main entry point for the GraphQnA CLI."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from graphqna.cli.commands import db, ingest, query, test
from graphqna.config import get_settings

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


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (uses sys.argv if None)
        
    Returns:
        Exit code
    """
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="GraphQnA - Knowledge Graph Question Answering System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create parser for the "ingest" command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest documents into the knowledge graph"
    )
    ingest.configure_parser(ingest_parser)
    
    # Create parser for the "query" command
    query_parser = subparsers.add_parser(
        "query", help="Query the knowledge graph for answers"
    )
    query.configure_parser(query_parser)
    
    # Create parser for the "db" command
    db_parser = subparsers.add_parser(
        "db", help="Database management commands"
    )
    db.configure_parser(db_parser)
    
    # Create parser for the "test" command
    test_parser = subparsers.add_parser(
        "test", help="Run tests on the knowledge base"
    )
    test.configure_parser(test_parser)
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Execute the appropriate command
    if parsed_args.command == "ingest":
        return ingest.execute(parsed_args)
    elif parsed_args.command == "query":
        return query.execute(parsed_args)
    elif parsed_args.command == "db":
        return db.execute(parsed_args)
    elif parsed_args.command == "test":
        return test.execute(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())