"""Utility functions for cnb_rates package."""

from datetime import date as Date, datetime
from typing import Union

from .exceptions import InvalidDateFormatError, InvalidDateTypeError


def parse_date(date_input: Union[Date, str]) -> str:
    """Convert date input to DD.MM.YYYY format used in CSV files.
    
    Args:
        date_input: Date as datetime.date, 'DD.MM.YYYY', 'YYYY-MM-DD', or 'YYYY/MM/DD'
        
    Returns:
        Date string in DD.MM.YYYY format
        
    Raises:
        InvalidDateFormatError: If date format is invalid
        InvalidDateTypeError: If date type is invalid
    """
    if isinstance(date_input, Date):
        return date_input.strftime("%d.%m.%Y")
    elif isinstance(date_input, str):
        date_str = date_input.strip()
        
        # Handle DD.MM.YYYY format
        if "." in date_str and len(date_str.split(".")) == 3:
            parts = date_str.split(".")
            if len(parts[0]) <= 2 and len(parts[1]) <= 2 and len(parts[2]) == 4:
                try:
                    # Validate the date is actually valid
                    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                    datetime(year, month, day)  # This will raise ValueError if invalid
                    return f"{day:02d}.{month:02d}.{year}"
                except ValueError:
                    raise InvalidDateFormatError(date_input)
        
        # Handle YYYY-MM-DD format
        elif "-" in date_str and len(date_str.split("-")) == 3:
            parts = date_str.split("-")
            if len(parts[0]) == 4 and len(parts[1]) <= 2 and len(parts[2]) <= 2:
                try:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    datetime(year, month, day)  # Validate
                    return f"{day:02d}.{month:02d}.{year}"
                except ValueError:
                    raise InvalidDateFormatError(date_input)
        
        # Handle YYYY/MM/DD format
        elif "/" in date_str and len(date_str.split("/")) == 3:
            parts = date_str.split("/")
            if len(parts[0]) == 4 and len(parts[1]) <= 2 and len(parts[2]) <= 2:
                try:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    datetime(year, month, day)  # Validate
                    return f"{day:02d}.{month:02d}.{year}"
                except ValueError:
                    raise InvalidDateFormatError(date_input)
        
        raise InvalidDateFormatError(date_input)
    else:
        raise InvalidDateTypeError(date_input)


def parse_rate_value(value: str) -> float:
    """Parse rate value from CSV (handles comma decimal separator).
    
    Args:
        value: Rate value as string with comma decimal separator
        
    Returns:
        Rate value as float
        
    Raises:
        ValueError: If value cannot be parsed as float
    """
    if not value or not value.strip():
        raise ValueError("Empty rate value")
        
    try:
        # Handle comma decimal separator
        normalized_value = value.strip().replace(",", ".")
        return float(normalized_value)
    except ValueError:
        raise ValueError(f"Invalid rate value: {value}")


def format_currency_rate(currency: str, date: str, amount: Union[int, float], 
                        czk_value: float, precision: int = 3) -> str:
    """Format currency exchange rate for display.
    
    Args:
        currency: Currency code
        date: Date string
        amount: Amount of currency
        czk_value: CZK value
        precision: Decimal places for rate display
        
    Returns:
        Formatted string
    """
    if amount == 1:
        return f"1 {currency} = {czk_value:.{precision}f} CZK on {date}"
    else:
        if amount == int(amount):
            amount_str = str(int(amount))
        else:
            amount_str = f"{amount:.2f}".rstrip('0').rstrip('.')
        
        return f"{amount_str} {currency} = {czk_value:.2f} CZK on {date}"