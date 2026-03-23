"""
Flight search tool
Note: This uses simulated data. In production, integrate with real flight APIs
like Amadeus, Skyscanner, or SerpAPI
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
from travel_planner.utils.logger import logger


class FlightTool:
    """Tool for searching flights"""
    
    def __init__(self):
        # Simulated airline data
        self.airlines = [
            "United Airlines", "Delta Air Lines", "American Airlines",
            "Emirates", "Lufthansa", "British Airways", "Air France",
            "Singapore Airlines", "Qatar Airways", "Japan Airlines"
        ]
        
        # Simulated price ranges by distance category
        self.price_ranges = {
            "short": (150, 400),      # < 1000 miles
            "medium": (300, 800),     # 1000-3000 miles
            "long": (500, 1500),      # 3000-6000 miles
            "ultra_long": (800, 2500) # > 6000 miles
        }
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        travelers: int = 1,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search for flights
        
        Args:
            origin: Origin city/airport
            destination: Destination city/airport
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Optional return date for round trip
            travelers: Number of travelers
            max_results: Maximum number of flight options
            
        Returns:
            Dictionary with flight options
        """
        try:
            logger.info(f"Searching flights: {origin} → {destination}")
            
            # Determine distance category (simplified)
            distance_category = self._estimate_distance_category(origin, destination)
            
            # Generate flight options
            outbound_flights = self._generate_flights(
                origin, destination, departure_date, distance_category, max_results
            )
            
            result = {
                "success": True,
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "travelers": travelers,
                "outbound_flights": outbound_flights
            }
            
            # Add return flights if round trip
            if return_date:
                return_flights = self._generate_flights(
                    destination, origin, return_date, distance_category, max_results
                )
                result["return_date"] = return_date
                result["return_flights"] = return_flights
                result["trip_type"] = "round_trip"
            else:
                result["trip_type"] = "one_way"
            
            return result
            
        except Exception as e:
            logger.error(f"Flight search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cheapest_flight(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the cheapest flight option"""
        results = self.search_flights(origin, destination, departure_date, return_date)
        
        if not results["success"]:
            return results
        
        cheapest = min(results["outbound_flights"], key=lambda x: x["price"])
        
        result = {
            "success": True,
            "cheapest_outbound": cheapest
        }
        
        if "return_flights" in results:
            cheapest_return = min(results["return_flights"], key=lambda x: x["price"])
            result["cheapest_return"] = cheapest_return
            result["total_price"] = cheapest["price"] + cheapest_return["price"]
        else:
            result["total_price"] = cheapest["price"]
        
        return result
    
    def _estimate_distance_category(self, origin: str, destination: str) -> str:
        """Estimate distance category based on city names (simplified)"""
        # In production, use actual distance calculation
        # For now, use simple heuristics
        
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Check if same country (very simplified)
        common_countries = ["usa", "uk", "france", "germany", "japan", "china", "india"]
        
        # Ultra long: transcontinental/transoceanic
        if any(x in origin_lower for x in ["usa", "america", "york", "los angeles"]) and \
           any(x in dest_lower for x in ["tokyo", "sydney", "singapore", "hong kong"]):
            return "ultra_long"
        
        # Long: cross-continental
        if any(x in origin_lower for x in ["europe", "paris", "london"]) and \
           any(x in dest_lower for x in ["asia", "tokyo", "delhi", "dubai"]):
            return "long"
        
        # Medium: regional international
        if origin_lower.split(",")[0] != dest_lower.split(",")[0]:
            return "medium"
        
        # Short: domestic or nearby
        return "short"
    
    def _generate_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        distance_category: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate simulated flight options"""
        flights = []
        price_min, price_max = self.price_ranges[distance_category]
        
        # Base duration by category (in minutes)
        duration_bases = {
            "short": 90,
            "medium": 240,
            "long": 480,
            "ultra_long": 720
        }
        base_duration = duration_bases[distance_category]
        
        for i in range(count):
            # Random airline
            airline = random.choice(self.airlines)
            
            # Random price within range
            price = random.randint(price_min, price_max)
            
            # Number of stops (more stops = cheaper)
            stops = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
            if stops > 0:
                price = int(price * (1 - stops * 0.15))
            
            # Duration increases with stops
            duration = base_duration + (stops * 120) + random.randint(-30, 60)
            
            # Generate times
            departure_hour = random.randint(6, 20)
            departure_time = f"{departure_hour:02d}:{random.choice(['00', '30'])}"
            
            arrival_hour = (departure_hour + duration // 60) % 24
            arrival_time = f"{arrival_hour:02d}:{random.choice(['00', '30'])}"
            
            # Format duration
            hours = duration // 60
            mins = duration % 60
            duration_str = f"{hours}h {mins}m"
            
            flights.append({
                "airline": airline,
                "flight_number": f"{airline[:2].upper()}{random.randint(100, 999)}",
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration_str,
                "stops": stops,
                "price": price,
                "currency": "USD",
                "cabin_class": "Economy",
                "origin": origin,
                "destination": destination,
                "date": date
            })
        
        # Sort by price
        flights.sort(key=lambda x: x["price"])
        return flights
    
    def calculate_total_cost(
        self,
        outbound_price: float,
        return_price: float,
        travelers: int
    ) -> Dict[str, Any]:
        """Calculate total flight cost for multiple travelers"""
        total_per_person = outbound_price + return_price
        total_cost = total_per_person * travelers
        
        return {
            "per_person": total_per_person,
            "travelers": travelers,
            "total_cost": total_cost,
            "currency": "USD"
        }


__all__ = ["FlightTool"]
