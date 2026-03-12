"""Tests for cnb_rates package."""

import unittest
from datetime import date
from cnb_rates import rate1, rate, years, currencies, USD, EUR, HUF
from cnb_rates.core import CurrencyNotFoundError, DateNotFoundError, DataFileError
from cnb_rates.exceptions import InvalidDateFormatError, InvalidDateTypeError


class TestCnbRates(unittest.TestCase):
    
    def test_years_function(self):
        """Test years() returns available years."""
        available_years = years()
        self.assertIsInstance(available_years, list)
        self.assertIn("2024", available_years)
        self.assertIn("2025", available_years)
    
    def test_currencies_function(self):
        """Test currencies() returns available currencies."""
        available_currencies = currencies()
        self.assertIsInstance(available_currencies, list)
        self.assertIn("USD", available_currencies)
        self.assertIn("EUR", available_currencies)
        self.assertIn("HUF", available_currencies)
    
    def test_currency_constants(self):
        """Test currency constants are defined."""
        self.assertEqual(USD, "USD")
        self.assertEqual(EUR, "EUR")
        self.assertEqual(HUF, "HUF")
    
    def test_rate1_with_datetime_date(self):
        """Test rate1() with datetime.date object."""
        test_date = date(2025, 1, 2)
        usd_rate = rate1(USD, test_date)
        self.assertIsInstance(usd_rate, float)
        self.assertGreater(usd_rate, 0)
    
    def test_rate1_with_string_dd_mm_yyyy(self):
        """Test rate1() with DD.MM.YYYY string format."""
        usd_rate = rate1(USD, "02.01.2025")
        self.assertIsInstance(usd_rate, float)
        self.assertGreater(usd_rate, 0)
    
    def test_rate1_with_string_yyyy_mm_dd(self):
        """Test rate1() with YYYY-MM-DD string format."""
        usd_rate = rate1(USD, "2025-01-02")
        self.assertIsInstance(usd_rate, float)
        self.assertGreater(usd_rate, 0)
    
    def test_rate1_consistency_across_formats(self):
        """Test rate1() returns same result for different date formats."""
        rate_dt = rate1(USD, date(2025, 1, 2))
        rate_dd = rate1(USD, "02.01.2025")
        rate_iso = rate1(USD, "2025-01-02")
        rate_slash = rate1(USD, "2025/01/02")
        
        self.assertEqual(rate_dt, rate_dd)
        self.assertEqual(rate_dd, rate_iso)
        self.assertEqual(rate_iso, rate_slash)
    
    def test_rate1_hundred_denomination(self):
        """Test rate1() correctly handles currencies with 100 unit denomination."""
        huf_rate = rate1(HUF, "02.01.2025")
        self.assertIsInstance(huf_rate, float)
        self.assertGreater(huf_rate, 0)
        # HUF rate should be relatively small (since it's per 1 HUF, not per 100)
        self.assertLess(huf_rate, 1)
    
    def test_rate_with_amount(self):
        """Test rate() function with amount multiplication."""
        unit_rate = rate1(USD, "02.01.2025")
        total_rate = rate(USD, "02.01.2025", 100)
        
        self.assertEqual(total_rate, unit_rate * 100)
    
    def test_rate_with_decimal_amount(self):
        """Test rate() function with decimal amount."""
        unit_rate = rate1(EUR, "02.01.2025")
        total_rate = rate(EUR, "02.01.2025", 2.5)
        
        self.assertEqual(total_rate, unit_rate * 2.5)
    
    def test_invalid_currency_raises_error(self):
        """Test that invalid currency raises CurrencyNotFoundError."""
        with self.assertRaises(CurrencyNotFoundError):
            rate1("XXX", "02.01.2025")
    
    def test_invalid_date_raises_error(self):
        """Test that invalid date raises DateNotFoundError."""
        with self.assertRaises(DateNotFoundError):
            rate1(USD, "01.01.1900")
    
    def test_rate1_with_string_yyyy_mm_dd_slash(self):
        """Test rate1() with YYYY/MM/DD string format."""
        usd_rate = rate1(USD, "2025/01/02")
        self.assertIsInstance(usd_rate, float)
        self.assertGreater(usd_rate, 0)
    
    def test_invalid_date_format_raises_error(self):
        """Test that invalid date format raises InvalidDateFormatError."""
        with self.assertRaises(InvalidDateFormatError):
            rate1(USD, "invalid-date")
    
    def test_invalid_date_type_raises_error(self):
        """Test that invalid date type raises InvalidDateTypeError."""
        with self.assertRaises(InvalidDateTypeError):
            rate1(USD, 12345)
    
    def test_cross_year_fallback(self):
        """Test that dates fall back to previous year when needed."""
        # January 1st should fall back to December 31st of previous year
        try:
            rate_jan1 = rate1(USD, "01.01.2025")
            rate_dec31 = rate1(USD, "31.12.2024")
            
            # Should use the same rate (last available date from 2024)
            self.assertEqual(rate_jan1, rate_dec31)
            self.assertIsInstance(rate_jan1, float)
            self.assertGreater(rate_jan1, 0)
        except (DateNotFoundError, DataFileError):
            # Skip if data not available - this is for real data testing
            self.skipTest("Cross-year test data not available")


class TestIntegration(unittest.TestCase):
    """Integration tests using real data."""
    
    def test_real_data_consistency(self):
        """Test that real data is consistent and reasonable."""
        # Test a few major currencies
        for currency in [USD, EUR, HUF]:
            try:
                rate_val = rate1(currency, "02.01.2025")
                self.assertIsInstance(rate_val, float)
                self.assertGreater(rate_val, 0)
                self.assertLess(rate_val, 1000)  # Reasonable upper bound
            except (CurrencyNotFoundError, DateNotFoundError):
                # Skip if data not available
                pass
    
    def test_multiple_years_data(self):
        """Test that multiple years of data are accessible."""
        available_years = years()
        self.assertGreaterEqual(len(available_years), 2)
        
        # Test at least one rate from each year
        for year in available_years[:2]:  # Test first 2 years to avoid too many tests
            test_date = f"02.01.{year}"
            try:
                usd_rate = rate1(USD, test_date)
                self.assertGreater(usd_rate, 0)
            except DateNotFoundError:
                # Skip if specific date not available in that year
                pass


if __name__ == "__main__":
    unittest.main()