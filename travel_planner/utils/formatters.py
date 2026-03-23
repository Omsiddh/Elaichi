"""
Formatting utilities for travel planner output
"""

from typing import Dict, List, Any
from datetime import datetime, date
import json


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "INR": "₹"
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_date(date_obj: Any) -> str:
    """Format date object to readable string"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, (datetime, date)):
        return date_obj.strftime("%B %d, %Y")
    
    return str(date_obj)


def format_time(time_str: str) -> str:
    """Format time string (HH:MM) to readable format"""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except ValueError:
        return time_str


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes}m"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def format_weather(weather_data: Dict[str, Any]) -> str:
    """Format weather data to readable string"""
    temp = weather_data.get('temperature', 'N/A')
    condition = weather_data.get('condition', 'Unknown')
    
    return f"{condition}, {temp}"


def format_itinerary_day(day_data: Dict[str, Any]) -> str:
    """Format a single day's itinerary for display"""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Day {day_data['day']} - {format_date(day_data['date'])}")
    lines.append(f"{'='*60}")
    
    if 'weather' in day_data:
        lines.append(f"Weather: {format_weather(day_data['weather'])}")
        lines.append("")
    
    for activity in day_data.get('activities', []):
        time = format_time(activity.get('time', ''))
        name = activity.get('activity', 'Activity')
        location = activity.get('location', '')
        duration = activity.get('duration', '')
        cost = activity.get('cost', 0)
        
        lines.append(f"  {time} - {name}")
        if location:
            lines.append(f"           Location: {location}")
        if duration:
            lines.append(f"           Duration: {duration}")
        if cost > 0:
            lines.append(f"           Cost: {format_currency(cost)}")
        lines.append("")
    
    return "\n".join(lines)


def format_budget_summary(budget: Dict[str, Any]) -> str:
    """Format budget breakdown for display"""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append("BUDGET SUMMARY")
    lines.append(f"{'='*60}")
    
    total = budget.get('total', 0)
    currency = budget.get('currency', 'USD')
    breakdown = budget.get('breakdown', {})
    
    lines.append(f"\nTotal Budget: {format_currency(total, currency)}")
    lines.append("\nBreakdown:")
    
    for category, amount in breakdown.items():
        lines.append(f"  {category.title():<20} {format_currency(amount, currency):>12}")
    
    return "\n".join(lines)


def format_flight_option(flight: Dict[str, Any]) -> str:
    """Format flight option for display"""
    airline = flight.get('airline', 'Unknown')
    departure = flight.get('departure_time', '')
    arrival = flight.get('arrival_time', '')
    duration = flight.get('duration', '')
    price = flight.get('price', 0)
    stops = flight.get('stops', 0)
    
    stops_text = "Direct" if stops == 0 else f"{stops} stop(s)"
    
    return (
        f"  {airline}\n"
        f"  {departure} → {arrival} ({duration})\n"
        f"  {stops_text} - {format_currency(price)}"
    )


def format_hotel_option(hotel: Dict[str, Any]) -> str:
    """Format hotel option for display"""
    name = hotel.get('name', 'Unknown Hotel')
    rating = hotel.get('rating', 0)
    price_per_night = hotel.get('price_per_night', 0)
    location = hotel.get('location', '')
    
    stars = "⭐" * int(rating) if rating > 0 else ""
    
    return (
        f"  {name} {stars}\n"
        f"  {location}\n"
        f"  {format_currency(price_per_night)} per night"
    )


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def pretty_print_json(data: Dict[str, Any]) -> str:
    """Pretty print JSON data"""
    return json.dumps(data, indent=2, ensure_ascii=False)


__all__ = [
    "format_currency",
    "format_date",
    "format_time",
    "format_duration",
    "format_weather",
    "format_itinerary_day",
    "format_budget_summary",
    "format_flight_option",
    "format_hotel_option",
    "truncate_text",
    "pretty_print_json"
]
