"""
Hotel search tool
Note: This uses simulated data. In production, integrate with real hotel APIs
like Booking.com, Hotels.com, or Amadeus
"""

from typing import Dict, Any, List, Optional
import random
from datetime import datetime, timedelta
from travel_planner.utils.logger import logger


class HotelTool:
    """Tool for searching hotels"""
    
    def __init__(self):
        # Simulated hotel chains and types
        self.hotel_names = [
            "Grand", "Royal", "Imperial", "Plaza", "Palace",
            "Boutique", "Central", "Downtown", "Historic", "Modern"
        ]
        
        self.hotel_types = [
            "Hotel", "Inn", "Resort", "Suites", "Lodge"
        ]
        
        # Price ranges by rating
        self.price_by_rating = {
            5: (200, 500),
            4: (100, 250),
            3: (60, 150),
            2: (30, 80)
        }
    
    def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        rooms: int = 1,
        min_rating: float = 3.0,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for hotels
        
        Args:
            destination: Destination city
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            guests: Number of guests
            rooms: Number of rooms needed
            min_rating: Minimum hotel rating
            max_results: Maximum number of results
            
        Returns:
            Dictionary with hotel options
        """
        try:
            logger.info(f"Searching hotels in {destination}")
            
            # Calculate nights
            check_in_date = datetime.fromisoformat(check_in)
            check_out_date = datetime.fromisoformat(check_out)
            nights = (check_out_date - check_in_date).days
            
            # Generate hotel options
            hotels = self._generate_hotels(
                destination, check_in, check_out, nights, 
                guests, rooms, min_rating, max_results
            )
            
            return {
                "success": True,
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights,
                "guests": guests,
                "rooms": rooms,
                "hotels": hotels
            }
            
        except Exception as e:
            logger.error(f"Hotel search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cheapest_hotel(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        min_rating: float = 3.0
    ) -> Dict[str, Any]:
        """Get the cheapest hotel option above minimum rating"""
        results = self.search_hotels(
            destination, check_in, check_out, 
            min_rating=min_rating, max_results=15
        )
        
        if not results["success"]:
            return results
        
        cheapest = min(results["hotels"], key=lambda x: x["price_per_night"])
        
        return {
            "success": True,
            "cheapest_hotel": cheapest,
            "total_cost": cheapest["total_cost"],
            "nights": results["nights"]
        }
    
    def get_best_rated_hotel(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        max_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get the best-rated hotel within budget"""
        results = self.search_hotels(destination, check_in, check_out, max_results=15)
        
        if not results["success"]:
            return results
        
        hotels = results["hotels"]
        
        # Filter by price if specified
        if max_price:
            hotels = [h for h in hotels if h["price_per_night"] <= max_price]
        
        if not hotels:
            return {
                "success": False,
                "error": "No hotels found within budget"
            }
        
        best = max(hotels, key=lambda x: x["rating"])
        
        return {
            "success": True,
            "best_hotel": best,
            "total_cost": best["total_cost"],
            "nights": results["nights"]
        }
    
    def _generate_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        nights: int,
        guests: int,
        rooms: int,
        min_rating: float,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate simulated hotel options"""
        hotels = []
        
        # Determine destination type for location variety
        locations = [
            f"Downtown {destination}",
            f"City Center {destination}",
            f"{destination} Old Town",
            f"{destination} Waterfront",
            f"Near {destination} Airport"
        ]
        
        amenities_pool = [
            "Free WiFi", "Breakfast Included", "Pool", "Gym",
            "Spa", "Restaurant", "Bar", "Room Service",
            "Free Parking", "Airport Shuttle", "Pet Friendly",
            "Business Center", "Concierge", "24-hour Front Desk"
        ]
        
        for i in range(count):
            # Random rating (weighted toward higher ratings)
            rating = random.choice([5, 5, 4, 4, 4, 3, 3, 2])
            
            # Skip if below minimum
            if rating < min_rating:
                continue
            
            # Generate price based on rating
            price_min, price_max = self.price_by_rating[rating]
            price_per_night = random.randint(price_min, price_max)
            
            # Apply room multiplier
            total_per_night = price_per_night * rooms
            total_cost = total_per_night * nights
            
            # Generate hotel name
            name = f"{random.choice(self.hotel_names)} {random.choice(self.hotel_types)}"
            
            # Random amenities (more for higher ratings)
            num_amenities = rating + random.randint(0, 3)
            amenities = random.sample(amenities_pool, min(num_amenities, len(amenities_pool)))
            
            # Distance from center (lower rating = farther)
            distance = round(random.uniform(0.5, 5.0) * (6 - rating) / 3, 1)
            
            hotels.append({
                "name": name,
                "rating": rating,
                "location": random.choice(locations),
                "distance_from_center": f"{distance} km",
                "price_per_night": price_per_night,
                "total_cost": total_cost,
                "currency": "USD",
                "rooms": rooms,
                "guests": guests,
                "amenities": amenities,
                "cancellation": "Free cancellation" if rating >= 4 else "Non-refundable",
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights
            })
        
        # Sort by rating descending, then price ascending
        hotels.sort(key=lambda x: (-x["rating"], x["price_per_night"]))
        return hotels[:count]
    
    def calculate_accommodation_cost(
        self,
        price_per_night: float,
        nights: int,
        rooms: int = 1
    ) -> Dict[str, Any]:
        """Calculate total accommodation cost"""
        total_per_night = price_per_night * rooms
        total_cost = total_per_night * nights
        
        return {
            "price_per_night": price_per_night,
            "nights": nights,
            "rooms": rooms,
            "total_per_night": total_per_night,
            "total_cost": total_cost,
            "currency": "USD"
        }


__all__ = ["HotelTool"]
