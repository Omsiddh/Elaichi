"""
Research Agent - Gathers destination information and recommendations
"""

from typing import Dict, Any, Optional
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.tools.search_tool import SearchTool
from travel_planner.utils.logger import logger


class ResearchAgent(BaseAgent):
    """Agent specialized in destination research"""
    
    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="destination research specialist",
            goal="gather comprehensive information about destinations including attractions, culture, and travel tips"
        )
        self.search_tool = SearchTool()
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute research task
        
        Args:
            task: Research task description
            context: Optional context with destination info
            
        Returns:
            Research results
        """
        try:
            destination = context.get("destination") if context else None
            
            if not destination:
                return {
                    "success": False,
                    "error": "No destination specified"
                }
            
            logger.info(f"Researching destination: {destination}")
            
            # Get comprehensive overview
            overview = self.search_tool.get_destination_overview(destination)
            
            # Generate insights using LLM
            research_prompt = f"""
            Based on the following research about {destination}, provide:
            1. A brief overview (2-3 sentences)
            2. Top 5 must-visit attractions with brief descriptions
            3. Local culture and customs travelers should know
            4. Best time to visit
            5. Transportation tips
            
            Research data:
            {overview}
            
            Provide practical, concise information useful for trip planning.
            """
            
            insights = self.generate_response(research_prompt, context)
            
            return {
                "success": True,
                "destination": destination,
                "raw_data": overview,
                "insights": insights,
                "attractions": overview.get("attractions", []),
                "local_tips": overview.get("local_tips", [])
            }
            
        except Exception as e:
            logger.error(f"Research error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def research_attractions(self, destination: str, interests: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Research attractions based on interests
        
        Args:
            destination: Destination name
            interests: List of interests (e.g., ["culture", "food", "adventure"])
            
        Returns:
            Curated attraction recommendations
        """
        try:
            attractions = self.search_tool.search_attractions(destination)
            
            if interests:
                interests_str = ", ".join(interests)
                filter_prompt = f"""
                From these attractions in {destination}:
                {attractions}
                
                Filter and rank them for someone interested in: {interests_str}
                Provide top 5 recommendations with brief explanations.
                """
                
                recommendations = self.generate_response(filter_prompt)
            else:
                recommendations = self.generate_response(
                    f"Summarize these top attractions in {destination}: {attractions}"
                )
            
            return {
                "success": True,
                "destination": destination,
                "interests": interests or ["general"],
                "recommendations": recommendations,
                "all_attractions": attractions
            }
            
        except Exception as e:
            logger.error(f"Attraction research error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def research_restaurants(self, destination: str, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Research restaurants and dining options
        
        Args:
            destination: Destination name
            preferences: Dining preferences (cuisine, budget, etc.)
            
        Returns:
            Restaurant recommendations
        """
        try:
            cuisine = preferences.get("cuisine", "") if preferences else ""
            restaurants = self.search_tool.search_restaurants(destination, cuisine)
            
            prompt = f"""
            Based on these restaurant options in {destination}:
            {restaurants}
            
            Preferences: {preferences or "general recommendations"}
            
            Provide top 5 restaurant recommendations with:
            - Name and cuisine type
            - Why it's recommended
            - Approximate price range
            """
            
            recommendations = self.generate_response(prompt)
            
            return {
                "success": True,
                "destination": destination,
                "preferences": preferences,
                "recommendations": recommendations,
                "restaurants_found": restaurants
            }
            
        except Exception as e:
            logger.error(f"Restaurant research error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["ResearchAgent"]
