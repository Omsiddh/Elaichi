"""
Weather tool for fetching weather forecasts
Uses OpenWeatherMap API
"""

from typing import Dict, Any, Optional
import requests
from datetime import datetime, timedelta
from config import get_settings
from travel_planner.utils.logger import logger


class WeatherTool:
    """Tool for fetching weather data"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openweather_api_key
        self.base_url = self.settings.openweather_base_url
        
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for a location
        
        Args:
            location: City name or "City, Country"
            
        Returns:
            Dictionary with weather data
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "location": location,
                "temperature": f"{data['main']['temp']}°C",
                "feels_like": f"{data['main']['feels_like']}°C",
                "condition": data['weather'][0]['description'].title(),
                "humidity": f"{data['main']['humidity']}%",
                "wind_speed": f"{data['wind']['speed']} m/s",
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "location": location
            }
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """
        Get weather forecast for upcoming days
        
        Args:
            location: City name or "City, Country"
            days: Number of days to forecast (max 5 for free tier)
            
        Returns:
            Dictionary with forecast data
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40)  # 8 forecasts per day, max 40
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Group by day
            daily_forecasts = {}
            for item in data['list']:
                dt = datetime.fromtimestamp(item['dt'])
                date_key = dt.date().isoformat()
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        "date": date_key,
                        "temps": [],
                        "conditions": [],
                        "precipitation": []
                    }
                
                daily_forecasts[date_key]["temps"].append(item['main']['temp'])
                daily_forecasts[date_key]["conditions"].append(item['weather'][0]['description'])
                
                # Check for precipitation
                if 'rain' in item:
                    daily_forecasts[date_key]["precipitation"].append(item['rain'].get('3h', 0))
                elif 'snow' in item:
                    daily_forecasts[date_key]["precipitation"].append(item['snow'].get('3h', 0))
            
            # Summarize each day
            forecasts = []
            for date_key, day_data in sorted(daily_forecasts.items())[:days]:
                avg_temp = sum(day_data['temps']) / len(day_data['temps'])
                max_temp = max(day_data['temps'])
                min_temp = min(day_data['temps'])
                
                # Most common condition
                condition = max(set(day_data['conditions']), key=day_data['conditions'].count)
                
                # Precipitation probability
                has_precip = len(day_data['precipitation']) > 0
                precip_prob = "High" if has_precip else "Low"
                
                forecasts.append({
                    "date": date_key,
                    "temperature": f"{avg_temp:.1f}°C",
                    "temp_range": f"{min_temp:.1f}°C - {max_temp:.1f}°C",
                    "condition": condition.title(),
                    "precipitation": precip_prob
                })
            
            return {
                "success": True,
                "location": location,
                "forecasts": forecasts
            }
            
        except requests.RequestException as e:
            logger.error(f"Weather forecast API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "location": location
            }
    
    def get_weather_for_dates(
        self, 
        location: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get weather forecast for specific date range
        
        Args:
            location: City name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with weather data for the date range
        """
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        days = (end - start).days + 1
        
        # Check if dates are within forecast range (5 days)
        days_from_now = (start - datetime.now()).days
        
        if days_from_now > 5:
            # Beyond forecast range, provide seasonal averages
            return {
                "success": True,
                "location": location,
                "note": "Dates beyond forecast range, providing seasonal averages",
                "forecasts": self._get_seasonal_data(location, start, days)
            }
        
        # Within forecast range
        forecast_data = self.get_forecast(location, days)
        
        if forecast_data["success"]:
            # Filter forecasts for requested dates
            requested_dates = set()
            current = start
            while current <= end:
                requested_dates.add(current.date().isoformat())
                current += timedelta(days=1)
            
            filtered_forecasts = [
                f for f in forecast_data["forecasts"]
                if f["date"] in requested_dates
            ]
            
            forecast_data["forecasts"] = filtered_forecasts
        
        return forecast_data
    
    def _get_seasonal_data(
        self, 
        location: str, 
        start_date: datetime, 
        days: int
    ) -> list:
        """Get seasonal average weather data (fallback for distant dates)"""
        # Simplified seasonal data - in production, use historical averages
        month = start_date.month
        
        # Rough seasonal estimates
        seasonal_temps = {
            "winter": {"avg": 5, "range": "0-10"},
            "spring": {"avg": 15, "range": "10-20"},
            "summer": {"avg": 25, "range": "20-30"},
            "autumn": {"avg": 15, "range": "10-20"}
        }
        
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "autumn"
        
        temp_data = seasonal_temps[season]
        
        forecasts = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).date().isoformat()
            forecasts.append({
                "date": date,
                "temperature": f"~{temp_data['avg']}°C",
                "temp_range": f"{temp_data['range']}°C",
                "condition": f"Typical {season} weather",
                "precipitation": "Variable",
                "note": "Seasonal average"
            })
        
        return forecasts


__all__ = ["WeatherTool"]
