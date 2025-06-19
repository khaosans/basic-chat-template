"""
Tests for document processing functionality
"""

import pytest
from document_processor import DocumentProcessor

def test_document_processor_initialization():
    """Test DocumentProcessor initialization"""
    processor = DocumentProcessor()
    assert processor is not None
    assert hasattr(processor, 'embeddings')
    assert hasattr(processor, 'text_splitter')

def test_text_splitting(sample_text):
    """Test text splitting functionality"""
    processor = DocumentProcessor()
    chunks = processor.text_splitter.split_text(sample_text)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_empty_document_handling():
    """Test handling of empty documents"""
    processor = DocumentProcessor()
    empty_text = ""
    chunks = processor.text_splitter.split_text(empty_text)
    assert len(chunks) == 0

def test_document_metadata_handling(sample_document):
    """Test document metadata handling"""
    processor = DocumentProcessor()
    assert sample_document['metadata']['source'] == 'test'
    assert sample_document['metadata']['type'] == 'text'

@pytest.mark.asyncio
async def test_async_processing(sample_text):
    """Test async document processing"""
    processor = DocumentProcessor()
    chunks = processor.text_splitter.split_text(sample_text)
    assert len(chunks) > 0 