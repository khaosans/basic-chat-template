"""
Shared test fixtures and configuration
"""

import pytest
import os
import sys

# Add the project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return """This is a sample text for testing.
    It contains multiple lines and can be used
    for various test cases."""

@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "What is Python programming?"

@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "content": "Sample document content",
        "metadata": {
            "source": "test",
            "type": "text"
        }
    }

@pytest.fixture
def test_model_name():
    """Test model name"""
    return "mistral" 