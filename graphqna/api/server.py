"""FastAPI server for GraphQnA API."""

import logging
import time
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from graphqna.api.models import (
    QueryRequest, 
    HealthResponse, 
    InfoResponse, 
    ErrorResponse,
    IngestRequest,
    IngestResponse
)
from graphqna.config import get_settings, Settings
from graphqna.db import Neo4jDatabase
from graphqna.retrieval import RetrievalService, RetrievalMethod

# Set up logging
logger = logging.getLogger(__name__)

# Create application
app = FastAPI(
    title="GraphQnA API",
    description="API for Graph-Enhanced Question Answering powered by Neo4j",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for settings
def get_api_settings():
    """Get application settings."""
    return get_settings()


# Dependency for database connection
def get_db(settings: Settings = Depends(get_api_settings)):
    """Get database connection."""
    db = Neo4jDatabase(settings=settings)
    try:
        yield db
    finally:
        db.close()


# Dependency for retrieval service
def get_retrieval_service(
    db: Neo4jDatabase = Depends(get_db),
    settings: Settings = Depends(get_api_settings)
):
    """Get retrieval service."""
    service = RetrievalService(db=db, settings=settings)
    try:
        yield service
    finally:
        service.close()


@app.get("/api/health", response_model=HealthResponse)
async def health_check(
    db: Neo4jDatabase = Depends(get_db),
    settings: Settings = Depends(get_api_settings)
):
    """
    Check the health of the service.
    
    Returns:
        Service health status
    """
    # Check database connection
    db_connected = False
    try:
        db_connected = db.is_connected()
    except Exception as e:
        logger.error(f"Error checking database connection: {str(e)}")
    
    return HealthResponse(
        status="ok",
        version=getattr(settings, "version", "0.1.0"),
        database_connected=db_connected
    )


@app.get("/api/info", response_model=InfoResponse)
async def get_info(
    db: Neo4jDatabase = Depends(get_db),
    settings: Settings = Depends(get_api_settings)
):
    """
    Get information about the service.
    
    Returns:
        Service information, including configuration and stats
    """
    # Get database statistics
    db_stats = {"nodes": 0, "relationships": 0, "labels": []}
    try:
        result = db.query(
            """
            MATCH (n) 
            RETURN 
                count(n) as nodes, 
                size([()-[r]->() | r]) as relationships,
                collect(distinct labels(n)[0]) as labels
            """
        )
        if result and len(result) > 0:
            db_stats = result[0]
    except Exception as e:
        logger.error(f"Error getting database statistics: {str(e)}")
    
    # Get domain configuration (without sensitive info)
    domain_config = {
        "name": settings.domain_name,
        "entity_types": getattr(settings, "domain_entity_types", []),
        "relationship_types": getattr(settings, "domain_relationship_types", []),
    }
    
    # Get available retrieval methods
    retrieval_methods = [method.value for method in RetrievalMethod]
    
    return InfoResponse(
        name="GraphQnA",
        version=getattr(settings, "version", "0.1.0"),
        description="Graph-Enhanced Question Answering powered by Neo4j",
        database_stats=db_stats,
        domain_config=domain_config,
        retrieval_methods=retrieval_methods
    )


@app.post("/api/query", response_model=Dict[str, Any])
async def query(
    request: QueryRequest,
    service: RetrievalService = Depends(get_retrieval_service),
    settings: Settings = Depends(get_api_settings)
):
    """
    Answer a question using the specified retrieval method.
    
    Args:
        request: Query request with question and parameters
        
    Returns:
        Answer to the question with context
    """
    # Validate retrieval method
    try:
        method = RetrievalMethod(request.retrieval_method.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid retrieval method: {request.retrieval_method}. "
                   f"Must be one of {[m.value for m in RetrievalMethod]}"
        )
    
    try:
        # Process the query
        start_time = time.time()
        
        response = service.answer_question(
            query=request.query,
            method=method,
            top_k=request.top_k,
        )
        
        # Calculate response time if not set
        if response.query_time == 0:
            response.query_time = time.time() - start_time
        
        # Convert to dict for JSON response
        # This includes extra processing to handle the more complex nested objects
        response_dict = response.model_dump()
        
        return response_dict
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_api_settings),
    db: Neo4jDatabase = Depends(get_db)
):
    """
    Ingest a document into the knowledge base.
    
    Args:
        request: Ingest request with document source and parameters
        
    Returns:
        Status of the ingestion process
    """
    try:
        # This would be implemented in an actual ingestion module
        # For now, return a placeholder
        return IngestResponse(
            success=True,
            document_id="doc-123",
            chunks=50,
            entities=25,
            relationships=30,
            message="Document successfully processed"
        )
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting document: {str(e)}"
        )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )


def start():
    """Start the API server using uvicorn."""
    import uvicorn
    uvicorn.run("graphqna.api.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()