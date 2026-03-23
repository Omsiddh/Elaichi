"""
Flight Agent - Handles flight search and recommendations
"""

from typing import Dict, Any, Optional
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.tools.flight_tool import FlightTool
from travel_planner.utils.logger import logger


class FlightAgent(BaseAgent):
    """Agent specialized in flight search and booking recommendations"""
    
    def __init__(self):
        super().__init__(
            name="Flight Agent",
            role="flight search specialist",
            goal="find the best flight options matching traveler preferences and budget"
        )
        self.flight_tool = FlightTool()
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute flight search task
        
        Args:
            task: Flight search task
            context: Context with travel details
            
        Returns:
            Flight search results and recommendations
        """
        try:
            if not context:
                return {"success": False, "error": "No context provided"}
            
            origin = context.get("origin")
            destination = context.get("destination")
            departure_date = context.get("start_date")
            return_date = context.get("end_date")
            travelers = context.get("travelers", 1)
            budget = context.get("budget")
            
            if not all([origin, destination, departure_date]):
                return {
                    "success": False,
                    "error": "Missing required information: origin, destination, start_date"
                }
            
            logger.info(f"Searching flights: {origin} → {destination}")
            
            # Search flights
            flight_results = self.flight_tool.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                travelers=travelers,
                max_results=8
            )
            
            if not flight_results["success"]:
                return flight_results
            
            # Generate recommendations
            recommendation_prompt = f"""
            Flight search results for {origin} to {destination}:
            Outbound flights: {flight_results['outbound_flights'][:5]}
            {"Return flights: " + str(flight_results.get('return_flights', [])[:5]) if return_date else ""}
            
            Travelers: {travelers}
            Budget: ${budget if budget else 'flexible'}
            
            Provide:
            1. Top 3 recommended flight combinations and why
            2. Best value option (balance of price and convenience)
            3. Fastest option
            4. Tips for this route
            
            Be specific with flight numbers and prices.
            """
            
            recommendations = self.generate_response(recommendation_prompt, context)
            
            # Calculate total cost for cheapest option
            cheapest = self.flight_tool.get_cheapest_flight(
                origin, destination, departure_date, return_date
            )
            
            return {
                "success": True,
                "origin": origin,
                "destination": destination,
                "travelers": travelers,
                "flight_results": flight_results,
                "recommendations": recommendations,
                "cheapest_option": cheapest,
                "estimated_cost": cheapest.get("total_price", 0) * travelers if cheapest["success"] else None
            }
            
        except Exception as e:
            logger.error(f"Flight agent error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_budget_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str],
        max_budget: float
    ) -> Dict[str, Any]:
        """
        Find flights within budget
        
        Args:
            origin: Origin city
            destination: Destination city
            departure_date: Departure date
            return_date: Optional return date
            max_budget: Maximum budget per person
            
        Returns:
            Budget-friendly flight options
        """
        try:
            results = self.flight_tool.search_flights(
                origin, destination, departure_date, return_date, max_results=10
            )
            
            if not results["success"]:
                return results
            
            # Filter by budget
            budget_flights = []
            for out_flight in results["outbound_flights"]:
                if return_date and "return_flights" in results:
                    for ret_flight in results["return_flights"]:
                        total = out_flight["price"] + ret_flight["price"]
                        if total <= max_budget:
                            budget_flights.append({
                                "outbound": out_flight,
                                "return": ret_flight,
                                "total_price": total
                            })
                else:
                    if out_flight["price"] <= max_budget:
                        budget_flights.append({
                            "outbound": out_flight,
                            "total_price": out_flight["price"]
                        })
            
            budget_flights.sort(key=lambda x: x["total_price"])
            
            return {
                "success": True,
                "origin": origin,
                "destination": destination,
                "max_budget": max_budget,
                "flights_within_budget": budget_flights[:5],
                "count": len(budget_flights)
            }
            
        except Exception as e:
            logger.error(f"Budget flight search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["FlightAgent"]
