"""Czech National Bank Exchange Rates Package

Provides exchange rates from Czech National Bank data.

Usage:
    import cnb_rates
    rate_czk = cnb_rates.rate1(cnb_rates.USD, "14.01.2025")
    total_czk = cnb_rates.rate(cnb_rates.EUR, "2025-01-14", 100)

Advanced usage with caching:
    with cnb_rates.RateSession() as session:
        rates = [session.get_rate('USD', date) for date in date_list]
"""

from .rates import rate1, rate, years, currencies, RateSession
from .currency import Currency
from .exceptions import (
    CnbRatesError, CurrencyNotFoundError, DateNotFoundError, DataFileError
)

# Import currency constants for backward compatibility
from .currency import (
    AUD, BGN, BRL, CAD, CHF, CNY, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, 
    ISK, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PLN, RON, SEK, SGD, THB, TRY, 
    USD, XDR, ZAR, ATS, BEF, CYP, DEM, EEK, ESP, FIM, FRF, GRD, IEP, ITL,
    LTL, LUF, LVL, MTL, NLG, PTE, ROL, RUB, SIT, SKK, TRL, XCU, XEU
)

# Version information
__version__ = "0.2.0"
__author__ = "cnb_rates contributors"

__all__ = [
    # Core functions
    "rate1", "rate", "years", "currencies", "RateSession",
    
    # Types
    "Currency",
    
    # Exceptions
    "CnbRatesError", "CurrencyNotFoundError", "DateNotFoundError", "DataFileError",
    
    # Currency constants (major currencies)
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "HKD",
    "BGN", "DKK", "HUF", "NOK", "PLN", "RON", "SEK", "IDR", "ILS", "INR", 
    "ISK", "KRW", "MYR", "PHP", "SGD", "THB", "TRY", "BRL", "MXN", "NZD", 
    "ZAR", "XDR",
    
    # Historical currencies
    "ATS", "BEF", "CYP", "DEM", "EEK", "ESP", "FIM", "FRF", "GRD", "IEP",
    "ITL", "LTL", "LUF", "LVL", "MTL", "NLG", "PTE", "ROL", "RUB", "SIT",
    "SKK", "TRL", "XCU", "XEU"
]