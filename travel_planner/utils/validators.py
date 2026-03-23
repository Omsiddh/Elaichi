"""
Input validation utilities
"""

from typing import Optional, Tuple
from datetime import datetime, date, timedelta
import re


def validate_date(date_str: str) -> Tuple[bool, Optional[datetime], str]:
    """
    Validate date string
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, parsed_date, error_message)
    """
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Check if date is not in the past
        if parsed_date.date() < date.today():
            return False, None, "Date cannot be in the past"
        
        # Check if date is not too far in future (2 years)
        max_future = date.today() + timedelta(days=730)
        if parsed_date.date() > max_future:
            return False, None, "Date cannot be more than 2 years in the future"
        
        return True, parsed_date, ""
        
    except ValueError:
        return False, None, "Invalid date format. Use YYYY-MM-DD"


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Validate date range
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_start, parsed_start, error_start = validate_date(start_date)
    if not valid_start:
        return False, f"Start date error: {error_start}"
    
    valid_end, parsed_end, error_end = validate_date(end_date)
    if not valid_end:
        return False, f"End date error: {error_end}"
    
    if parsed_start >= parsed_end:
        return False, "End date must be after start date"
    
    # Check if trip is not too long (30 days max)
    if (parsed_end - parsed_start).days > 30:
        return False, "Trip duration cannot exceed 30 days"
    
    return True, ""


def validate_budget(budget: float) -> Tuple[bool, str]:
    """
    Validate budget amount
    
    Args:
        budget: Budget amount
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if budget <= 0:
        return False, "Budget must be positive"
    
    if budget < 100:
        return False, "Budget seems too low (minimum $100)"
    
    if budget > 1000000:
        return False, "Budget seems unrealistic (maximum $1,000,000)"
    
    return True, ""


def validate_travelers(count: int) -> Tuple[bool, str]:
    """
    Validate number of travelers
    
    Args:
        count: Number of travelers
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if count <= 0:
        return False, "Number of travelers must be positive"
    
    if count > 20:
        return False, "Maximum 20 travelers supported"
    
    return True, ""


def validate_destination(destination: str) -> Tuple[bool, str]:
    """
    Validate destination string
    
    Args:
        destination: Destination string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not destination or len(destination.strip()) < 2:
        return False, "Destination must be at least 2 characters"
    
    if len(destination) > 100:
        return False, "Destination name too long (maximum 100 characters)"
    
    # Check for valid characters (letters, spaces, commas, hyphens)
    if not re.match(r'^[a-zA-Z\s,\-\.]+$', destination):
        return False, "Destination contains invalid characters"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address
    
    Args:
        email: Email string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    return False, "Invalid email format"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text


__all__ = [
    "validate_date",
    "validate_date_range",
    "validate_budget",
    "validate_travelers",
    "validate_destination",
    "validate_email",
    "sanitize_input"
]
