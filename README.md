# cnb-rates

Another Czech National Bank exchange rates package for Python.

Další balíček poskytující kurzy ČNB. Data do konce 2025, distribuována spolu s balíčkem, v [data/all.csv.xz](data/all.csv.xz).

## Try

```bash
uvx cnb-rates EUR 2025-10-28
```

## Installation

```bash
pip install cnb-rates
```

## Usage

### Command Line

```bash
# Get rate for 1 unit of currency
python -m cnb_rates 2025-01-05 EUR
python -m cnb_rates 05.01.2025 USD
python -m cnb_rates 2025/01/05 GBP

# Convert specific amount
python -m cnb_rates 2025-01-05 USD 1.5

# List available data
python -m cnb_rates --list-years
python -m cnb_rates --list-currencies
```

### Python API

```python
import cnb_rates
from datetime import date

# Get CZK value of 1 USD on specific date
rate = cnb_rates.rate1(cnb_rates.USD, "02.01.2025")
print(f"1 USD = {rate} CZK")

# Convert amount
czk_value = cnb_rates.rate(cnb_rates.EUR, "2025-01-02", 100)
print(f"100 EUR = {czk_value} CZK")

# Using datetime.date
rate = cnb_rates.rate1(cnb_rates.GBP, date(2025, 1, 2))

# List available data
print("Available years:", cnb_rates.years())
print("Available currencies:", cnb_rates.currencies())
```

## API

### Functions

- `rate1(currency, date)` - Get CZK value of 1 unit of currency
- `rate(currency, date, amount)` - Get CZK value of specified amount  
- `years()` - List available data years
- `currencies()` - List supported currencies

### Currency Constants

Available as `cnb_rates.USD`, `cnb_rates.EUR`, etc:

AUD, BGN, BRL, CAD, CHF, CNY, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, ISK, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PLN, RON, SEK, SGD, THB, TRY, USD, XDR, ZAR

### Date Formats

Supports multiple date formats:
- `datetime.date` objects
- `"DD.MM.YYYY"` strings (e.g., "02.01.2025") 
- `"YYYY-MM-DD"` strings (e.g., "2025-01-02")
- `"YYYY/MM/DD"` strings (e.g., "2025/01/02")

**Note:** If the requested date is not available (e.g., weekends, holidays), the package automatically uses the most recent previous date with available data. This includes searching across years if needed (e.g., January 1st will use December 31st from the previous year).

## Data Source

https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/rok_form.html

