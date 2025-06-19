"""
Tests for the reasoning engine functionality
"""

import pytest
from reasoning_engine import (
    ReasoningAgent,
    ReasoningChain,
    MultiStepReasoning,
    ReasoningResult
)

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