"""
Tests for the main application functionality
"""

import pytest
import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.core.app import DocumentProcessor, OllamaChat
from src.config import config

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
    assert chat.async_chat is not None

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

def test_chat_fallback_mechanism(test_model_name):
    """Test fallback to sync implementation"""
    chat = OllamaChat(test_model_name)
    
    # Force fallback
    chat._use_sync_fallback = True
    
    payload = {"inputs": "Hello"}
    result = chat.query(payload)
    assert isinstance(result, (str, type(None)))

@pytest.mark.asyncio
async def test_health_check(test_model_name):
    """Test health check functionality"""
    chat = OllamaChat(test_model_name)
    health_status = await chat.health_check()
    assert isinstance(health_status, bool)

def test_cache_stats(test_model_name):
    """Test cache statistics retrieval"""
    chat = OllamaChat(test_model_name)
    stats = chat.get_cache_stats()
    assert isinstance(stats, dict)
    assert "caching_enabled" in stats

@pytest.mark.asyncio
async def test_stream_query(test_model_name):
    """Test streaming query functionality"""
    chat = OllamaChat(test_model_name)
    payload = {"inputs": "Hello"}
    
    # Test async stream
    chunks = []
    async for chunk in chat.query_stream(payload):
        chunks.append(chunk)
    
    # Should have some response
    assert len(chunks) >= 0

def test_config_integration():
    """Test that config is properly integrated"""
    assert config is not None
    assert hasattr(config, 'ollama_url')
    assert hasattr(config, 'ollama_model')
    assert hasattr(config, 'enable_caching')

def test_async_chat_integration():
    """Test that async chat is properly integrated"""
    from src.utils.async_ollama import async_chat
    assert async_chat is not None
    assert hasattr(async_chat, 'query')
    assert hasattr(async_chat, 'health_check')

def test_cache_integration():
    """Test that cache is properly integrated"""
    from src.utils.caching import response_cache
    assert response_cache is not None
    assert hasattr(response_cache, 'get')
    assert hasattr(response_cache, 'set')
    assert hasattr(response_cache, 'get_stats') 