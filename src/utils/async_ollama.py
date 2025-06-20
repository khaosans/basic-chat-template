"""
Async Ollama client with connection pooling and rate limiting
"""

import asyncio
import json
import time
from typing import Dict, Optional, AsyncGenerator, Any
import aiohttp
import logging
from asyncio_throttle import Throttler

from src.config import config
from src.utils.caching import response_cache

logger = logging.getLogger(__name__)

class AsyncOllamaClient:
    """Async client for Ollama API with connection pooling and caching"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.ollama_model
        self.api_url = f"{config.ollama_url}/generate"
        self.base_url = config.get_ollama_base_url()
        
        # Lazy initialization of async resources
        self.connector = None
        self.throttler = None
        self._session = None
        self._session_lock = None
    
    def _ensure_async_resources(self):
        """Initialize async resources if not already done"""
        if self.connector is None:
            # Connection pooling
            self.connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
        
        if self.throttler is None:
            # Rate limiting
            self.throttler = Throttler(
                rate_limit=config.rate_limit,
                period=config.rate_limit_period
            )
        
        if self._session_lock is None:
            self._session_lock = asyncio.Lock()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling"""
        self._ensure_async_resources()
        
        if self._session is None or self._session.closed:
            async with self._session_lock:
                if self._session is None or self._session.closed:
                    timeout = aiohttp.ClientTimeout(
                        total=config.request_timeout,
                        connect=config.connect_timeout
                    )
                    self._session = aiohttp.ClientSession(
                        connector=self.connector,
                        timeout=timeout,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "BasicChat/1.0"
                        }
                    )
        return self._session
    
    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        self._ensure_async_resources()
        session = await self._get_session()
        
        for attempt in range(config.max_retries):
            try:
                async with self.throttler:
                    async with session.post(
                        self.api_url,
                        json=payload,
                        raise_for_status=True
                    ) as response:
                        return await response.json()
                        
            except aiohttp.ClientError as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{config.max_retries}): {e}")
                if attempt == config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error in request: {e}")
                raise
    
    async def _stream_request(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Make streaming HTTP request"""
        self._ensure_async_resources()
        session = await self._get_session()
        
        for attempt in range(config.max_retries):
            try:
                async with self.throttler:
                    async with session.post(
                        self.api_url,
                        json=payload,
                        raise_for_status=True
                    ) as response:
                        async for line in response.content:
                            if line:
                                try:
                                    chunk_data = json.loads(line.decode().strip())
                                    response_text = chunk_data.get("response", "")
                                    if response_text:
                                        yield response_text
                                except json.JSONDecodeError:
                                    continue
                        return
                        
            except aiohttp.ClientError as e:
                logger.warning(f"Stream request failed (attempt {attempt + 1}/{config.max_retries}): {e}")
                if attempt == config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Unexpected error in stream request: {e}")
                raise
    
    async def query_async(self, payload: Dict[str, Any], use_cache: bool = True) -> Optional[str]:
        """Query Ollama API asynchronously with caching"""
        user_input = payload.get("inputs", "")
        
        # Generate cache key
        cache_key = response_cache.get_cache_key(
            query=user_input,
            model=self.model_name,
            temperature=payload.get("temperature", config.temperature),
            max_tokens=payload.get("max_tokens", config.max_tokens)
        )
        
        # Check cache first
        if use_cache:
            cached_response = response_cache.get(cache_key)
            if cached_response:
                logger.info(f"Cache hit for query: {user_input[:50]}...")
                return cached_response
        
        # Prepare Ollama payload
        ollama_payload = {
            "model": self.model_name,
            "prompt": user_input,
            "system": payload.get("system", ""),
            "stream": False,
            "options": {
                "temperature": payload.get("temperature", config.temperature),
                "num_predict": payload.get("max_tokens", config.max_tokens)
            }
        }
        
        try:
            start_time = time.time()
            response = await self._make_request(ollama_payload)
            response_time = time.time() - start_time
            
            result = response.get("response", "")
            
            # Cache the result
            if use_cache and result:
                response_cache.set(cache_key, result)
            
            logger.info(f"Query completed in {response_time:.2f}s: {user_input[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
    
    async def query_stream_async(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Query Ollama API with streaming response"""
        user_input = payload.get("inputs", "")
        
        # Prepare Ollama payload for streaming
        ollama_payload = {
            "model": self.model_name,
            "prompt": user_input,
            "system": payload.get("system", ""),
            "stream": True,
            "options": {
                "temperature": payload.get("temperature", config.temperature),
                "num_predict": payload.get("max_tokens", config.max_tokens)
            }
        }
        
        try:
            async for chunk in self._stream_request(ollama_payload):
                yield chunk
        except Exception as e:
            logger.error(f"Stream query failed: {e}")
            yield f"Error: {str(e)}"
    
    async def get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current model"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    for model in models:
                        if model.get("name") == self.model_name:
                            return model
            return None
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

class AsyncOllamaChat:
    """Enhanced async chat interface with caching and streaming"""
    
    def __init__(self, model_name: str = None):
        self.client = AsyncOllamaClient(model_name)
        self.system_prompt = """
You are a helpful and knowledgeable AI assistant with advanced reasoning capabilities. You can:
1. Answer questions about a wide range of topics using logical reasoning
2. Summarize documents that have been uploaded with detailed analysis
3. Have natural, friendly conversations with enhanced understanding
4. Break down complex problems into manageable steps
5. Provide well-reasoned explanations for your answers

Please be concise, accurate, and helpful in your responses. 
If you don't know something, just say so instead of making up information.
Always show your reasoning process when appropriate.
"""
    
    async def query(self, payload: Dict[str, Any], use_cache: bool = True) -> Optional[str]:
        """Query with caching support"""
        payload["system"] = self.system_prompt
        return await self.client.query_async(payload, use_cache)
    
    async def query_stream(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Query with streaming response"""
        payload["system"] = self.system_prompt
        async for chunk in self.client.query_stream_async(payload):
            yield chunk
    
    async def close(self):
        """Close the client"""
        await self.client.close()
    
    async def health_check(self) -> bool:
        """Check service health"""
        return await self.client.health_check()

# Global async chat instance
async_chat = AsyncOllamaChat() 