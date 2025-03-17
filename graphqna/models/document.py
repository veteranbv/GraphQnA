"""Document models for GraphQnA."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    source: str = Field(..., description="Source of the document (file path, URL, etc.)")
    source_type: str = Field("file", description="Type of source (file, URL, etc.)")
    title: Optional[str] = Field(None, description="Title of the document")
    author: Optional[str] = Field(None, description="Author of the document")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    keywords: List[str] = Field(default=[], description="Keywords for the document")
    mime_type: Optional[str] = Field(None, description="MIME type of the document")
    language: str = Field("en", description="Language of the document (ISO 639-1)")
    custom_metadata: Dict[str, Any] = Field(
        default={}, description="Custom metadata key-value pairs"
    )

    @validator("source")
    def validate_source(cls, v):
        """Validate the source field."""
        if not v:
            raise ValueError("Source cannot be empty")
        return v


class DocumentChunk(BaseModel):
    """A chunk of a document with its metadata."""

    text: str = Field(..., description="Text content of the chunk")
    index: int = Field(..., description="Index of the chunk in the document")
    start_char: int = Field(..., description="Starting character position in the original document")
    end_char: int = Field(..., description="Ending character position in the original document")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the chunk")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    id: Optional[str] = Field(None, description="Unique identifier for the chunk")

    @validator("text")
    def validate_text(cls, v):
        """Validate the text field."""
        if not v or not v.strip():
            raise ValueError("Chunk text cannot be empty")
        return v


class Document(BaseModel):
    """A document with its content and metadata."""

    text: str = Field(..., description="Full text content of the document")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    chunks: List[DocumentChunk] = Field(default=[], description="Document chunks")

    @validator("text")
    def validate_text(cls, v):
        """Validate the text field."""
        if not v or not v.strip():
            raise ValueError("Document text cannot be empty")
        return v

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Document":
        """
        Create a Document from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Document: Created document
            
        Raises:
            FileNotFoundError: If file not found
            ValueError: If file type not supported
            IOError: If file cannot be read
        """
        # Convert to Path object if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Get file metadata
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime)
        updated_at = datetime.fromtimestamp(stat.st_mtime)
        
        # Get file extension and determine type
        extension = file_path.suffix.lower()
        
        # Set mime type based on extension
        mime_type_map = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".json": "application/json",
            ".html": "text/html",
            ".htm": "text/html",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        mime_type = mime_type_map.get(extension, "application/octet-stream")
        
        # Read file content based on type
        if extension in [".txt", ".md", ".json", ".html", ".htm"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                raise IOError(f"Failed to read file: {str(e)}")
        elif extension == ".pdf":
            # For this simplified version, we'll skip PDF parsing
            # In a real implementation, use PyPDF2 or a similar library
            raise ValueError("PDF parsing not implemented in this example")
        else:
            raise ValueError(f"Unsupported file type: {extension}")
            
        # Create document metadata
        metadata = DocumentMetadata(
            source=str(file_path),
            source_type="file",
            title=file_path.stem,
            created_at=created_at,
            updated_at=updated_at,
            mime_type=mime_type,
        )
        
        # Create and return the document
        return cls(text=text, metadata=metadata)