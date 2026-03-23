"""
Weather Agent - Provides weather forecasts and recommendations
"""

from typing import Dict, Any, Optional
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.tools.weather_tool import WeatherTool
from travel_planner.utils.logger import logger


class WeatherAgent(BaseAgent):
    """Agent specialized in weather information and recommendations"""
    
    def __init__(self):
        super().__init__(
            name="Weather Agent",
            role="weather information specialist",
            goal="provide accurate weather forecasts and packing/planning recommendations"
        )
        self.weather_tool = WeatherTool()
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute weather-related task
        
        Args:
            task: Weather task description
            context: Context with destination and dates
            
        Returns:
            Weather information and recommendations
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
                    "error": "Missing required information: destination, start_date, end_date"
                }
            
            logger.info(f"Getting weather for {destination} ({start_date} to {end_date})")
            
            # Get weather forecast
            weather_data = self.weather_tool.get_weather_for_dates(
                destination, start_date, end_date
            )
            
            if not weather_data["success"]:
                return weather_data
            
            # Generate recommendations based on weather
            weather_prompt = f"""
            Based on this weather forecast for {destination}:
            {weather_data['forecasts']}
            
            Provide:
            1. Overall weather summary for the trip
            2. What to pack (clothing and accessories)
            3. Any weather-related activity recommendations or warnings
            4. Best days for outdoor activities
            
            Be practical and specific.
            """
            
            recommendations = self.generate_response(weather_prompt, context)
            
            return {
                "success": True,
                "destination": destination,
                "date_range": f"{start_date} to {end_date}",
                "forecast": weather_data["forecasts"],
                "recommendations": recommendations,
                "note": weather_data.get("note")
            }
            
        except Exception as e:
            logger.error(f"Weather agent error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_daily_forecast(self, destination: str, date: str) -> Dict[str, Any]:
        """
        Get weather forecast for a specific day
        
        Args:
            destination: Destination name
            date: Date (YYYY-MM-DD)
            
        Returns:
            Daily weather forecast
        """
        try:
            weather_data = self.weather_tool.get_weather_for_dates(destination, date, date)
            
            if weather_data["success"] and weather_data["forecasts"]:
                return {
                    "success": True,
                    "destination": destination,
                    "date": date,
                    "forecast": weather_data["forecasts"][0]
                }
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Daily forecast error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def recommend_activities_by_weather(
        self,
        destination: str,
        date: str,
        planned_activities: list
    ) -> Dict[str, Any]:
        """
        Recommend whether planned activities are suitable for weather
        
        Args:
            destination: Destination name
            date: Date to check
            planned_activities: List of planned activities
            
        Returns:
            Weather suitability assessment
        """
        try:
            forecast = self.get_daily_forecast(destination, date)
            
            if not forecast["success"]:
                return forecast
            
            activities_str = "\n".join(f"- {act}" for act in planned_activities)
            
            assessment_prompt = f"""
            Weather forecast for {destination} on {date}:
            {forecast['forecast']}
            
            Planned activities:
            {activities_str}
            
            For each activity, assess:
            1. Is it suitable for this weather?
            2. Any precautions needed?
            3. Alternative suggestions if weather is unsuitable
            
            Be specific and practical.
            """
            
            assessment = self.generate_response(assessment_prompt)
            
            return {
                "success": True,
                "destination": destination,
                "date": date,
                "weather": forecast["forecast"],
                "planned_activities": planned_activities,
                "assessment": assessment
            }
            
        except Exception as e:
            logger.error(f"Activity assessment error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["WeatherAgent"]
