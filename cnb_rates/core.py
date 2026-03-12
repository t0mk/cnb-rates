"""Core exchange rate functions for Czech National Bank data.

This module provides the main public API for the cnb_rates package.
All functionality has been moved to specialized modules but is re-exported
here for backward compatibility.
"""

# Import all functions from the rates module
from .rates import rate1, rate, years, currencies, RateSession

# Import exceptions for backward compatibility
from .exceptions import (
    CnbRatesError,
    CurrencyNotFoundError, 
    DateNotFoundError,
    DataFileError,
    InvalidDateFormatError,
    InvalidDateTypeError
)

# Import currency definitions
from .currency import Currency, get_all_currency_codes, is_valid_currency, normalize_currency

# Import utility functions
from .utils import parse_date, parse_rate_value, format_currency_rate

# Import data management functions
from .data import get_data_index, invalidate_cache

__all__ = [
    # Main API functions
    "rate1", "rate", "years", "currencies", "RateSession",
    
    # Exceptions
    "CnbRatesError", "CurrencyNotFoundError", "DateNotFoundError", "DataFileError",
    "InvalidDateFormatError", "InvalidDateTypeError",
    
    # Currency utilities
    "Currency", "get_all_currency_codes", "is_valid_currency", "normalize_currency",
    
    # Utilities
    "parse_date", "parse_rate_value", "format_currency_rate",
    
    # Data management
    "get_data_index", "invalidate_cache"
]