"""
BasicChat - AI Chat Application

A production-ready Streamlit application for AI-powered conversations
with advanced reasoning capabilities and document processing.

This package contains the core application logic organized into modules:
- core: Main application logic and UI components
- reasoning: Advanced reasoning engines (Chain-of-Thought, Multi-Step, Agent-Based)
- session: Session management and persistence
- api: External API integrations (Ollama, web search)
- utils: Utility modules (async operations, caching, tools)
- config: Configuration management
- database: Database operations and migrations
"""

__version__ = "1.0.0"
__author__ = "Souriya Khaosanga"
__email__ = "souriya@chainable.ai"

# Import configuration and session management for easy access
from .config.config import config
from .session.session_manager import session_manager

__all__ = [
    "config", 
    "session_manager"
] 