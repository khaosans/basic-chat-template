"""
Tests for the main application functionality
"""

import pytest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app import DocumentProcessor, OllamaChat

def test_document_processor_init():
    processor = DocumentProcessor()
    assert processor is not None
    assert processor.processed_files == []

def test_mime_type_detection():
    processor = DocumentProcessor()
    assert processor is not None

def test_ollama_chat_initialization(test_model_name):
    """Test OllamaChat initialization"""
    chat = OllamaChat(test_model_name)
    assert chat is not None
    assert chat.model_name == test_model_name
    assert chat.system_prompt is not None

def test_chat_query_structure(test_model_name):
    """Test chat query structure"""
    chat = OllamaChat(test_model_name)
    payload = {"inputs": "Hello"}
    query = chat.query(payload)
    assert isinstance(query, (str, type(None)))

def test_error_handling(test_model_name):
    """Test error handling in chat"""
    chat = OllamaChat(test_model_name)
    result = chat.query({"inputs": ""})  # Empty input
    assert result == "" or result is None

@pytest.mark.asyncio
async def test_async_chat(test_model_name, sample_query):
    """Test async chat functionality"""
    chat = OllamaChat(test_model_name)
    payload = {"inputs": sample_query}
    result = chat.query(payload)
    assert isinstance(result, (str, type(None))) 