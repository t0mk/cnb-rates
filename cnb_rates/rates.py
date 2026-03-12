"""Exchange rate calculation functions for cnb_rates package."""

from datetime import datetime, date as Date
from typing import Union, List

from .data import get_data_index
from .utils import parse_date, parse_rate_value
from .exceptions import CurrencyNotFoundError, DateNotFoundError


def rate1(currency: str, date_input: Union[Date, str]) -> float:
    """Get CZK value of 1 unit of the specified currency on given date.
    
    If the exact date is not available (e.g., weekends), uses the most recent previous date.
    
    Args:
        currency: Currency code (e.g., 'USD', 'EUR', 'HUF')
        date_input: Date as datetime.date, 'DD.MM.YYYY', 'YYYY-MM-DD', or 'YYYY/MM/DD'
        
    Returns:
        CZK value of 1 unit of currency
        
    Raises:
        CurrencyNotFoundError: If currency is not supported
        DateNotFoundError: If no data available for date or any previous date
    """
    # Parse and validate date
    date_str = parse_date(date_input)
    target_dt = datetime.strptime(date_str, "%d.%m.%Y")
    
    # Get cached data index
    data_index = get_data_index()
    
    # Find the best matching date using binary search
    date_info = data_index.find_date(target_dt)
    if date_info is None:
        raise DateNotFoundError(date_str, data_index.date_range)
    
    # Check if currency is available for this date
    currency_upper = currency.upper()
    if currency_upper not in date_info.currencies:
        available_currencies = sorted(date_info.currencies.keys())
        raise CurrencyNotFoundError(currency_upper, date_info.date_str, available_currencies)
    
    # Get rate data
    col_index = date_info.currencies[currency_upper]
    rate_value = date_info.row[col_index]
    
    # Get denomination from header (e.g., "100 HUF" means rate is per 100 units)
    header_col = date_info.header[col_index]
    denomination_str = header_col.split()[0]  # "1", "100", "1000"
    denomination = int(denomination_str)
    
    # Parse and convert rate to per-1-unit basis
    parsed_rate = parse_rate_value(rate_value)
    return parsed_rate / denomination


def rate(currency: str, date_input: Union[Date, str], amount: float) -> float:
    """Get CZK value of specified amount of currency on given date.
    
    Args:
        currency: Currency code (e.g., 'USD', 'EUR', 'HUF')
        date_input: Date as datetime.date, 'DD.MM.YYYY', 'YYYY-MM-DD', or 'YYYY/MM/DD'
        amount: Amount of currency to convert
        
    Returns:
        CZK value of the specified amount
        
    Raises:
        CurrencyNotFoundError: If currency is not supported
        DateNotFoundError: If date is not found in data
    """
    unit_rate = rate1(currency, date_input)
    return unit_rate * amount


def years() -> List[str]:
    """Get list of available data years.
    
    Returns:
        List of year strings for which data is available
    """
    data_index = get_data_index()
    return data_index.get_years()


def currencies() -> List[str]:
    """Get list of available currency codes.
    
    Returns:
        List of currency codes supported by the data
    """
    data_index = get_data_index()
    return data_index.all_currencies


class RateSession:
    """Context manager for batch exchange rate operations with cached data."""
    
    def __init__(self):
        self._data_index = None
    
    def __enter__(self):
        # Pre-load data index
        self._data_index = get_data_index()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed
        pass
    
    def get_rate(self, currency: str, date_input: Union[Date, str], amount: float = 1.0) -> float:
        """Get exchange rate using cached data.
        
        Args:
            currency: Currency code
            date_input: Date in any supported format
            amount: Amount to convert (default: 1.0)
            
        Returns:
            CZK value of the specified amount
        """
        if amount == 1.0:
            return rate1(currency, date_input)
        else:
            return rate(currency, date_input, amount)
    
    def get_rates(self, currency: str, dates: List[Union[Date, str]], 
                  amount: float = 1.0) -> List[float]:
        """Get exchange rates for multiple dates efficiently.
        
        Args:
            currency: Currency code
            dates: List of dates in any supported format
            amount: Amount to convert (default: 1.0)
            
        Returns:
            List of CZK values
        """
        return [self.get_rate(currency, date, amount) for date in dates]