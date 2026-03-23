"""
Coordinator Agent - Orchestrates all agents to plan complete trips
"""

from typing import Dict, Any, Optional
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.agents.research_agent import ResearchAgent
from travel_planner.agents.weather_agent import WeatherAgent
from travel_planner.agents.flight_agent import FlightAgent
from travel_planner.agents.hotel_agent import HotelAgent
from travel_planner.agents.budget_agent import BudgetAgent
from travel_planner.agents.itinerary_agent import ItineraryAgent
from travel_planner.utils.logger import logger
from travel_planner.utils.validators import (
    validate_destination, validate_date_range,
    validate_budget, validate_travelers
)


class CoordinatorAgent(BaseAgent):
    """
    Main coordinator agent that orchestrates all specialized agents
    to create complete travel plans
    """
    
    def __init__(self):
        super().__init__(
            name="Travel Coordinator",
            role="travel planning coordinator",
            goal="orchestrate all agents to create comprehensive, personalized travel itineraries"
        )
        
        # Initialize all specialized agents
        logger.info("Initializing specialized agents...")
        self.research_agent = ResearchAgent()
        self.weather_agent = WeatherAgent()
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.budget_agent = BudgetAgent()
        self.itinerary_agent = ItineraryAgent()
        
        logger.info("All agents initialized successfully")
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute coordinated travel planning
        
        Args:
            task: Planning task description
            context: Trip parameters
            
        Returns:
            Complete travel plan
        """
        try:
            return self.plan_trip(
                destination=context.get("destination"),
                start_date=context.get("start_date"),
                end_date=context.get("end_date"),
                budget=context.get("budget"),
                travelers=context.get("travelers", 1),
                origin=context.get("origin", "New York, USA"),
                preferences=context.get("preferences", {})
            )
        except Exception as e:
            logger.error(f"Coordinator error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def plan_trip(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: float,
        travelers: int = 1,
        origin: str = "New York, USA",
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete travel plan
        
        Args:
            destination: Destination city/country
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            budget: Total budget in USD
            travelers: Number of travelers
            origin: Origin city for flights
            preferences: User preferences (interests, pace, etc.)
            
        Returns:
            Complete travel plan with all details
        """
        try:
            logger.info(f"=== Planning trip to {destination} ===")
            
            # Validate inputs
            validation_errors = self._validate_inputs(
                destination, start_date, end_date, budget, travelers
            )
            if validation_errors:
                return {
                    "success": False,
                    "errors": validation_errors
                }
            
            preferences = preferences or {}
            
            # Build context for all agents
            context = {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "travelers": travelers,
                "origin": origin,
                "preferences": preferences
            }
            
            # Calculate trip duration
            from datetime import datetime
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            duration_days = (end - start).days
            
            context["duration_days"] = duration_days
            
            # Step 1: Research destination
            logger.info("Step 1/6: Researching destination...")
            research_results = self.research_agent.execute(
                f"Research {destination} for travel planning",
                context
            )
            
            # Step 2: Get weather forecast
            logger.info("Step 2/6: Getting weather forecast...")
            weather_results = self.weather_agent.execute(
                f"Get weather for {destination}",
                context
            )
            
            # Step 3: Search flights
            logger.info("Step 3/6: Searching flights...")
            flight_results = self.flight_agent.execute(
                f"Find flights to {destination}",
                context
            )
            
            # Update context with flight cost
            if flight_results.get("success"):
                context["flight_cost"] = flight_results.get("estimated_cost", 0)
            else:
                context["flight_cost"] = budget * 0.4  # Estimate 40% for flights
            
            # Step 4: Search hotels
            logger.info("Step 4/6: Searching accommodations...")
            hotel_results = self.hotel_agent.execute(
                f"Find hotels in {destination}",
                context
            )
            
            # Update context with hotel cost
            if hotel_results.get("success"):
                context["hotel_cost"] = hotel_results.get("estimated_cost", 0)
            else:
                context["hotel_cost"] = budget * 0.3  # Estimate 30% for hotels
            
            # Step 5: Budget analysis
            logger.info("Step 5/6: Analyzing budget...")
            budget_results = self.budget_agent.execute(
                "Analyze trip budget",
                context
            )
            
            # Calculate per-day budget for activities
            remaining_budget = budget - context["flight_cost"] - context["hotel_cost"]
            context["budget_per_day"] = remaining_budget / duration_days if duration_days > 0 else 0
            
            # Add research and weather to context for itinerary
            context["attractions"] = research_results.get("attractions", [])
            context["weather_forecast"] = weather_results.get("forecast", [])
            
            # Step 6: Create itinerary
            logger.info("Step 6/6: Creating detailed itinerary...")
            itinerary_results = self.itinerary_agent.execute(
                f"Create itinerary for {destination}",
                context
            )
            
            # Compile complete travel plan
            travel_plan = {
                "success": True,
                "trip_summary": {
                    "destination": destination,
                    "origin": origin,
                    "dates": {
                        "start": start_date,
                        "end": end_date,
                        "duration_days": duration_days
                    },
                    "travelers": travelers,
                    "total_budget": budget
                },
                "research": research_results,
                "weather": weather_results,
                "flights": flight_results,
                "accommodation": hotel_results,
                "budget_analysis": budget_results,
                "itinerary": itinerary_results,
                "recommendations": self._generate_final_recommendations(
                    context, research_results, weather_results,
                    flight_results, hotel_results, budget_results
                )
            }
            
            logger.info("=== Trip planning completed successfully! ===")
            return travel_plan
            
        except Exception as e:
            logger.error(f"Trip planning failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create complete travel plan"
            }
    
    def _validate_inputs(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: float,
        travelers: int
    ) -> list:
        """Validate all inputs"""
        errors = []
        
        valid, msg = validate_destination(destination)
        if not valid:
            errors.append(f"Destination: {msg}")
        
        valid, msg = validate_date_range(start_date, end_date)
        if not valid:
            errors.append(f"Dates: {msg}")
        
        valid, msg = validate_budget(budget)
        if not valid:
            errors.append(f"Budget: {msg}")
        
        valid, msg = validate_travelers(travelers)
        if not valid:
            errors.append(f"Travelers: {msg}")
        
        return errors
    
    def _generate_final_recommendations(
        self,
        context: Dict[str, Any],
        research: Dict[str, Any],
        weather: Dict[str, Any],
        flights: Dict[str, Any],
        hotels: Dict[str, Any],
        budget: Dict[str, Any]
    ) -> str:
        """Generate final recommendations and tips"""
        
        recommendation_prompt = f"""
        Based on the complete travel plan for {context['destination']}:
        
        Budget Status: {budget.get('status', {}).get('message', 'N/A')}
        Weather: {weather.get('recommendations', 'Check forecast')}
        Available Budget per Day: ${context.get('budget_per_day', 0):.2f}
        
        Provide final recommendations:
        1. Top 3 things to prioritize during this trip
        2. Money-saving tips specific to this destination
        3. Important things to book in advance
        4. Safety and practical travel tips
        5. Best way to get around locally
        
        Be specific and actionable.
        """
        
        return self.generate_response(recommendation_prompt)
    
    def modify_trip(
        self,
        current_plan: Dict[str, Any],
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modify an existing trip plan
        
        Args:
            current_plan: Current travel plan
            modifications: Requested modifications
            
        Returns:
            Updated travel plan
        """
        try:
            logger.info("Modifying existing trip plan...")
            
            # Update context with modifications
            context = current_plan.get("trip_summary", {}).copy()
            context.update(modifications)
            
            # Re-run affected agents based on modifications
            if "budget" in modifications or "travelers" in modifications:
                # Re-analyze budget
                budget_results = self.budget_agent.execute("Re-analyze budget", context)
                current_plan["budget_analysis"] = budget_results
            
            if "start_date" in modifications or "end_date" in modifications:
                # Update weather and itinerary
                weather_results = self.weather_agent.execute("Update weather", context)
                current_plan["weather"] = weather_results
                
                itinerary_results = self.itinerary_agent.execute("Update itinerary", context)
                current_plan["itinerary"] = itinerary_results
            
            current_plan["trip_summary"].update(modifications)
            current_plan["last_modified"] = datetime.now().isoformat()
            
            logger.info("Trip modifications completed")
            return current_plan
            
        except Exception as e:
            logger.error(f"Modification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["CoordinatorAgent"]
