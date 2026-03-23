"""
Hotel Agent - Handles accommodation search and recommendations
"""

from typing import Dict, Any, Optional
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.tools.hotel_tool import HotelTool
from travel_planner.utils.logger import logger


class HotelAgent(BaseAgent):
    """Agent specialized in hotel search and accommodation recommendations"""
    
    def __init__(self):
        super().__init__(
            name="Hotel Agent",
            role="accommodation specialist",
            goal="find the best hotel options matching traveler preferences, budget, and requirements"
        )
        self.hotel_tool = HotelTool()
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute hotel search task
        
        Args:
            task: Hotel search task
            context: Context with travel details
            
        Returns:
            Hotel search results and recommendations
        """
        try:
            if not context:
                return {"success": False, "error": "No context provided"}
            
            destination = context.get("destination")
            check_in = context.get("start_date")
            check_out = context.get("end_date")
            travelers = context.get("travelers", 2)
            budget = context.get("budget")
            preferences = context.get("preferences", {})
            
            if not all([destination, check_in, check_out]):
                return {
                    "success": False,
                    "error": "Missing required information: destination, start_date, end_date"
                }
            
            logger.info(f"Searching hotels in {destination}")
            
            # Determine rooms needed (assume 2 people per room)
            rooms = (travelers + 1) // 2
            
            # Get min rating from preferences
            min_rating = preferences.get("min_hotel_rating", 3.0)
            
            # Search hotels
            hotel_results = self.hotel_tool.search_hotels(
                destination=destination,
                check_in=check_in,
                check_out=check_out,
                guests=travelers,
                rooms=rooms,
                min_rating=min_rating,
                max_results=10
            )
            
            if not hotel_results["success"]:
                return hotel_results
            
            # Filter by budget if specified
            hotels = hotel_results["hotels"]
            if budget:
                # Allocate 30% of total budget to accommodation
                accommodation_budget = budget * 0.3
                per_night_budget = accommodation_budget / hotel_results["nights"]
                hotels = [h for h in hotels if h["price_per_night"] <= per_night_budget * 1.2]
            
            # Generate recommendations
            recommendation_prompt = f"""
            Hotel options in {destination} ({hotel_results['nights']} nights):
            {hotels[:5]}
            
            Travelers: {travelers} (needing {rooms} room(s))
            Budget: ${budget if budget else 'flexible'}
            Preferences: {preferences}
            
            Provide:
            1. Top 3 recommended hotels and why
            2. Best value option (balance of price, rating, and location)
            3. Best location for sightseeing
            4. Any important considerations
            
            Be specific with hotel names and prices.
            """
            
            recommendations = self.generate_response(recommendation_prompt, context)
            
            # Get cheapest and best rated options
            if hotels:
                cheapest = min(hotels, key=lambda x: x["price_per_night"])
                best_rated = max(hotels, key=lambda x: x["rating"])
            else:
                cheapest = None
                best_rated = None
            
            return {
                "success": True,
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "nights": hotel_results["nights"],
                "travelers": travelers,
                "rooms": rooms,
                "hotel_results": hotels[:8],
                "recommendations": recommendations,
                "cheapest_option": cheapest,
                "best_rated_option": best_rated,
                "estimated_cost": cheapest["total_cost"] if cheapest else None
            }
            
        except Exception as e:
            logger.error(f"Hotel agent error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_budget_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        max_budget: float,
        min_rating: float = 3.0
    ) -> Dict[str, Any]:
        """
        Find hotels within budget
        
        Args:
            destination: Destination city
            check_in: Check-in date
            check_out: Check-out date
            max_budget: Maximum total budget for accommodation
            min_rating: Minimum acceptable rating
            
        Returns:
            Budget-friendly hotel options
        """
        try:
            results = self.hotel_tool.search_hotels(
                destination, check_in, check_out,
                min_rating=min_rating, max_results=15
            )
            
            if not results["success"]:
                return results
            
            # Filter by total budget
            budget_hotels = [h for h in results["hotels"] if h["total_cost"] <= max_budget]
            budget_hotels.sort(key=lambda x: (-x["rating"], x["total_cost"]))
            
            return {
                "success": True,
                "destination": destination,
                "nights": results["nights"],
                "max_budget": max_budget,
                "hotels_within_budget": budget_hotels[:8],
                "count": len(budget_hotels)
            }
            
        except Exception as e:
            logger.error(f"Budget hotel search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def recommend_by_location(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        preferred_area: str
    ) -> Dict[str, Any]:
        """
        Recommend hotels in specific area
        
        Args:
            destination: Destination city
            check_in: Check-in date
            check_out: Check-out date
            preferred_area: Preferred area/neighborhood
            
        Returns:
            Hotels in preferred area
        """
        try:
            results = self.hotel_tool.search_hotels(
                destination, check_in, check_out, max_results=15
            )
            
            if not results["success"]:
                return results
            
            # Filter by location (simple string matching)
            area_hotels = [
                h for h in results["hotels"]
                if preferred_area.lower() in h["location"].lower()
            ]
            
            return {
                "success": True,
                "destination": destination,
                "preferred_area": preferred_area,
                "hotels_in_area": area_hotels,
                "count": len(area_hotels)
            }
            
        except Exception as e:
            logger.error(f"Location-based search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["HotelAgent"]
