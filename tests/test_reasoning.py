"""
Tests for the reasoning engine functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.reasoning import (
    ReasoningAgent,
    ReasoningChain,
    MultiStepReasoning,
    ReasoningResult
)
from src.utils.async_ollama import AsyncOllamaClient, AsyncOllamaChat

def test_reasoning_result_creation():
    """Test creation of ReasoningResult"""
    result = ReasoningResult(
        content="Test content",
        reasoning_steps=["Step 1", "Step 2"],
        confidence=0.9,
        sources=["test"],
        success=True
    )
    assert result.content == "Test content"
    assert len(result.reasoning_steps) == 2
    assert result.confidence == 0.9
    assert result.success is True

def test_chain_of_thought(test_model_name, sample_query):
    """Test chain-of-thought reasoning"""
    chain = ReasoningChain(model_name=test_model_name)
    result = chain.execute_reasoning(sample_query)
    
    assert isinstance(result, ReasoningResult)
    assert result.content is not None
    assert len(result.reasoning_steps) > 0
    assert result.confidence > 0
    assert result.success is True

def test_multi_step_reasoning(test_model_name, sample_query):
    """Test multi-step reasoning"""
    multi_step = MultiStepReasoning(doc_processor=None, model_name=test_model_name)
    result = multi_step.step_by_step_reasoning(sample_query)
    
    assert isinstance(result, ReasoningResult)
    assert result.content is not None
    assert len(result.reasoning_steps) > 0
    assert result.confidence > 0
    assert result.success is True

def test_agent_based_reasoning(test_model_name, sample_query):
    """Test agent-based reasoning"""
    agent = ReasoningAgent(model_name=test_model_name)
    result = agent.run(sample_query)
    
    assert isinstance(result, ReasoningResult)
    assert result.content is not None
    assert len(result.reasoning_steps) > 0
    assert result.confidence > 0
    assert result.success is True

def test_error_handling():
    """Test error handling in reasoning components"""
    # Test with invalid model name
    chain = ReasoningChain(model_name="invalid_model")
    result = chain.execute_reasoning("test query")
    
    assert result.success is False
    assert result.error is not None
    assert result.confidence == 0.0

@pytest.mark.parametrize("reasoning_class", [
    ReasoningChain,
    lambda m: MultiStepReasoning(None, m),
    ReasoningAgent
])
def test_reasoning_components(reasoning_class, test_model_name):
    """Test all reasoning components with same input"""
    component = reasoning_class(test_model_name)
    query = "What is 2 + 2?"
    
    if isinstance(component, MultiStepReasoning):
        result = component.step_by_step_reasoning(query)
    elif isinstance(component, ReasoningAgent):
        result = component.run(query)
    else:
        result = component.execute_reasoning(query)
    
    assert isinstance(result, ReasoningResult)
    assert result.content is not None
    assert result.success is True

# New async functionality tests
class TestAsyncFunctionality:
    """Test async functionality integration"""
    
    @pytest.mark.asyncio
    async def test_async_ollama_client_init(self, test_model_name):
        """Test AsyncOllamaClient initialization"""
        client = AsyncOllamaClient(test_model_name)
        assert client.model_name == test_model_name
        assert client.api_url == f"http://localhost:11434/api/generate"
        # Resources are lazily initialized
        assert client.connector is None
        assert client.throttler is None
        
        # After calling _ensure_async_resources in async context, they should be initialized
        client._ensure_async_resources()
        assert client.connector is not None
        assert client.throttler is not None
    
    def test_async_ollama_chat_init(self, test_model_name):
        """Test AsyncOllamaChat initialization"""
        chat = AsyncOllamaChat(test_model_name)
        assert chat.client is not None
        assert isinstance(chat.client, AsyncOllamaClient)
        assert chat.system_prompt is not None
    
    @pytest.mark.asyncio
    async def test_async_chat_query(self, test_model_name, sample_query):
        """Test async chat query functionality"""
        chat = AsyncOllamaChat(test_model_name)
        
        # Mock the async client to avoid actual API calls
        with patch.object(chat.client, 'query_async', return_value="Mock response") as mock_query:
            result = await chat.query({"inputs": sample_query})
            assert result == "Mock response"
            mock_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_health_check(self, test_model_name):
        """Test async health check"""
        chat = AsyncOllamaChat(test_model_name)
        
        # Mock the health check
        with patch.object(chat.client, 'health_check', return_value=True) as mock_health:
            result = await chat.health_check()
            assert result is True
            mock_health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_stream_query(self, test_model_name):
        """Test async streaming query"""
        chat = AsyncOllamaChat(test_model_name)
        
        # Mock the stream response
        async def mock_stream():
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"
        
        with patch.object(chat.client, 'query_stream_async', return_value=mock_stream()) as mock_stream_method:
            chunks = []
            async for chunk in chat.query_stream({"inputs": "test"}):
                chunks.append(chunk)
            
            assert chunks == ["chunk1", "chunk2", "chunk3"]
            mock_stream_method.assert_called_once() 