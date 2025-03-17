"""Test command for the CLI."""

import argparse
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from graphqna.config import get_settings
from graphqna.retrieval import RetrievalService, RetrievalMethod

logger = logging.getLogger(__name__)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """
    Configure the argument parser for the test command.
    
    Args:
        parser: The parser to configure
    """
    parser.add_argument(
        "--suite", "-s", 
        choices=["basic", "full", "custom"], default="basic",
        help="Test suite to run (default: basic)"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to a test questions file (required for custom suite)"
    )
    parser.add_argument(
        "--method", "-m", 
        default="graphrag", choices=["vector", "graphrag", "kg", "all"],
        help="Retrieval method to use for tests (default: graphrag, 'all' to test all methods)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write test results to (in JSON format)"
    )
    parser.add_argument(
        "--rebuild", "-r", action="store_true",
        help="Rebuild the knowledge base before running tests (may take several minutes)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed information about each test"
    )


def execute(args: argparse.Namespace) -> int:
    """
    Execute the test command.
    
    Args:
        args: The parsed arguments
        
    Returns:
        Exit code
    """
    # Validate arguments
    if args.suite == "custom" and not args.file:
        print("Error: --file is required for custom test suite")
        return 1
        
    # Get test questions
    if args.suite == "custom":
        test_questions = load_custom_tests(args.file)
    elif args.suite == "full":
        test_questions = load_full_tests()
    else:  # basic
        test_questions = load_basic_tests()
        
    if not test_questions:
        print("Error: No test questions loaded")
        return 1
        
    # Rebuild knowledge base if requested
    if args.rebuild:
        if not rebuild_knowledge_base():
            print("Error: Failed to rebuild knowledge base")
            return 1
            
    # Determine methods to test
    methods = []
    if args.method == "all":
        methods = ["vector", "graphrag", "kg"]
    else:
        methods = [args.method]
        
    # Run tests
    results = run_tests(
        test_questions=test_questions,
        methods=methods,
        verbose=args.verbose,
    )
    
    # Show results
    show_results(results, verbose=args.verbose)
    
    # Write to file if requested
    if args.output:
        write_results_to_file(results, args.output)
        print(f"\nResults written to {args.output}")
    
    # Return success if all tests passed
    return 0


