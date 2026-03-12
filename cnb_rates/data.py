"""Data loading and caching for cnb_rates package."""

import csv
import lzma
import os
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional, NamedTuple
from functools import lru_cache

from .exceptions import DataFileError


class DateInfo(NamedTuple):
    """Information about a specific date's exchange rate data."""
    date_str: str
    year: int
    row: List[str]
    header: List[str]
    currencies: Dict[str, int]


class DataIndex:
    """Indexed data for fast lookups."""
    
    def __init__(self, all_data: Dict):
        self.all_data = all_data
        self.date_index = self._build_date_index()
        self.date_range = self._calculate_date_range()
        self.all_currencies = self._collect_all_currencies()
    
    def _build_date_index(self) -> List[Tuple[datetime, DateInfo]]:
        """Build sorted index of all dates for fast lookups."""
        date_index = []
        
        for year, year_data in self.all_data.items():
            for date_str, date_data in year_data["data"].items():
                try:
                    dt = datetime.strptime(date_str, "%d.%m.%Y")
                    date_info = DateInfo(
                        date_str=date_str,
                        year=year,
                        row=date_data["row"],
                        header=date_data["header"],
                        currencies=date_data["currencies"]
                    )
                    date_index.append((dt, date_info))
                except ValueError:
                    continue
        
        # Sort by date for binary search
        return sorted(date_index, key=lambda x: x[0])
    
    def _calculate_date_range(self) -> Tuple[str, str]:
        """Calculate the available date range."""
        if not self.date_index:
            return ("", "")
        
        earliest = self.date_index[0][1].date_str
        latest = self.date_index[-1][1].date_str
        return (earliest, latest)
    
    def _collect_all_currencies(self) -> List[str]:
        """Collect all unique currencies across all dates."""
        currencies = set()
        for _, date_info in self.date_index:
            currencies.update(date_info.currencies.keys())
        return sorted(list(currencies))
    
    def find_date(self, target_dt: datetime) -> Optional[DateInfo]:
        """Find exact date or most recent previous date using binary search."""
        if not self.date_index:
            return None
        
        # Binary search for the target date or closest previous date
        left, right = 0, len(self.date_index) - 1
        best_match = None
        
        while left <= right:
            mid = (left + right) // 2
            mid_dt, mid_info = self.date_index[mid]
            
            if mid_dt == target_dt:
                return mid_info
            elif mid_dt < target_dt:
                best_match = mid_info
                left = mid + 1
            else:
                right = mid - 1
        
        return best_match
    
    def get_years(self) -> List[str]:
        """Get list of available years."""
        return [str(year) for year in sorted(self.all_data.keys())]


class DataCache:
    """Thread-safe singleton cache for exchange rate data."""
    
    _instance = None
    _lock = threading.Lock()
    _data_index: Optional[DataIndex] = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def data_index(self) -> DataIndex:
        """Get the data index, loading it if necessary."""
        if self._data_index is None:
            with self._lock:
                if self._data_index is None:
                    raw_data = _load_all_data()
                    self._data_index = DataIndex(raw_data)
        return self._data_index
    
    def invalidate(self):
        """Clear the cache (useful for testing or data updates)."""
        with self._lock:
            self._data_index = None


def _get_data_dir() -> str:
    """Get the path to the data directory."""
    package_dir = os.path.dirname(__file__)
    return os.path.join(os.path.dirname(package_dir), "data")


def _load_all_data() -> Dict:
    """Load all exchange rate data from the all.csv.xz file."""
    data_dir = _get_data_dir()
    file_path = os.path.join(data_dir, "all.csv.xz")
    
    if not os.path.exists(file_path):
        raise DataFileError(f"Data file not found: {file_path}")
    
    try:
        # Data structure to hold all parsed data
        all_data = {}
        current_header = None
        current_currencies = {}
        
        with lzma.open(file_path, 'rt', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            
            for row_num, row in enumerate(reader, 1):
                if not row:  # Skip empty rows
                    continue
                
                try:
                    # Check if this is a header row
                    if row[0] == "Datum":
                        current_header = row
                        # Parse header to get currency mappings
                        current_currencies = {}
                        for i, col in enumerate(row[1:], 1):  # Skip first column (Datum)
                            # Extract currency code from column headers like "1 USD", "100 HUF"
                            parts = col.strip().split()
                            if len(parts) == 2:
                                try:
                                    # Validate denomination is numeric
                                    int(parts[0])
                                    currency = parts[1]
                                    current_currencies[currency] = i
                                except ValueError:
                                    # Skip invalid denominations
                                    continue
                    else:
                        # This is a data row
                        if current_header is None:
                            continue  # Skip data rows without header
                        
                        # Validate row has enough columns
                        if len(row) < len(current_header):
                            continue
                            
                        row_date = row[0]
                        try:
                            # Validate date format
                            datetime.strptime(row_date, "%d.%m.%Y")
                            year = int(row_date.split(".")[2])
                        except ValueError:
                            continue  # Skip invalid dates
                        
                        # Initialize year data if not exists
                        if year not in all_data:
                            all_data[year] = {
                                "headers": [],
                                "data": {}
                            }
                        
                        # Store the header and currency mapping for this date
                        all_data[year]["data"][row_date] = {
                            "row": row,
                            "header": current_header,
                            "currencies": current_currencies.copy()
                        }
                        
                        # Track unique headers for this year
                        if current_header not in all_data[year]["headers"]:
                            all_data[year]["headers"].append(current_header)
                            
                except Exception as e:
                    # Log problematic row but continue processing
                    continue
        
        if not all_data:
            raise DataFileError("No valid data found in file")
            
        return all_data
    
    except Exception as e:
        raise DataFileError(f"Error reading data file {file_path}: {e}")


@lru_cache(maxsize=None)
def get_data_cache() -> DataCache:
    """Get the global data cache instance."""
    return DataCache()


def get_data_index() -> DataIndex:
    """Get the data index from cache."""
    return get_data_cache().data_index


def invalidate_cache():
    """Invalidate the data cache."""
    get_data_cache().invalidate()