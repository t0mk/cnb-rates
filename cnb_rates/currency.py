"""Currency definitions and validation for cnb_rates package."""

from enum import Enum
from typing import Set, List


class Currency(Enum):
    """Enumeration of supported currencies."""
    
    # Major currencies
    USD = "USD"
    EUR = "EUR" 
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    
    # European currencies
    BGN = "BGN"
    DKK = "DKK"
    HUF = "HUF"
    NOK = "NOK"
    PLN = "PLN"
    RON = "RON"
    SEK = "SEK"
    
    # Asian currencies
    CNY = "CNY"
    HKD = "HKD"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    ISK = "ISK"
    KRW = "KRW"
    MYR = "MYR"
    PHP = "PHP"
    SGD = "SGD"
    THB = "THB"
    TRY = "TRY"
    
    # Other currencies
    BRL = "BRL"
    MXN = "MXN"
    NZD = "NZD"
    ZAR = "ZAR"
    XDR = "XDR"  # Special Drawing Rights
    
    # Historical currencies (may not be in current data)
    ATS = "ATS"  # Austrian Schilling
    BEF = "BEF"  # Belgian Franc
    CYP = "CYP"  # Cypriot Pound
    DEM = "DEM"  # Deutsche Mark
    EEK = "EEK"  # Estonian Kroon
    ESP = "ESP"  # Spanish Peseta
    FIM = "FIM"  # Finnish Markka
    FRF = "FRF"  # French Franc
    GRD = "GRD"  # Greek Drachma
    IEP = "IEP"  # Irish Pound
    ITL = "ITL"  # Italian Lira
    LTL = "LTL"  # Lithuanian Litas
    LUF = "LUF"  # Luxembourg Franc
    LVL = "LVL"  # Latvian Lats
    MTL = "MTL"  # Maltese Lira
    NLG = "NLG"  # Dutch Guilder
    PTE = "PTE"  # Portuguese Escudo
    ROL = "ROL"  # Romanian Leu (old)
    RUB = "RUB"  # Russian Ruble
    SIT = "SIT"  # Slovenian Tolar
    SKK = "SKK"  # Slovak Koruna
    TRL = "TRL"  # Turkish Lira (old)
    XCU = "XCU"  # European Currency Unit (historical)
    XEU = "XEU"  # European Currency Unit
    
    def __str__(self) -> str:
        return self.value


# Constant definitions for backward compatibility
USD = Currency.USD.value
EUR = Currency.EUR.value
GBP = Currency.GBP.value
JPY = Currency.JPY.value
CHF = Currency.CHF.value
CAD = Currency.CAD.value
AUD = Currency.AUD.value
BGN = Currency.BGN.value
BRL = Currency.BRL.value
CNY = Currency.CNY.value
DKK = Currency.DKK.value
HKD = Currency.HKD.value
HUF = Currency.HUF.value
IDR = Currency.IDR.value
ILS = Currency.ILS.value
INR = Currency.INR.value
ISK = Currency.ISK.value
KRW = Currency.KRW.value
MXN = Currency.MXN.value
MYR = Currency.MYR.value
NOK = Currency.NOK.value
NZD = Currency.NZD.value
PHP = Currency.PHP.value
PLN = Currency.PLN.value
RON = Currency.RON.value
SEK = Currency.SEK.value
SGD = Currency.SGD.value
THB = Currency.THB.value
TRY = Currency.TRY.value
XDR = Currency.XDR.value
ZAR = Currency.ZAR.value

# Historical currencies
ATS = Currency.ATS.value
BEF = Currency.BEF.value
CYP = Currency.CYP.value
DEM = Currency.DEM.value
EEK = Currency.EEK.value
ESP = Currency.ESP.value
FIM = Currency.FIM.value
FRF = Currency.FRF.value
GRD = Currency.GRD.value
IEP = Currency.IEP.value
ITL = Currency.ITL.value
LTL = Currency.LTL.value
LUF = Currency.LUF.value
LVL = Currency.LVL.value
MTL = Currency.MTL.value
NLG = Currency.NLG.value
PTE = Currency.PTE.value
ROL = Currency.ROL.value
RUB = Currency.RUB.value
SIT = Currency.SIT.value
SKK = Currency.SKK.value
TRL = Currency.TRL.value
XCU = Currency.XCU.value
XEU = Currency.XEU.value


def get_all_currency_codes() -> List[str]:
    """Get list of all currency codes."""
    return [currency.value for currency in Currency]


def is_valid_currency(code: str) -> bool:
    """Check if a currency code is valid."""
    try:
        Currency(code.upper())
        return True
    except ValueError:
        return False


def normalize_currency(code: str) -> str:
    """Normalize currency code to uppercase."""
    normalized = code.upper().strip()
    if not is_valid_currency(normalized):
        raise ValueError(f"Unknown currency code: {code}")
    return normalized