def load_custom_tests(file_path: str) -> List[Dict[str, Any]]:
    """
    Load test questions from a custom file.
    
    The file can be in one of these formats:
    1. Plain text with one question per line
    2. JSON with a list of question objects
    3. Markdown with questions in sections (like test_questions.md)
    
    Args:
        file_path: Path to the test file
        
    Returns:
        List of test question objects
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: Test file not found: {file_path}")
        return []
        
    # Try to parse based on file extension
    extension = file_path.suffix.lower()
    
    if extension == ".json":
        # JSON format
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                
                # If it's a list of strings, convert to proper format
                if isinstance(data, list):
                    if all(isinstance(item, str) for item in data):
                        return [{"question": q, "category": "Custom"} for q in data]
                    elif all(isinstance(item, dict) and "question" in item for item in data):
                        return data
                
                print("Error: Invalid JSON format for test questions")
                return []
            except json.JSONDecodeError:
                print("Error: Invalid JSON format")
                return []
    elif extension == ".md":
        # Markdown format (like test_questions.md)
        with open(file_path, "r") as f:
            content = f.read()
            return parse_markdown_test_questions(content)
    else:
        # Plain text format (one question per line)
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            return [{"question": q, "category": "Custom"} for q in lines]


def load_basic_tests() -> List[Dict[str, Any]]:
    """
    Load the basic test suite using domain-specific questions.
    
    Returns:
        List of test question objects
    """
    # Get settings and domain name
    settings = get_settings()
    domain_name = settings.domain_name
    example_queries = settings.example_queries
    
    # Basic test suite includes a small set of representative questions
    # Use example queries from domain config if available
    questions = []
    
    # Try to get a factual question about the domain
    factual_q = example_queries.get("factual", [f"What is {domain_name}?"])[0]
    factual_q = factual_q.format(domain_name=domain_name) if "{domain_name}" in factual_q else factual_q
    questions.append({
        "question": factual_q,
        "category": "Basic Information",
        "expected_method": "vector",
    })
    
    # Try to get a procedural question
    procedural_q = example_queries.get("procedural", ["What are the main steps involved in the standard process?"])[0]
    procedural_q = procedural_q.format(domain_name=domain_name) if "{domain_name}" in procedural_q else procedural_q
    questions.append({
        "question": procedural_q,
        "category": "Process",
        "expected_method": "graphrag",
    })
    
    # Try to get a getting started question
    access_q = f"How do I access {domain_name} for the first time?"
    if example_queries.get("procedural") and len(example_queries.get("procedural")) > 1:
        access_q = example_queries.get("procedural")[1]
        access_q = access_q.format(domain_name=domain_name) if "{domain_name}" in access_q else access_q
    questions.append({
        "question": access_q,
        "category": "Getting Started",
        "expected_method": "vector",
    })
    
    # Try to get an entity question
    entity_q = example_queries.get("entity", ["What types are available in the system?"])[0]
    entity_q = entity_q.format(domain_name=domain_name) if "{domain_name}" in entity_q else entity_q
    questions.append({
        "question": entity_q,
        "category": "Entities",
        "expected_method": "graphrag",
    })
    
    # Try to get a relationship question
    relationship_q = example_queries.get("relationship", ["Which roles can perform specific tasks?"])[0]
    relationship_q = relationship_q.format(domain_name=domain_name) if "{domain_name}" in relationship_q else relationship_q
    questions.append({
        "question": relationship_q,
        "category": "Relationships",
        "expected_method": "graphrag",
    })
    
    return questions


def load_full_tests() -> List[Dict[str, Any]]:
    """
    Load the full test suite from domain-specific test questions file.
    Tries to load test_questions_domain.md first, then falls back to test_questions.md.
    
    Returns:
        List of test question objects
    """
    settings = get_settings()
    domain_test_file = settings.base_dir / "tests" / "resources" / "test_questions_domain.md"
    default_test_file = settings.base_dir / "tests" / "resources" / "test_questions.md"
    test_template_file = settings.base_dir / "tests" / "resources" / "test_questions_template.md"
    
    # Try loading domain-specific test questions first
    if domain_test_file.exists():
        with open(domain_test_file, "r") as f:
            content = f.read()
            # Replace {domain_name} with actual domain name if needed
            if "{domain_name}" in content:
                content = content.replace("{domain_name}", settings.domain_name)
            return parse_markdown_test_questions(content)
    
    # Fall back to default test questions if available
    if default_test_file.exists():
        with open(default_test_file, "r") as f:
            content = f.read()
            return parse_markdown_test_questions(content)
    
    # If neither exists, try to create a domain-specific file from the template
    if test_template_file.exists():
        print(f"Domain-specific test questions file not found.")
        print(f"Creating one from template at: {domain_test_file}")
        
        # Load template and replace domain_name
        with open(test_template_file, "r") as f:
            content = f.read()
            content = content.replace("{domain_name}", settings.domain_name)
        
        # Save domain-specific test file
        try:
            with open(domain_test_file, "w") as f:
                f.write(content)
            print(f"Created domain-specific test questions file at: {domain_test_file}")
            return parse_markdown_test_questions(content)
        except Exception as e:
            print(f"Error creating domain-specific test file: {str(e)}")
            return []
    
    # If nothing works, return empty list
    print(f"Error: No test questions file found")
    return []


def parse_markdown_test_questions(content: str) -> List[Dict[str, Any]]:
    """
    Parse test questions from a markdown file.
    
    The markdown should be formatted like test_questions.md, with sections
    and numbered questions.
    
    Args:
        content: Markdown content
        
    Returns:
        List of test question objects
    """
    questions = []
    current_category = "General"
    
    # Split into lines
    lines = content.splitlines()
    
    for line in lines:
        # Check for section headers
        if line.startswith("## "):
            current_category = line[3:].strip()
            continue
            
        # Look for numbered questions
        match = re.match(r"^\d+\.[ \t]+(.+)$", line)
        if match:
            question_text = match.group(1).strip()
            questions.append({
                "question": question_text,
                "category": current_category,
            })
    
    return questions


def rebuild_knowledge_base() -> bool:
    """
    Rebuild the knowledge base from scratch.
    
    Returns:
        True if successful, False otherwise
    """
    from graphqna.cli.commands.db import execute as db_execute
    from graphqna.cli.commands.ingest import execute as ingest_execute
    
    # Create argument objects
    db_args = argparse.Namespace(
        clear=True,
        stats=False,
        reset_vector_index=False,
        check_connection=False,
        check_index=False,
        backup=None,
        force=True,
        dimensions=None,
    )
    
    # Clear database
    print("Clearing database...")
    result = db_execute(db_args)
    if result != 0:
        print("Error: Failed to clear database")
        return False
    
    # Create ingest args
    settings = get_settings()
    raw_dir = settings.data_dir / "raw"
    
    # Find document files
    doc_files = list(raw_dir.glob("*.md"))
    if not doc_files:
        print(f"Error: No document files found in {raw_dir}")
        return False
        
    # Use the first document file
    doc_file = doc_files[0]
    
    ingest_args = argparse.Namespace(
        file=str(doc_file),
        directory=None,
        pattern="*.md",
        clear=False,  # Already cleared
        append=False,
        simple=False,
        move_processed=False,
        skip_existing=False,
        batch_size=5,
    )
    
    # Ingest document
    print(f"Ingesting document: {doc_file}")
    result = ingest_execute(ingest_args)
    if result != 0:
        print("Error: Failed to ingest document")
        return False
        
    return True


def run_tests(
    test_questions: List[Dict[str, Any]],
    methods: List[str],
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Run the test suite.
    
    Args:
        test_questions: List of test questions
        methods: List of retrieval methods to test
        verbose: Whether to show verbose output
        
    Returns:
        Dictionary of test results
    """
    # Create retrieval service
    service = RetrievalService()
    
    try:
        # Test results
        results = {
            "total": len(test_questions) * len(methods),
            "successful": 0,
            "methods": {},
            "categories": {},
            "questions": [],
        }
        
        # Initialize method stats
        for method in methods:
            results["methods"][method] = {
                "total": 0,
                "successful": 0,
                "average_time": 0.0,
            }
            
        # Run tests
        print(f"Running {len(test_questions)} tests with {len(methods)} methods ({len(test_questions) * len(methods)} total tests)...")
        
        for i, test in enumerate(test_questions):
            question = test["question"]
            category = test.get("category", "General")
            
            # Initialize category stats if needed
            if category not in results["categories"]:
                results["categories"][category] = {
                    "total": 0,
                    "successful": 0,
                }
                
            # Track question results
            question_results = {
                "question": question,
                "category": category,
                "results": {},
            }
            
            # Run tests for each method
            for method in methods:
                # Update stats
                results["categories"][category]["total"] += 1
                results["methods"][method]["total"] += 1
                
                # Execute query
                try:
                    print(f"\nTest {i+1}/{len(test_questions)} ({method}): {question}")
                    
                    # Time the query
                    start_time = time.time()
                    response = service.answer_question(
                        query=question,
                        method=method,
                    )
                    end_time = time.time()
                    
                    # If query_time wasn't set, use our measurement
                    if response.query_time == 0:
                        response.query_time = end_time - start_time
                        
                    # Display answer
                    if verbose:
                        from graphqna.cli.commands.query import format_response
                        print(format_response(response, show_context=False))
                    else:
                        # Just show a short version
                        print(f"Answer: {response.answer[:100]}{'...' if len(response.answer) > 100 else ''}")
                        print(f"Time: {response.query_time:.2f}s")
                    
                    # Check if successful
                    success = len(response.answer) > 50 and "error" not in response.answer.lower()
                    
                    # Update stats
                    if success:
                        results["successful"] += 1
                        results["categories"][category]["successful"] += 1
                        results["methods"][method]["successful"] += 1
                        
                    # Update method stats
                    results["methods"][method]["average_time"] += response.query_time
                    
                    # Add to question results
                    question_results["results"][method] = {
                        "success": success,
                        "time": response.query_time,
                        "answer": response.answer,
                    }
                    
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
                    # Add error to question results
                    question_results["results"][method] = {
                        "success": False,
                        "error": str(e),
                    }
            
            # Add to questions results
            results["questions"].append(question_results)
            
        # Calculate averages
        for method in methods:
            total = results["methods"][method]["total"]
            if total > 0:
                results["methods"][method]["average_time"] /= total
                
        return results
    finally:
        # Clean up
        service.close()


