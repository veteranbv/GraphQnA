"""Tests for model classes."""

import pytest
from datetime import datetime
from pathlib import Path

from graphqna.models.document import Document, DocumentChunk, DocumentMetadata


def test_document_chunk_creation():
    """Test creation of document chunks."""
    # Create a document chunk
    chunk = DocumentChunk(
        text="This is a test chunk",
        index=0,
        start_char=0,
        end_char=19,
    )
    
    # Verify properties
    assert chunk.text == "This is a test chunk"
    assert chunk.index == 0
    assert chunk.start_char == 0
    assert chunk.end_char == 19
    assert chunk.embedding is None


def test_document_metadata_creation():
    """Test creation of document metadata."""
    # Create document metadata
    metadata = DocumentMetadata(
        source="test.md",
        title="Test Document",
        author="Test Author",
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 2),
        keywords=["test", "document"],
        language="en",
    )
    
    # Verify properties
    assert metadata.source == "test.md"
    assert metadata.source_type == "file"
    assert metadata.title == "Test Document"
    assert metadata.author == "Test Author"
    assert metadata.created_at == datetime(2023, 1, 1)
    assert metadata.updated_at == datetime(2023, 1, 2)
    assert metadata.keywords == ["test", "document"]
    assert metadata.language == "en"
    assert metadata.custom_metadata == {}


def test_document_creation():
    """Test creation of documents."""
    # Create document metadata
    metadata = DocumentMetadata(
        source="test.md",
        title="Test Document",
    )
    
    # Create document chunks
    chunks = [
        DocumentChunk(
            text="Chunk 1",
            index=0,
            start_char=0,
            end_char=7,
        ),
        DocumentChunk(
            text="Chunk 2",
            index=1,
            start_char=8,
            end_char=15,
        ),
    ]
    
    # Create document
    document = Document(
        text="Chunk 1\nChunk 2",
        metadata=metadata,
        chunks=chunks,
    )
    
    # Verify properties
    assert document.text == "Chunk 1\nChunk 2"
    assert document.metadata.title == "Test Document"
    assert len(document.chunks) == 2
    assert document.chunks[0].text == "Chunk 1"
    assert document.chunks[1].text == "Chunk 2"


def test_document_validation():
    """Test document validation."""
    # Test empty text validation
    with pytest.raises(ValueError):
        Document(
            text="",
            metadata=DocumentMetadata(source="test.md"),
        )
        
    # Test empty source validation
    with pytest.raises(ValueError):
        DocumentMetadata(source="")