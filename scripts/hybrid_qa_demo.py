#!/usr/bin/env python3
"""
Demo script for the Hybrid Knowledge Graph QA System.

This script demonstrates the new hybrid retriever that automatically selects
the optimal retrieval method based on the query type.
"""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphqna.retrieval import RetrievalService, RetrievalMethod
from graphqna.retrieval.hybrid_retriever import HybridRetriever, QueryClassifier, QueryType
from graphqna.models.response import QueryResponse

def print_separator(message=None):
    """Print a separator line with an optional message."""
    print("\n" + "=" * 80)
    if message:
        print(f"  {message}")
        print("=" * 80)
    print()

def format_response(method, response, display_context=True):
    """Format a query response for display."""
    output = f"📝 Answer ({method}):\n{response.answer}\n\n"
    output += f"⏱️  Response time: {response.query_time:.2f}s\n"
    
    if display_context and response.context:
        output += "\n--- Context Information ---\n"
        
        # Knowledge Graph results
        if hasattr(response.context, 'query') and response.context.query:
            output += f"Generated Cypher query:\n{response.context.query}\n\n"
        
        # Handle entities
        if hasattr(response.context, 'entities') and response.context.entities:
            output += f"Entities found: {len(response.context.entities)}\n"
            for i, entity in enumerate(response.context.entities[:3]):  # Show first 3
                if hasattr(entity, 'primary_label'):
                    label = entity.primary_label
                elif hasattr(entity, 'labels') and entity.labels:
                    label = entity.labels[0]
                else:
                    label = "Unknown"
                    
                name = entity.name if hasattr(entity, 'name') else "Unnamed"
                output += f"  {i+1}. {label}: {name}\n"
    
    return output

def compare_methods(query):
    """Compare different retrieval methods on the same query."""
    # Create service and hybrid retriever
    service = RetrievalService()
    hybrid_retriever = HybridRetriever()
    classifier = QueryClassifier()
    
    print_separator(f"Query: {query}")
    
    # Classify the query first
    query_type = classifier.classify(query)
    print(f"Query classified as: {query_type}")
    
    try:
        # First run with the hybrid retriever
        print("Running with smart hybrid retriever...")
        start_time = time.time()
        hybrid_response = hybrid_retriever.answer_question(query=query, top_k=5)
        hybrid_time = time.time() - start_time
        print(f"✓ Hybrid retrieval completed in {hybrid_time:.2f}s")
        
        # Compare with individual methods
        methods = {
            "Vector Similarity": RetrievalMethod.VECTOR,
            "GraphRAG Retrieval": RetrievalMethod.GRAPHRAG,
            "Knowledge Graph": RetrievalMethod.KG,
            "Enhanced KG": RetrievalMethod.ENHANCED_KG
        }
        
        results = {}
        
        # Run the query with each method
        for name, method in methods.items():
            print(f"Trying {name} method...")
            start_time = time.time()
            
            try:
                response = service.answer_question(
                    query=query,
                    method=method,
                    top_k=5
                )
                
                results[name] = response
                print(f"✓ {name} query completed in {time.time() - start_time:.2f}s")
            except Exception as e:
                print(f"✗ {name} query failed: {str(e)}")
        
        # Display hybrid result first
        print_separator("Hybrid Retriever (Smart Selection)")
        print(format_response("Hybrid", hybrid_response))
        
        # Display individual results
        for name, response in results.items():
            print_separator(name)
            print(format_response(name, response))
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up resources
        service.close()
        hybrid_retriever.db.close()

def run_demo_questions():
    """Run the demo with predefined questions from domain configuration."""
    from graphqna.config import get_settings
    # Create hybrid retriever
    hybrid_retriever = HybridRetriever()
    classifier = QueryClassifier()
    
    # Get settings and domain name
    settings = get_settings()
    domain_name = settings.domain_name
    example_queries = settings.example_queries
    
    # Demo questions for each query type, using domain config examples if available
    questions = {
        "factual": example_queries.get("factual", ["What is used for?"])[0].format(domain_name=domain_name),
        "procedural": example_queries.get("procedural", ["How do I create a report?"])[0].format(domain_name=domain_name),
        "entity": example_queries.get("entity", ["What types are available?"])[0].format(domain_name=domain_name),
        "relationship": example_queries.get("relationship", ["Which roles can perform customer enablement?"])[0],
    }
    
    print_separator("Running Example Questions for Each Query Type")
    
    # Run each question
    for query_type, question in questions.items():
        print_separator(f"Query Type: {query_type}")
        print(f"Question: {question}")
        
        # Classify to verify
        actual_type = classifier.classify(question)
        print(f"Classified as: {actual_type}")
        
        # Answer the question
        start_time = time.time()
        response = hybrid_retriever.answer_question(query=question, top_k=5)
        print(f"✓ Query completed in {time.time() - start_time:.2f}s")
        
        # Display the result
        print(format_response("Hybrid", response))
    
    # Clean up
    hybrid_retriever.db.close()

def main():
    """Main entry point for the demo."""
    print("\n=== GraphQnA - Hybrid Knowledge Graph QA System Demo ===\n")
    print("This demo shows how the hybrid retriever automatically selects")
    print("the best retrieval method based on query classification.\n")
    
    print("Choose a demo mode:")
    print("1. Compare all retrieval methods on a single query")
    print("2. Run example questions for each query type")
    print("3. Try your own question with the hybrid retriever")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Option 1: Compare methods
        # Use example queries from domain config if available
        settings = get_settings()
        domain_name = settings.domain_name
        example_queries = settings.example_queries
        
        all_examples = []
        for category, examples in example_queries.items():
            if examples and isinstance(examples, list):
                all_examples.extend([q.format(domain_name=domain_name) if "{domain_name}" in q else q for q in examples[:2]])
        
        # Fallback to defaults if no examples in config
        if not all_examples:
            all_examples = [
                f"What are the key features of {domain_name}?",
                f"How can I track interactions in {domain_name}?",
                "What's the difference between an activity and a task?",
                f"How do I create a custom report in {domain_name}?",
                "What roles can perform customer tasks?"
            ]
            
        # Take the first 5 examples or all if fewer
        demos = all_examples[:5]
        
        print("\nDemo queries:")
        for i, query in enumerate(demos):
            print(f"{i+1}. {query}")
        
        print("\nEnter a number to use a demo query, or type your own question:")
        user_input = input("> ").strip()
        
        # Process input
        if user_input.isdigit() and 1 <= int(user_input) <= len(demos):
            query = demos[int(user_input) - 1]
        else:
            query = user_input
        
        compare_methods(query)
        
    elif choice == "2":
        # Option 2: Run example questions
        run_demo_questions()
        
    elif choice == "3":
        # Option 3: Try your own question
        hybrid_retriever = HybridRetriever()
        classifier = QueryClassifier()
        
        print("\nEnter your question:")
        query = input("> ").strip()
        
        # Classify the query
        query_type = classifier.classify(query)
        print(f"Query classified as: {query_type}")
        
        # Answer the question
        start_time = time.time()
        response = hybrid_retriever.answer_question(query=query, top_k=5)
        print(f"✓ Query completed in {time.time() - start_time:.2f}s")
        
        # Display the result
        print(format_response("Hybrid", response, display_context=True))
        
        # Clean up
        hybrid_retriever.db.close()
        
    else:
        print("Invalid choice. Please run the demo again and select 1, 2, or 3.")
    
    print("\nDemo completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())