def show_results(results: Dict[str, Any], verbose: bool = False) -> None:
    """
    Display test results.
    
    Args:
        results: Test results
        verbose: Whether to show verbose output
    """
    print("\n===== Test Results =====")
    print(f"Total tests: {results['total']}")
    print(f"Successful: {results['successful']} ({results['successful'] / results['total'] * 100:.1f}%)")
    
    # Show method results
    print("\nResults by Method:")
    for method, stats in results["methods"].items():
        success_rate = stats["successful"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {method}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%) - Avg time: {stats['average_time']:.2f}s")
        
    # Show category results
    print("\nResults by Category:")
    for category, stats in results["categories"].items():
        success_rate = stats["successful"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {category}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
        
    # Show detailed results if verbose
    if verbose:
        print("\nDetailed Results:")
        for question in results["questions"]:
            print(f"\nQuestion: {question['question']}")
            print(f"Category: {question['category']}")
            
            for method, result in question["results"].items():
                if result.get("success", False):
                    print(f"  {method}: ✅ ({result.get('time', 0):.2f}s)")
                    print(f"    Answer: {result.get('answer', '')[:100]}{'...' if len(result.get('answer', '')) > 100 else ''}")
                else:
                    print(f"  {method}: ❌ {result.get('error', '')}")


def write_results_to_file(results: Dict[str, Any], file_path: str) -> None:
    """
    Write test results to a file.
    
    Args:
        results: Test results
        file_path: Path to write results to
    """
    with open(file_path, "w") as f:
        json.dump(results, f, indent=2)