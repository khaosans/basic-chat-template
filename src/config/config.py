"""
Configuration management for BasicChat application
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

@dataclass
class SessionConfig:
    """Session management configuration"""
    auto_save_interval: int = int(os.getenv("SESSION_AUTO_SAVE_INTERVAL", "5"))
    max_sessions_per_user: int = int(os.getenv("SESSION_MAX_PER_USER", "100"))
    session_retention_days: int = int(os.getenv("SESSION_RETENTION_DAYS", "365"))
    enable_auto_save: bool = os.getenv("SESSION_ENABLE_AUTO_SAVE", "true").lower() == "true"
    enable_session_search: bool = os.getenv("SESSION_ENABLE_SEARCH", "true").lower() == "true"
    export_formats: List[str] = field(default_factory=lambda: ["json", "markdown"])
    database_path: str = os.getenv("SESSION_DB_PATH", "./chat_sessions.db")
    cleanup_interval_hours: int = int(os.getenv("SESSION_CLEANUP_INTERVAL", "24"))

@dataclass
class AppConfig:
    """Application configuration with environment variable support"""
    
    # Ollama Configuration
    ollama_url: str = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # LLM Parameters
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2048"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Caching Configuration
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))
    cache_maxsize: int = int(os.getenv("CACHE_MAXSIZE", "1000"))
    enable_caching: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    # Performance Configuration
    enable_streaming: bool = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    connect_timeout: int = int(os.getenv("CONNECT_TIMEOUT", "5"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    rate_limit: int = int(os.getenv("RATE_LIMIT", "10"))
    rate_limit_period: int = int(os.getenv("RATE_LIMIT_PERIOD", "1"))
    
    # Redis Configuration (for distributed caching)
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    redis_enabled: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_structured_logging: bool = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
    
    # Vector Store Configuration
    vectorstore_persist_directory: str = os.getenv("VECTORSTORE_DIR", "./chroma_db")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    
    # Session Management Configuration
    session: SessionConfig = field(default_factory=SessionConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables"""
        return cls()
    
    def get_ollama_base_url(self) -> str:
        """Get Ollama base URL without /api suffix"""
        return self.ollama_url.replace("/api", "")
    
    def validate(self) -> bool:
        """Validate configuration values"""
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if self.max_tokens < 1:
            raise ValueError("Max tokens must be positive")
        if self.cache_ttl < 0:
            raise ValueError("Cache TTL must be non-negative")
        return True

# Global configuration instance
config = AppConfig.from_env() 