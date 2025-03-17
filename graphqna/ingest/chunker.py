"""Document chunking utilities."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from graphqna.config import Settings, get_settings
from graphqna.models.document import Document, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Splits documents into chunks based on configurable parameters.
    
    This class handles splitting documents into semantic chunks that can be
    processed efficiently while maintaining context boundaries.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the document chunker.
        
        Args:
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()
        self.chunk_size = self.settings.chunking.chunk_size
        self.chunk_overlap = self.settings.chunking.chunk_overlap

    def chunk_document(self, document: Document) -> Document:
        """
        Split a document into chunks.
        
        Args:
            document: The document to chunk
            
        Returns:
            Document with chunks added
        """
        # Create chunks
        text = document.text
        chunks = self._create_chunks(text)
        
        # Add chunks to document
        document.chunks = chunks
        
        logger.info(f"Created {len(chunks)} chunks from document: {document.metadata.title}")
        return document

    def _create_chunks(self, text: str) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of document chunks
        """
        if not text:
            return []
            
        chunks = []
        content_length = len(text)
        
        # Determine if we should use semantic chunking based on document structure
        if _has_semantic_structure(text):
            chunk_segments = self._create_semantic_chunks(text)
        else:
            # Use simple chunking by character count
            chunk_segments = self._create_simple_chunks(text)
            
        # Convert segments to DocumentChunk objects
        for i, (chunk_text, start_char, end_char) in enumerate(chunk_segments):
            chunk = DocumentChunk(
                text=chunk_text,
                index=i,
                start_char=start_char,
                end_char=end_char,
                metadata={
                    "char_length": len(chunk_text),
                    "token_estimate": _estimate_tokens(chunk_text),
                }
            )
            chunks.append(chunk)
            
        return chunks

    def _create_semantic_chunks(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Create chunks that respect semantic boundaries like paragraphs and headings.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of tuples (chunk_text, start_char, end_char)
        """
        chunks = []
        content_length = len(text)
        
        # Split text into sections based on headings
        sections = _split_by_headings(text)
        
        current_chunk = ""
        current_start = 0
        
        for section_text, section_start, section_end in sections:
            # If adding this section would exceed chunk size, finish the current chunk
            if len(current_chunk) + len(section_text) > self.chunk_size and current_chunk:
                chunks.append((current_chunk, current_start, current_start + len(current_chunk)))
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:]
                current_start = current_start + overlap_start
                
            # Add the section to the current chunk
            current_chunk += section_text
            
            # If current chunk exceeds chunk size, split it further
            while len(current_chunk) > self.chunk_size:
                # Find a good split point - prefer end of paragraph or sentence
                split_point = _find_split_point(current_chunk, self.chunk_size)
                
                # Add the chunk
                chunks.append((current_chunk[:split_point], current_start, current_start + split_point))
                
                # Start new chunk with overlap
                overlap_start = max(0, split_point - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:]
                current_start = current_start + overlap_start
        
        # Add the final chunk if there's anything left
        if current_chunk:
            chunks.append((current_chunk, current_start, current_start + len(current_chunk)))
            
        return chunks

    def _create_simple_chunks(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Create simple overlapping chunks based on character count.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of tuples (chunk_text, start_char, end_char)
        """
        chunks = []
        content_length = len(text)
        
        # Use a simple chunking strategy - fixed size with overlap
        for i in range(0, content_length, self.chunk_size - self.chunk_overlap):
            # Determine chunk boundaries
            start = i
            end = min(i + self.chunk_size, content_length)
            
            # Extract the chunk text
            chunk_text = text[start:end]
            
            # Add the chunk
            chunks.append((chunk_text, start, end))
            
            # If we've reached the end of the text, break
            if end >= content_length:
                break
                
        return chunks


def _split_by_headings(text: str) -> List[Tuple[str, int, int]]:
    """
    Split text into sections based on Markdown headings.
    
    Args:
        text: Text to split
        
    Returns:
        List of tuples (section_text, start_char, end_char)
    """
    # Regex to match Markdown headings
    heading_pattern = r'^#{1,6}\s+.*$'
    
    # Find all heading positions
    heading_matches = []
    current_pos = 0
    
    for line in text.split('\n'):
        # If this is a heading, record its position
        if re.match(heading_pattern, line.strip()):
            heading_matches.append(current_pos)
        
        # Move to the next line
        current_pos += len(line) + 1  # +1 for the newline
    
    # If no headings were found, return the entire text as one section
    if not heading_matches:
        return [(text, 0, len(text))]
    
    # Create sections based on heading positions
    sections = []
    
    for i, start_pos in enumerate(heading_matches):
        # Determine the end position of this section
        if i < len(heading_matches) - 1:
            end_pos = heading_matches[i + 1]
        else:
            end_pos = len(text)
        
        # Extract the section text
        section_text = text[start_pos:end_pos]
        
        # Add the section
        sections.append((section_text, start_pos, end_pos))
    
    return sections


def _find_split_point(text: str, max_size: int) -> int:
    """
    Find a good split point in the text, preferring paragraph or sentence boundaries.
    
    Args:
        text: Text to split
        max_size: Maximum size of the chunk
        
    Returns:
        Character index for the split point
    """
    # Default to max size if the text is shorter than that
    if len(text) <= max_size:
        return len(text)
    
    # Try to find a paragraph break
    last_paragraph = text[:max_size].rfind('\n\n')
    if last_paragraph != -1 and last_paragraph > max_size * 0.5:
        return last_paragraph + 2  # Include the double newline
    
    # Try to find a line break
    last_line = text[:max_size].rfind('\n')
    if last_line != -1 and last_line > max_size * 0.7:
        return last_line + 1  # Include the newline
    
    # Try to find a sentence end (., !, ?)
    for i in range(max_size - 1, max_size // 2, -1):
        if i < len(text) and text[i] in '.!?' and (i + 1 >= len(text) or text[i + 1].isspace()):
            return i + 1  # Include the punctuation
    
    # Fall back to a word boundary
    for i in range(max_size - 1, max_size // 2, -1):
        if i < len(text) and text[i].isspace():
            return i + 1  # Include the space
    
    # If all else fails, just split at max_size
    return max_size


def _has_semantic_structure(text: str) -> bool:
    """
    Determine if the text has semantic structure like headings or paragraphs.
    
    Args:
        text: Text to analyze
        
    Returns:
        True if the text has semantic structure, False otherwise
    """
    # Check for Markdown headings
    if re.search(r'^#+\s+', text, re.MULTILINE):
        return True
        
    # Check for multiple paragraphs
    if text.count('\n\n') > 2:
        return True
        
    return False


def _estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in the text (rough approximation).
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4