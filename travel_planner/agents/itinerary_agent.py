"""
Itinerary Agent - Creates detailed day-by-day travel itineraries
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.utils.logger import logger


class ItineraryAgent(BaseAgent):
    """Agent specialized in creating detailed travel itineraries"""
    
    def __init__(self):
        super().__init__(
            name="Itinerary Agent",
            role="itinerary planning specialist",
            goal="create detailed, practical day-by-day itineraries optimized for time, interests, and energy"
        )
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute itinerary creation task
        
        Args:
            task: Itinerary task description
            context: Context with trip details, attractions, weather
            
        Returns:
            Complete day-by-day itinerary
        """
        try:
            if not context:
                return {"success": False, "error": "No context provided"}
            
            destination = context.get("destination")
            start_date = context.get("start_date")
            end_date = context.get("end_date")
            
            if not all([destination, start_date, end_date]):
                return {
                    "success": False,
                    "error": "Missing required information"
                }
            
            logger.info(f"Creating itinerary for {destination}")
            
            # Calculate days
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            num_days = (end - start).days + 1
            
            # Get additional context
            attractions = context.get("attractions", [])
            weather = context.get("weather_forecast", [])
            preferences = context.get("preferences", {})
            budget_per_day = context.get("budget_per_day", 100)
            
            # Create itinerary
            itinerary = self.create_daily_itinerary(
                destination=destination,
                start_date=start_date,
                num_days=num_days,
                attractions=attractions,
                weather=weather,
                preferences=preferences,
                budget_per_day=budget_per_day
            )
            
            return {
                "success": True,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "num_days": num_days,
                "itinerary": itinerary
            }
            
        except Exception as e:
            logger.error(f"Itinerary agent error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_daily_itinerary(
        self,
        destination: str,
        start_date: str,
        num_days: int,
        attractions: List[Any],
        weather: List[Any],
        preferences: Dict[str, Any],
        budget_per_day: float
    ) -> List[Dict[str, Any]]:
        """
        Create detailed day-by-day itinerary
        
        Args:
            destination: Destination name
            start_date: Start date
            num_days: Number of days
            attractions: List of attractions/activities
            weather: Weather forecast
            preferences: User preferences
            budget_per_day: Daily budget
            
        Returns:
            List of daily itinerary dictionaries
        """
        itinerary_days = []
        start = datetime.fromisoformat(start_date)
        
        # Generate AI-powered itinerary
        itinerary_prompt = f"""
        Create a detailed {num_days}-day itinerary for {destination}.
        
        Preferences: {preferences}
        Daily budget: ${budget_per_day}
        
        For EACH day (Day 1 through Day {num_days}), provide:
        
        Day X (Date):
        Morning (9 AM - 12 PM):
        - [Specific activity with location]
        - Duration: [time]
        - Cost: $[amount]
        
        Afternoon (12 PM - 5 PM):
        - [Specific activity with location]  
        - Duration: [time]
        - Cost: $[amount]
        
        Evening (5 PM - 9 PM):
        - [Specific activity with location]
        - Duration: [time]
        - Cost: $[amount]
        
        Day total: $[amount]
        
        Be specific with actual attractions, restaurants, and activities in {destination}.
        Include realistic times and costs.
        """
        
        try:
            detailed_plan = self.generate_response(itinerary_prompt)
            
            # Check if we got a real response (not an error)
            if detailed_plan and "Error:" not in detailed_plan and len(detailed_plan) > 100:
                # Parse into structured format
                for day_num in range(1, num_days + 1):
                    current_date = start + timedelta(days=day_num - 1)
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Get weather for this day if available
                    day_weather = None
                    if weather:
                        day_weather = next(
                            (w for w in weather if w.get("date") == date_str),
                            None
                        )
                    
                    itinerary_days.append({
                        "day": day_num,
                        "date": date_str,
                        "day_of_week": current_date.strftime("%A"),
                        "weather": day_weather,
                        "estimated_cost": budget_per_day,
                        "note": f"See detailed plan for Day {day_num}"
                    })
                
                return {
                    "days": itinerary_days,
                    "detailed_plan": detailed_plan
                }
            else:
                # AI failed, use fallback
                return self._create_fallback_itinerary(
                    destination, start_date, num_days, weather, budget_per_day, preferences
                )
        except Exception as e:
            logger.error(f"Itinerary generation error: {e}")
            return self._create_fallback_itinerary(
                destination, start_date, num_days, weather, budget_per_day, preferences
            )
    
    def _create_fallback_itinerary(
        self,
        destination: str,
        start_date: str,
        num_days: int,
        weather: List[Any],
        budget_per_day: float,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a basic itinerary when AI is unavailable"""
        
        itinerary_days = []
        start = datetime.fromisoformat(start_date)
        
        # Generic activities by day
        generic_activities = [
            {
                "title": "Arrival & Orientation",
                "morning": f"Arrive in {destination}, check into accommodation",
                "afternoon": "Explore the neighborhood, grab lunch at a local restaurant",
                "evening": "Settle in, light dinner, rest after travel"
            },
            {
                "title": "Main Attractions",
                "morning": f"Visit top attraction in {destination}",
                "afternoon": "Explore historic/cultural district",
                "evening": "Dinner at recommended restaurant"
            },
            {
                "title": "Local Experience",
                "morning": "Morning market or local neighborhood walk",
                "afternoon": "Museum or cultural site visit",
                "evening": "Try local specialty cuisine"
            },
            {
                "title": "Day Trip or Adventure",
                "morning": f"Day trip to nearby attraction from {destination}",
                "afternoon": "Continue exploring, lunch on location",
                "evening": "Return to city, relaxed dinner"
            },
            {
                "title": "Shopping & Leisure",
                "morning": "Shopping district or local markets",
                "afternoon": "Leisure time, café hopping",
                "evening": "Special dinner experience"
            },
            {
                "title": "Hidden Gems",
                "morning": "Off-the-beaten-path neighborhood",
                "afternoon": "Local experience or workshop",
                "evening": "Authentic local restaurant"
            },
            {
                "title": "Departure Day",
                "morning": "Last-minute souvenir shopping",
                "afternoon": "Pack and prepare for departure",
                "evening": "Departure or farewell dinner"
            }
        ]
        
        # Build detailed plan text
        detailed_plan = f"DETAILED ITINERARY FOR {destination.upper()}\n"
        detailed_plan += "="*60 + "\n\n"
        
        for day_num in range(1, num_days + 1):
            current_date = start + timedelta(days=day_num - 1)
            date_str = current_date.strftime("%Y-%m-%d")
            day_of_week = current_date.strftime("%A")
            
            # Get weather for this day
            day_weather = None
            if weather:
                day_weather = next(
                    (w for w in weather if w.get("date") == date_str),
                    {"temperature": "Check forecast", "condition": "Variable"}
                )
            
            # Select activity template
            activity_idx = min(day_num - 1, len(generic_activities) - 1)
            activity = generic_activities[activity_idx]
            
            # Build day entry
            detailed_plan += f"DAY {day_num} - {day_of_week}, {current_date.strftime('%B %d, %Y')}\n"
            detailed_plan += f"{activity['title']}\n"
            detailed_plan += "-"*60 + "\n"
            
            if day_weather:
                detailed_plan += f"Weather: {day_weather.get('condition', 'Variable')}, "
                detailed_plan += f"{day_weather.get('temperature', 'Check forecast')}\n\n"
            
            detailed_plan += f"MORNING (9:00 AM - 12:00 PM):\n"
            detailed_plan += f"  • {activity['morning']}\n"
            detailed_plan += f"  • Duration: ~3 hours\n"
            detailed_plan += f"  • Estimated cost: ${budget_per_day * 0.2:.0f}\n\n"
            
            detailed_plan += f"AFTERNOON (12:00 PM - 5:00 PM):\n"
            detailed_plan += f"  • {activity['afternoon']}\n"
            detailed_plan += f"  • Duration: ~4-5 hours\n"
            detailed_plan += f"  • Estimated cost: ${budget_per_day * 0.4:.0f}\n\n"
            
            detailed_plan += f"EVENING (5:00 PM - 9:00 PM):\n"
            detailed_plan += f"  • {activity['evening']}\n"
            detailed_plan += f"  • Duration: ~3-4 hours\n"
            detailed_plan += f"  • Estimated cost: ${budget_per_day * 0.4:.0f}\n\n"
            
            detailed_plan += f"Daily Budget: ${budget_per_day:.2f}\n"
            detailed_plan += "="*60 + "\n\n"
            
            # Add to itinerary days list
            itinerary_days.append({
                "day": day_num,
                "date": date_str,
                "day_of_week": day_of_week,
                "weather": day_weather,
                "activities": [
                    {"time": "Morning", "description": activity['morning'], "cost": budget_per_day * 0.2},
                    {"time": "Afternoon", "description": activity['afternoon'], "cost": budget_per_day * 0.4},
                    {"time": "Evening", "description": activity['evening'], "cost": budget_per_day * 0.4}
                ],
                "estimated_cost": budget_per_day
            })
        
        # Add travel tips
        interests = preferences.get("interests", [])
        interests_text = ", ".join(interests) if interests else "general sightseeing"
        
        detailed_plan += "\nTRAVEL TIPS:\n"
        detailed_plan += "-"*60 + "\n"
        detailed_plan += f"• This itinerary is optimized for {interests_text}\n"
        detailed_plan += f"• Budget approximately ${budget_per_day:.0f} per day for activities and meals\n"
        detailed_plan += "• Book popular attractions in advance\n"
        detailed_plan += "• Allow flexibility for spontaneous discoveries\n"
        detailed_plan += "• Stay hydrated and take breaks as needed\n"
        detailed_plan += f"• Research {destination}'s local customs and etiquette\n\n"
        
        detailed_plan += "Note: This is a template itinerary. Research specific attractions,\n"
        detailed_plan += f"restaurants, and activities in {destination} for your dates.\n"
        
        return {
            "days": itinerary_days,
            "detailed_plan": detailed_plan
        }
    
    def optimize_itinerary(
        self,
        itinerary: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize existing itinerary based on constraints
        
        Args:
            itinerary: Current itinerary
            constraints: New constraints or preferences
            
        Returns:
            Optimized itinerary
        """
        try:
            optimization_prompt = f"""
            Current itinerary:
            {itinerary}
            
            New constraints/feedback:
            {constraints}
            
            Optimize the itinerary considering:
            1. The new constraints
            2. Logical flow and efficiency
            3. Travel time and distances
            4. Energy management
            
            Provide the updated itinerary with explanations of changes.
            """
            
            optimized = self.generate_response(optimization_prompt)
            
            return {
                "success": True,
                "optimized_itinerary": optimized,
                "changes_made": "See optimized itinerary for details"
            }
            
        except Exception as e:
            logger.error(f"Itinerary optimization error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def suggest_alternatives(
        self,
        activity: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest alternative activities
        
        Args:
            activity: Original activity
            reason: Reason for change (e.g., "bad weather", "closed", "too expensive")
            context: Trip context
            
        Returns:
            Alternative suggestions
        """
        try:
            alternatives_prompt = f"""
            Original activity: {activity}
            Reason for change: {reason}
            
            Trip context:
            {context}
            
            Suggest 3-5 alternative activities that:
            1. Address the reason for change
            2. Fit the same time slot
            3. Match the trip's overall theme
            4. Are practical and accessible
            
            For each alternative, provide:
            - Activity name and description
            - Why it's a good substitute
            - Estimated duration and cost
            """
            
            alternatives = self.generate_response(alternatives_prompt)
            
            return {
                "success": True,
                "original_activity": activity,
                "reason": reason,
                "alternatives": alternatives
            }
            
        except Exception as e:
            logger.error(f"Alternative suggestion error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["ItineraryAgent"]
