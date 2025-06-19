"""
Tests for web search functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from web_search import SearchResult, search_web, WebSearch

class TestWebSearch(unittest.TestCase):
    
    def setUp(self):
        self.test_query = "Python programming"
    
    @patch('web_search.DDGS')
    def test_basic_search(self, mock_ddgs):
        """Test basic web search functionality"""
        # Mock successful search results
        mock_results = [
            {
                'title': 'Python Programming',
                'link': 'https://python.org',
                'body': 'Python is a programming language'
            }
        ]
        
        # Mock the DDGS instance and its text method
        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_results
        mock_ddgs.return_value = mock_instance
        
        results = search_web(self.test_query)
        self.assertIsInstance(results, str)
        self.assertIn("Python Programming", results)
    
    def test_empty_query(self):
        """Test search with empty query"""
        # Empty query should return "No results found."
        results = search_web("")
        self.assertEqual(results, "No results found.", "Empty query should return no results message")
    
    @patch('web_search.DDGS')
    def test_formatted_output(self, mock_ddgs):
        """Test formatted search results"""
        # Mock successful search results
        mock_results = [
            {
                'title': 'Python Programming',
                'link': 'https://python.org',
                'body': 'Python is a programming language'
            }
        ]
        
        # Mock the DDGS instance and its text method
        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_results
        mock_ddgs.return_value = mock_instance
        
        results = search_web(self.test_query)
        self.assertIn("Search Results:", results)
        self.assertIn("Python Programming", results)
    
    @patch('web_search.DDGS')
    def test_max_results(self, mock_ddgs):
        """Test that max_results parameter is respected"""
        # Mock many results
        mock_results = [
            {
                'title': f'Result {i}',
                'link': f'https://example{i}.com',
                'body': f'Snippet {i}'
            }
            for i in range(10)
        ]
        
        # Mock the DDGS instance and its text method
        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_results
        mock_ddgs.return_value = mock_instance
        
        results = search_web(self.test_query, max_results=3)
        # Count the number of numbered results in the formatted output
        result_count = results.count("1. **") + results.count("2. **") + results.count("3. **")
        self.assertEqual(result_count, 3, "Should respect max_results parameter")
    
    @patch('web_search.DDGS')
    def test_rate_limit_handling(self, mock_ddgs):
        """Test handling of rate limiting"""
        # Mock rate limit error
        mock_instance = MagicMock()
        mock_instance.text.side_effect = Exception("Rate limit")
        mock_ddgs.return_value = mock_instance
        
        results = search_web(self.test_query)
        # Now returns fallback results instead of "No results found."
        self.assertIn("Search Results:", results, "Should return fallback results")
        self.assertIn("Unable to perform real-time search", results, "Should indicate search failure")
    
    def test_search_result_creation(self):
        """Test SearchResult object creation"""
        result = SearchResult(
            title="Test Title",
            link="https://test.com",
            snippet="Test snippet"
        )
        self.assertEqual(result.title, "Test Title")
        self.assertEqual(result.link, "https://test.com")
        self.assertEqual(result.snippet, "Test snippet")
    
    def test_search_result_string_representation(self):
        """Test SearchResult string representation"""
        result = SearchResult(
            title="Test Title",
            link="https://test.com",
            snippet="Test snippet"
        )
        string_repr = str(result)
        self.assertIn("Test Title", string_repr)
        self.assertIn("https://test.com", string_repr)
        self.assertIn("Test snippet", string_repr)
    
    def test_web_search_class(self):
        """Test WebSearch class directly"""
        searcher = WebSearch()
        self.assertIsNotNone(searcher)
        self.assertEqual(searcher.max_results, 5)
        self.assertEqual(searcher.region, 'wt-wt')

if __name__ == '__main__':
    unittest.main() 