"""Exception classes for cnb_rates package."""

from typing import Optional, Tuple
from datetime import date as Date


class CnbRatesError(Exception):
    """Base exception for cnb_rates package."""
    pass


class DataFileError(CnbRatesError):
    """Raised when data file cannot be read or parsed."""
    pass


class CurrencyNotFoundError(CnbRatesError):
    """Raised when currency is not found in data."""
    
    def __init__(self, currency: str, date: str, available_currencies: Optional[list] = None):
        self.currency = currency
        self.date = date
        self.available_currencies = available_currencies
        
        msg = f"Currency '{currency}' not found in data for date '{date}'"
        if available_currencies:
            msg += f". Available currencies: {', '.join(sorted(available_currencies))}"
        
        super().__init__(msg)


class DateNotFoundError(CnbRatesError):
    """Raised when date is not found in data."""
    
    def __init__(self, date: str, available_range: Optional[Tuple[str, str]] = None):
        self.date = date
        self.available_range = available_range
        
        msg = f"No data available for date '{date}'"
        if available_range:
            msg += f". Available data range: {available_range[0]} to {available_range[1]}"
        
        super().__init__(msg)


class InvalidDateFormatError(CnbRatesError):
    """Raised when date format is invalid."""
    
    def __init__(self, date_input: str):
        self.date_input = date_input
        msg = (f"Invalid date format: '{date_input}'. "
               "Use 'DD.MM.YYYY', 'YYYY-MM-DD', or 'YYYY/MM/DD'")
        super().__init__(msg)


class InvalidDateTypeError(CnbRatesError):
    """Raised when date type is invalid."""
    
    def __init__(self, date_input):
        self.date_input = date_input
        msg = f"Date must be datetime.date or string, got {type(date_input).__name__}"
        super().__init__(msg)