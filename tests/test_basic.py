import unittest
from src.core.app import OllamaChat
from src.config import AppConfig, config
from src.utils.caching import MemoryCache, ResponseCache, response_cache

class TestBasicFunctionality(unittest.TestCase):
    def test_ollamachat_initialization(self):
        """Test that OllamaChat can be initialized"""
        chat = OllamaChat("mistral")
        self.assertIsInstance(chat, OllamaChat)
        self.assertEqual(chat.model_name, "mistral")
        self.assertIsNotNone(chat.async_chat)

class TestConfiguration(unittest.TestCase):
    def test_app_config_defaults(self):
        """Test AppConfig default values"""
        app_config = AppConfig()
        self.assertEqual(app_config.ollama_url, "http://localhost:11434/api")
        self.assertEqual(app_config.ollama_model, "mistral")
        self.assertEqual(app_config.max_tokens, 2048)
        self.assertEqual(app_config.temperature, 0.7)
        self.assertTrue(app_config.enable_caching)
    
    def test_app_config_validation(self):
        """Test AppConfig validation"""
        app_config = AppConfig()
        self.assertTrue(app_config.validate())
    
    def test_global_config_exists(self):
        """Test that global config instance exists"""
        self.assertIsNotNone(config)
        self.assertIsInstance(config, AppConfig)

class TestCaching(unittest.TestCase):
    def test_memory_cache_basic(self):
        """Test basic memory cache functionality"""
        cache = MemoryCache(ttl=60)
        
        # Test set and get
        self.assertTrue(cache.set("test_key", "test_value"))
        self.assertEqual(cache.get("test_key"), "test_value")
        
        # Test cache miss
        self.assertIsNone(cache.get("nonexistent_key"))
    
    def test_response_cache_basic(self):
        """Test basic response cache functionality"""
        cache = ResponseCache()
        
        # Test cache key generation
        key1 = cache.get_cache_key("test query", "mistral")
        key2 = cache.get_cache_key("test query", "mistral")
        self.assertEqual(key1, key2)
        
        # Test set and get
        self.assertTrue(cache.set("test_key", "test_value"))
        self.assertEqual(cache.get("test_key"), "test_value")
    
    def test_global_cache_exists(self):
        """Test that global cache instance exists"""
        self.assertIsNotNone(response_cache)
        self.assertIsInstance(response_cache, ResponseCache)

if __name__ == '__main__':
    unittest.main()