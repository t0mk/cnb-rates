"""Command-line interface for cnb_rates package."""

import sys
import json
import csv
import argparse
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any

from . import rate1, rate, years, currencies, RateSession, __version__
from .exceptions import CurrencyNotFoundError, DateNotFoundError, DataFileError
from .utils import format_currency_rate


def format_output(currency: str, date_str: str, amount: Optional[float], 
                 czk_value: float, output_format: str = "text") -> str:
    """Format the output for CLI."""
    if output_format == "json":
        data = {
            "currency": currency,
            "date": date_str,
            "amount": amount or 1.0,
            "czk_value": round(czk_value, 6),
            "rate_per_unit": round(czk_value / (amount or 1.0), 6)
        }
        return json.dumps(data, indent=2)
    elif output_format == "csv":
        return f"{currency},{date_str},{amount or 1.0},{czk_value:.6f},{czk_value / (amount or 1.0):.6f}"
    else:  # text format
        return format_currency_rate(currency, date_str, amount or 1, czk_value)


def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """Generate list of dates between start_date and end_date."""
    start = datetime.strptime(start_date, "%d.%m.%Y")
    end = datetime.strptime(end_date, "%d.%m.%Y")
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%d.%m.%Y"))
        current += timedelta(days=1)
    
    return dates


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Czech National Bank exchange rates",
        prog="cnb-rates",
        epilog="Examples:\n"
               "  cnb-rates 2025-01-05 EUR\n"
               "  cnb-rates 2025/11/17 USD 1.5\n"
               "  cnb-rates 17.11.2025 GBP --format json\n"
               "  cnb-rates --from 2024-01-01 --to 2024-01-07 USD\n"
               "  cnb-rates --list-years\n"
               "  cnb-rates --list-currencies",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Version information
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"cnb-rates {__version__}"
    )
    
    # Output format
    parser.add_argument(
        "--format", 
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)"
    )
    
    # Date range options
    parser.add_argument(
        "--from",
        dest="from_date",
        help="Start date for range query (YYYY-MM-DD, DD.MM.YYYY, or YYYY/MM/DD)"
    )
    parser.add_argument(
        "--to",
        dest="to_date", 
        help="End date for range query (YYYY-MM-DD, DD.MM.YYYY, or YYYY/MM/DD)"
    )
    
    # Mutually exclusive group for main commands vs info commands
    group = parser.add_mutually_exclusive_group(required=False)
    
    # Info commands
    group.add_argument(
        "--list-years", 
        action="store_true", 
        help="List available data years"
    )
    group.add_argument(
        "--list-currencies", 
        action="store_true", 
        help="List available currencies"
    )
    
    # Main conversion command
    parser.add_argument(
        "date", 
        nargs="?", 
        help="Date in YYYY-MM-DD, DD.MM.YYYY, or YYYY/MM/DD format"
    )
    
    # Currency and amount for conversion
    parser.add_argument(
        "currency", 
        nargs="?", 
        help="Currency code (e.g., USD, EUR, GBP)"
    )
    parser.add_argument(
        "amount", 
        nargs="?", 
        type=float, 
        default=1.0,
        help="Amount to convert (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.list_years:
            available_years = years()
            if args.format == "json":
                print(json.dumps({"years": available_years}, indent=2))
            elif args.format == "csv":
                print("year")
                for year in available_years:
                    print(year)
            else:
                print(f"Available years ({len(available_years)}):")
                # Print in columns
                cols = 10
                for i in range(0, len(available_years), cols):
                    row = available_years[i:i+cols]
                    print("  " + "  ".join(f"{y:>4}" for y in row))
            return
        
        elif args.list_currencies:
            available_currencies = currencies()
            if args.format == "json":
                print(json.dumps({"currencies": available_currencies}, indent=2))
            elif args.format == "csv":
                print("currency")
                for currency in available_currencies:
                    print(currency)
            else:
                print(f"Available currencies ({len(available_currencies)}):")
                # Print in columns for better readability
                cols = 6
                for i in range(0, len(available_currencies), cols):
                    row = available_currencies[i:i+cols]
                    print("  " + "  ".join(f"{c:>3}" for c in row))
            return
        
        elif args.from_date or args.to_date:
            # Date range query - currency should be in positional argument
            if not args.currency and not (hasattr(args, 'currency') and args.currency):
                # Check if currency is in the positional date argument
                if args.date:
                    # Swap them - user put currency in date position
                    args.currency = args.date
                    args.date = None
                else:
                    parser.error("Currency is required for date range queries")
            
            if not args.from_date or not args.to_date:
                parser.error("Both --from and --to dates are required for range queries")
            
            # Validate currency
            available_currencies = currencies()
            currency_upper = args.currency.upper()
            if currency_upper not in available_currencies:
                print(f"Error: Currency '{args.currency}' not supported", file=sys.stderr)
                print(f"Available currencies: {', '.join(available_currencies)}", file=sys.stderr)
                sys.exit(1)
            
            # Parse date range (convert to internal format)
            from .utils import parse_date
            start_date_str = parse_date(args.from_date)
            end_date_str = parse_date(args.to_date)
            
            # Generate date range
            date_list = generate_date_range(start_date_str, end_date_str)
            
            # Batch processing with RateSession for performance
            results = []
            with RateSession() as session:
                for date_str in date_list:
                    try:
                        czk_value = session.get_rate(currency_upper, date_str, args.amount)
                        results.append({
                            "date": date_str,
                            "value": czk_value
                        })
                    except (CurrencyNotFoundError, DateNotFoundError):
                        # Skip dates without data
                        continue
            
            # Output results
            if args.format == "json":
                output_data = {
                    "currency": currency_upper,
                    "amount": args.amount,
                    "from_date": args.from_date,
                    "to_date": args.to_date,
                    "rates": results
                }
                print(json.dumps(output_data, indent=2))
            elif args.format == "csv":
                print("date,currency,amount,czk_value,rate_per_unit")
                for result in results:
                    rate_per_unit = result["value"] / args.amount
                    print(f"{result['date']},{currency_upper},{args.amount},{result['value']:.6f},{rate_per_unit:.6f}")
            else:
                print(f"Exchange rates for {currency_upper} from {args.from_date} to {args.to_date}:")
                for result in results:
                    formatted = format_currency_rate(currency_upper, result["date"], args.amount, result["value"])
                    print(f"  {formatted}")
                print(f"Total: {len(results)} rates")
        
        else:
            # Single date conversion
            if not args.date or not args.currency:
                # If no arguments provided, show help
                if not any([args.date, args.currency, args.list_years, args.list_currencies]):
                    parser.print_help()
                    return
                parser.error("Date and currency are required for conversion")
            
            # Validate currency
            available_currencies = currencies()
            currency_upper = args.currency.upper()
            if currency_upper not in available_currencies:
                print(f"Error: Currency '{args.currency}' not supported", file=sys.stderr)
                if args.format == "text":
                    print(f"Available currencies: {', '.join(available_currencies[:10])}...", file=sys.stderr)
                sys.exit(1)
            
            # Perform conversion
            if args.amount == 1.0:
                czk_value = rate1(currency_upper, args.date)
                amount_for_display = None
            else:
                czk_value = rate(currency_upper, args.date, args.amount)
                amount_for_display = args.amount
            
            # Output result
            result = format_output(currency_upper, args.date, amount_for_display, czk_value, args.format)
            print(result)
    
    except CurrencyNotFoundError as e:
        if args.format == "json":
            error_data = {"error": "currency_not_found", "message": str(e)}
            print(json.dumps(error_data), file=sys.stderr)
        else:
            print(f"Currency error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except DateNotFoundError as e:
        if args.format == "json":
            error_data = {"error": "date_not_found", "message": str(e)}
            print(json.dumps(error_data), file=sys.stderr)
        else:
            print(f"Date error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except DataFileError as e:
        if args.format == "json":
            error_data = {"error": "data_file_error", "message": str(e)}
            print(json.dumps(error_data), file=sys.stderr)
        else:
            print(f"Data file error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except ValueError as e:
        if args.format == "json":
            error_data = {"error": "invalid_input", "message": str(e)}
            print(json.dumps(error_data), file=sys.stderr)
        else:
            print(f"Invalid input: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        if args.format == "json":
            error_data = {"error": "unexpected_error", "message": str(e)}
            print(json.dumps(error_data), file=sys.stderr)
        else:
            print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()