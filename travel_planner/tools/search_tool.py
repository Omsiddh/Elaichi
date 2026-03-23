"""
Search tool for general web searches and destination research
"""

from typing import Dict, Any, List, Optional
import requests
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from travel_planner.utils.logger import logger


class SearchTool:
    """Tool for web searches and information gathering"""
    
    def __init__(self):
        try:
            self.ddg = DDGS()
        except Exception as e:
            logger.warning(f"Search tool initialization warning: {e}")
            self.ddg = None
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a web search
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.ddg:
            logger.warning("Search tool not available, returning empty results")
            return []
        
        try:
            results = []
            search_results = self.ddg.text(query, max_results=max_results)
            
            # Handle different return types
            if search_results:
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", "") or result.get("url", ""),
                        "snippet": result.get("body", "") or result.get("snippet", "")
                    })
            
            logger.info(f"Search completed: {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            logger.warning(f"Search error (returning empty): {e}")
            return []
    
    def search_attractions(self, destination: str) -> List[Dict[str, Any]]:
        """
        Search for tourist attractions in a destination
        
        Args:
            destination: Destination name
            
        Returns:
            List of attractions with information
        """
        query = f"top tourist attractions things to do in {destination}"
        return self.search(query, max_results=8)
    
    def search_restaurants(self, destination: str, cuisine: str = "") -> List[Dict[str, Any]]:
        """
        Search for restaurants in a destination
        
        Args:
            destination: Destination name
            cuisine: Optional cuisine type
            
        Returns:
            List of restaurant information
        """
        cuisine_filter = f"{cuisine} " if cuisine else ""
        query = f"best {cuisine_filter}restaurants in {destination}"
        return self.search(query, max_results=5)
    
    def search_local_tips(self, destination: str) -> List[Dict[str, Any]]:
        """
        Search for local tips and travel advice
        
        Args:
            destination: Destination name
            
        Returns:
            List of travel tips and advice
        """
        query = f"travel tips local advice visiting {destination}"
        return self.search(query, max_results=5)
    
    def search_transportation(self, destination: str) -> List[Dict[str, Any]]:
        """
        Search for transportation options in destination
        
        Args:
            destination: Destination name
            
        Returns:
            List of transportation information
        """
        query = f"public transportation getting around {destination}"
        return self.search(query, max_results=5)
    
    def get_destination_overview(self, destination: str) -> Dict[str, Any]:
        """
        Get comprehensive overview of a destination
        
        Args:
            destination: Destination name
            
        Returns:
            Dictionary with destination overview
        """
        overview_query = f"{destination} travel guide overview"
        overview_results = self.search(overview_query, max_results=3)
        
        return {
            "destination": destination,
            "overview": overview_results,
            "attractions": self.search_attractions(destination)[:5],
            "local_tips": self.search_local_tips(destination)[:3]
        }


__all__ = ["SearchTool"]
