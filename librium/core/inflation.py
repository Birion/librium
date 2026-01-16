import requests
from typing import Dict, Optional, Any
from datetime import datetime
from librium.core.logging import get_logger

logger = get_logger("core.inflation")

# Using Ninja API for inflation and exchange rates as they are generally free/easy to use for small projects
# or similar public APIs. For this task, I'll use a reliable public API.
# World Bank API is good for inflation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-api
# Exchange rates: https://exchangerate.host/ (sometimes needs key now) or https://api.exchangerate-api.com/v4/latest/USD


class InflationService:
    """Service to fetch inflation data."""

    _inflation_cache: Dict[str, Dict[int, float]] = {}

    @classmethod
    def get_inflation_data(cls, country_code: str = "USA") -> Dict[int, float]:
        """
        Fetch annual inflation rates (CPI) for a given country from World Bank.
        Returns a mapping of year -> inflation rate (percentage).
        """
        if country_code in cls._inflation_cache:
            return cls._inflation_cache[country_code]

        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/FP.CPI.TOTL.ZG?format=json&per_page=100"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or not isinstance(data[1], list):
                logger.error(f"Invalid response from World Bank API for {country_code}")
                return {}

            rates = {}
            for entry in data[1]:
                year = int(entry["date"])
                value = entry["value"]
                if value is not None:
                    rates[year] = value

            cls._inflation_cache[country_code] = rates
            return rates
        except Exception as e:
            logger.error(f"Error fetching inflation data for {country_code}: {e}")
            return {}

    @classmethod
    def get_inflation_factors(cls, currency: str = "USD") -> Dict[int, float]:
        """
        Calculate inflation factors relative to current year.
        Inflation factor for year Y = (1 + r_{Y+1}) * (1 + r_{Y+2}) * ... * (1 + r_{current})
        where r is the inflation rate for that year.

        Note: World Bank data is usually delayed by a year or two.
        We'll map currencies to countries for inflation data.
        """
        currency_to_country = {
            "USD": "USA",
            "EUR": "EMU",  # Euro area
            "GBP": "GBR",
            "CZK": "CZE",
        }

        country_code = currency_to_country.get(currency, "USA")
        rates = cls.get_inflation_data(country_code)

        if not rates:
            return {}

        current_year = datetime.now().year
        factors = {}

        # Sort years descending
        sorted_years = sorted(rates.keys(), reverse=True)

        cumulative_factor = 1.0
        # We want factor to adjust year Y to current year value.
        # If rates[year] is the inflation IN that year.
        # Price in year Y * (1 + rate_{Y+1}) ...

        # Actually World Bank FP.CPI.TOTL.ZG is "Inflation, consumer prices (annual %)"
        # It means how much prices increased in THAT year compared to PREVIOUS year.
        # So value in year 2024 = value in 2023 * (1 + inflation_2024/100)

        factors[current_year] = 1.0
        running_factor = 1.0

        for year in sorted_years:
            if year > current_year:
                continue

            # The rate for year Y is the increase FROM Y-1 TO Y.
            # To bring Y to current:
            # Value_current = Value_Y * (1 + rate_{Y+1}/100) * (1 + rate_{Y+2}/100) ... * (1 + rate_{current}/100)

            factors[year] = running_factor

            # Update running factor for the NEXT (earlier) year
            rate = rates.get(year)
            if rate is not None:
                running_factor *= 1 + rate / 100.0

        return factors
