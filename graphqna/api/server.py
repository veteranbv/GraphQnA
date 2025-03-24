"""FastAPI server for GraphQnA API."""

import logging
import os
import time
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Dict

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import ValidationError

from graphqna.api.models import (
    HealthResponse,
    InfoResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
)
from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.retrieval import RetrievalMethod, RetrievalService

# Set up logging with rotation
logger = logging.getLogger(__name__)


# Configure log rotation if log directory is set
def setup_log_rotation():
    settings = get_settings()
    log_dir = getattr(settings, "logs_dir", None)

    if log_dir:
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Security log
        security_log_path = os.path.join(log_dir, "security.log")
        security_handler = TimedRotatingFileHandler(
            filename=security_log_path,
            when="midnight",
            backupCount=30,  # Keep 30 days of logs
        )
        security_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        security_handler.setLevel(logging.INFO)

        # Get security logger
        security_logger = logging.getLogger("graphqna.security")
        security_logger.setLevel(logging.INFO)
        security_logger.addHandler(security_handler)
        security_logger.propagate = False  # Don't send to root logger

        # API log
        api_log_path = os.path.join(log_dir, "api.log")
        api_handler = TimedRotatingFileHandler(
            filename=api_log_path,
            when="midnight",
            backupCount=14,  # Keep 14 days of logs
        )
        api_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        # Add to main logger
        logger.addHandler(api_handler)
        logger.setLevel(logging.INFO)

        return security_logger

    return logging.getLogger("graphqna.security")


# Initialize security logger
security_logger = setup_log_rotation()

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


# Simple rate limiting implementation
class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # IP -> list of timestamps

    def is_rate_limited(self, ip: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Clean up old entries
        if ip in self.requests:
            self.requests[ip] = [ts for ts in self.requests[ip] if ts > minute_ago]

        # Check if rate limit is exceeded
        if ip in self.requests and len(self.requests[ip]) >= self.requests_per_minute:
            return True

        # Add this request
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip].append(now)

        return False


# Initialize rate limiter
rate_limiter = RateLimiter(requests_per_minute=60)  # Adjust as needed


# Dependency for settings
def get_api_settings():
    """Get application settings."""
    return get_settings()


# API Key security - using a single header name with case-insensitive comparison
api_key_header = APIKeyHeader(name="x-api-key")  # Standard lowercase header


async def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get the first IP in X-Forwarded-For as it's likely the client
        return forwarded.split(",")[0].strip()

    # If no forwarding headers, use the direct client address
    client_host = request.client.host if request.client else "unknown"
    return client_host


def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    settings: Settings = Depends(get_api_settings),
):
    """Verify API key with case-insensitive comparison."""
    # Apply rate limiting first
    client_ip = "unknown"
    try:
        client_ip = request.client.host if request.client else "unknown"
    except:
        pass

    if rate_limiter.is_rate_limited(client_ip):
        security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429, detail="Too many requests. Please try again later."
        )

    # Check for API key configuration
    if not settings.api_key:
        # If no API key is configured, allow access but warn (development mode)
        security_logger.warning(
            "Security alert: No API key configured. Running in insecure mode."
        )
        return api_key

    # Check if API key was provided
    if not api_key:
        security_logger.warning(
            f"Security alert: Missing API key in request from {client_ip}"
        )
        raise HTTPException(status_code=403, detail="API key is required")

    # Case-insensitive comparison
    if api_key.lower() != settings.api_key.lower():
        # Sanitize key for logging (show only first few chars)
        sanitized_key = api_key[:5] + "..." if api_key else "none"
        security_logger.warning(
            f"Security alert: Invalid API key ({sanitized_key}) from IP {client_ip}"
        )
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key


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
    db: Neo4jDatabase = Depends(get_db), settings: Settings = Depends(get_api_settings)
):
    """Get retrieval service."""
    service = RetrievalService(db=db, settings=settings)
    try:
        yield service
    finally:
        service.close()


@app.get("/api/health", response_model=HealthResponse)
async def health_check(
    db: Neo4jDatabase = Depends(get_db), settings: Settings = Depends(get_api_settings)
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
        database_connected=db_connected,
    )


@app.get(
    "/api/info", response_model=InfoResponse, dependencies=[Depends(verify_api_key)]
)
async def get_info(
    db: Neo4jDatabase = Depends(get_db), settings: Settings = Depends(get_api_settings)
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
        retrieval_methods=retrieval_methods,
    )


@app.post(
    "/api/query", response_model=Dict[str, Any], dependencies=[Depends(verify_api_key)]
)
async def query(
    request: QueryRequest,
    service: RetrievalService = Depends(get_retrieval_service),
    settings: Settings = Depends(get_api_settings),
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
            f"Must be one of {[m.value for m in RetrievalMethod]}",
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
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post(
    "/api/ingest", response_model=IngestResponse, dependencies=[Depends(verify_api_key)]
)
async def ingest_document(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_api_settings),
    db: Neo4jDatabase = Depends(get_db),
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
            message="Document successfully processed",
        )
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error ingesting document: {str(e)}"
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
