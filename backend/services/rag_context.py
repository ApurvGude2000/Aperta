# ABOUTME: RAG context manager for loading, chunking, and retrieving transcript context
# ABOUTME: Supports loading from files or strings with semantic text chunking

import os
from typing import List, Optional, Dict
from pathlib import Path
import re


class RAGContextManager:
    """
    Manages transcript context for RAG (Retrieval-Augmented Generation).
    Loads transcripts, chunks them semantically, and retrieves relevant context.
    """
    
    def __init__(self, custom_prompt_path: Optional[str] = None):
        """
        Initialize the RAG context manager.
        
        Args:
            custom_prompt_path: Optional path to custom_prompt.txt file
        """
        self.chunks: List[Dict[str, str]] = []
        self.full_text: str = ""
        self.custom_prompt: str = ""
        
        # Load custom prompt if path provided
        if custom_prompt_path and os.path.exists(custom_prompt_path):
            with open(custom_prompt_path, 'r', encoding='utf-8') as f:
                self.custom_prompt = f.read()
    
    def load_transcript(self, file_path_or_text: str) -> None:
        """
        Load transcript from file path or directly from text string.
        
        Args:
            file_path_or_text: File path to transcript or raw text content
        """
        # Check if it's a file path
        if os.path.exists(file_path_or_text):
            with open(file_path_or_text, 'r', encoding='utf-8') as f:
                self.full_text = f.read()
        else:
            # Treat as raw text
            self.full_text = file_path_or_text
        
        # Auto-chunk after loading
        self.chunk_text(self.full_text)
    
    def chunk_text(self, text: str, chunk_size: int = 500) -> List[Dict[str, str]]:
        """
        Chunk text into semantic segments based on paragraphs and sentences.
        
        Args:
            text: Text to chunk
            chunk_size: Target size for each chunk in characters
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Split by double newlines (paragraphs) first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk_size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > chunk_size:
                chunks.append({
                    'text': current_chunk.strip(),
                    'index': chunk_index,
                    'size': len(current_chunk)
                })
                current_chunk = ""
                chunk_index += 1
            
            # Add paragraph to current chunk
            current_chunk += para + "\n\n"
        
        # Add final chunk if exists
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'index': chunk_index,
                'size': len(current_chunk)
            })
        
        self.chunks = chunks
        return chunks
    
    def get_relevant_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve most relevant chunks for a given query.
        Uses simple keyword matching for now (can be upgraded to embeddings later).
        
        Args:
            query: Query string to match against chunks
            top_k: Number of top chunks to return
            
        Returns:
            List of relevant chunk texts
        """
        if not self.chunks:
            return []
        
        # Extract query keywords (simple approach)
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Score each chunk based on keyword overlap
        scored_chunks = []
        for chunk in self.chunks:
            chunk_lower = chunk['text'].lower()
            chunk_words = set(re.findall(r'\b\w+\b', chunk_lower))
            
            # Calculate overlap score
            overlap = len(query_words & chunk_words)
            score = overlap / len(query_words) if query_words else 0
            
            scored_chunks.append({
                'chunk': chunk,
                'score': score
            })
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top_k chunks
        return [item['chunk']['text'] for item in scored_chunks[:top_k]]
    
    def get_full_context(self) -> str:
        """
        Get the complete transcript text.
        
        Returns:
            Full transcript text
        """
        return self.full_text
    
    def get_custom_prompt(self) -> str:
        """
        Get the custom prompt if loaded.
        
        Returns:
            Custom prompt text
        """
        return self.custom_prompt
    
    def clear(self) -> None:
        """
        Clear all loaded context and chunks.
        """
        self.chunks = []
        self.full_text = ""
        # Don't clear custom_prompt as it's configuration
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about loaded context.
        
        Returns:
            Dictionary with context statistics
        """
        return {
            'total_chunks': len(self.chunks),
            'total_characters': len(self.full_text),
            'has_custom_prompt': bool(self.custom_prompt),
            'avg_chunk_size': sum(c['size'] for c in self.chunks) / len(self.chunks) if self.chunks else 0
        }
