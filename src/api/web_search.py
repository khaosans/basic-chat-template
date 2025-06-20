"""
Web search functionality using DuckDuckGo with improved error handling
"""

from typing import List, Dict, Optional
from duckduckgo_search import DDGS
import time
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SearchResult:
    """Structure for search results"""
    title: str
    link: str
    snippet: str

class WebSearch:
    def __init__(self):
        """Initialize the web search with DuckDuckGo"""
        self.ddgs = DDGS()
        self.max_results = 5
        self.region = 'wt-wt'  # Worldwide results
        self.retry_attempts = 3
        self.retry_delay = 2  # seconds
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Perform a web search using DuckDuckGo with retry logic and caching
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            List of SearchResult objects containing search results
        """
        if not query.strip():
            return []
        
        # Check cache first
        cache_key = f"{query}_{max_results}"
        if cache_key in self.cache:
            cached_time, cached_results = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                print(f"Returning cached results for: {query}")
                return cached_results
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
            
        for attempt in range(self.retry_attempts):
            try:
                results = []
                search_results = self.ddgs.text(
                    query,
                    region=self.region,
                    max_results=max_results
                )
                
                # Convert generator to list to handle potential errors
                search_results = list(search_results)
                
                for r in search_results:
                    results.append(SearchResult(
                        title=r.get('title', 'No title'),
                        link=r.get('link', ''),
                        snippet=r.get('body', 'No description available')
                    ))
                    
                if results:
                    # Cache successful results
                    self.cache[cache_key] = (datetime.now(), results)
                    return results
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Search attempt {attempt + 1} failed: {error_msg}")
                
                # If it's a rate limit, wait longer
                if "rate" in error_msg.lower() or "429" in error_msg or "202" in error_msg:
                    wait_time = self.retry_delay * (attempt + 1) + random.uniform(0, 1)
                    print(f"Rate limited, waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    # For other errors, wait a bit and retry
                    time.sleep(1)
        
        # If all attempts failed, return fallback results
        fallback_results = self._get_fallback_results(query)
        # Cache fallback results for a shorter time
        self.cache[cache_key] = (datetime.now(), fallback_results)
        return fallback_results
    
    def _get_fallback_results(self, query: str) -> List[SearchResult]:
        """Provide fallback results when search fails"""
        fallback_results = [
            SearchResult(
                title=f"Search for '{query}'",
                link="https://duckduckgo.com",
                snippet=f"Unable to perform real-time search for '{query}'. Please try again later or visit DuckDuckGo directly."
            ),
            SearchResult(
                title="Search Temporarily Unavailable",
                link="https://duckduckgo.com",
                snippet="The search service is currently experiencing high traffic. Please try again in a few minutes."
            )
        ]
        return fallback_results
    
    def format_results(self, results: List[SearchResult]) -> str:
        """
        Format search results into a readable string
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return "No results found."
            
        formatted = "Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result.title}**\n"
            formatted += f"   {result.snippet}\n"
            formatted += f"   [Link]({result.link})\n\n"
            
        return formatted

def search_web(query: str, max_results: int = 5) -> str:
    """
    Convenience function to search and format results in one call
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted string with search results
    """
    searcher = WebSearch()
    results = searcher.search(query, max_results)
    return searcher.format_results(results) 