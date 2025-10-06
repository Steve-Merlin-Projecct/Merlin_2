"""
Salary Formatting Utilities
Provides consistent salary formatting with currency across the application
"""

from typing import Optional


def format_salary_range(
    salary_low: Optional[int] = None, salary_high: Optional[int] = None, currency: str = "CAD"
) -> str:
    """
    Format salary range with proper currency display

    Args:
        salary_low: Minimum salary amount
        salary_high: Maximum salary amount
        currency: Currency code (CAD, USD, etc.)

    Returns:
        Formatted salary string with currency
    """
    if not salary_low and not salary_high:
        return "Salary not specified"

    if salary_low and salary_high:
        if salary_low == salary_high:
            return f"${salary_low:,} {currency}"
        else:
            return f"${salary_low:,} - ${salary_high:,} {currency}"
    elif salary_low:
        return f"${salary_low:,}+ {currency}"
    elif salary_high:
        return f"Up to ${salary_high:,} {currency}"

    return "Salary not specified"


def format_single_salary(amount: Optional[int], currency: str = "CAD", period: str = "annually") -> str:
    """
    Format single salary amount with currency and period

    Args:
        amount: Salary amount
        currency: Currency code (CAD, USD, etc.)
        period: Salary period (annually, monthly, hourly)

    Returns:
        Formatted salary string
    """
    if not amount:
        return "Amount not specified"

    formatted_amount = f"${amount:,} {currency}"

    if period and period != "annually":
        formatted_amount += f" {period}"

    return formatted_amount


def get_currency_from_location(location: Optional[str] = None, country: Optional[str] = None) -> str:
    """
    Determine currency based on location

    Args:
        location: Location string
        country: Country name

    Returns:
        Currency code (CAD, USD, etc.)
    """
    if country:
        if "canada" in country.lower():
            return "CAD"
        elif "united states" in country.lower() or "usa" in country.lower():
            return "USD"

    if location:
        location_lower = location.lower()
        # Canadian indicators
        if any(
            indicator in location_lower
            for indicator in [
                "canada",
                "alberta",
                "ontario",
                "quebec",
                "bc",
                "british columbia",
                "saskatchewan",
                "manitoba",
                "nova scotia",
                "new brunswick",
                "newfoundland",
                "pei",
                "yukon",
                "northwest territories",
                "nunavut",
            ]
        ):
            return "CAD"
        # US indicators
        elif any(
            indicator in location_lower
            for indicator in ["usa", "united states", "california", "texas", "new york", "florida"]
        ):
            return "USD"

    # Default to CAD for Canadian job board
    return "CAD"


def extract_salary_from_text(salary_text: str) -> dict:
    """
    Extract salary information from text with currency detection

    Args:
        salary_text: Raw salary text

    Returns:
        Dictionary with salary_low, salary_high, currency, period
    """
    import re

    result = {"salary_low": None, "salary_high": None, "currency": "CAD", "period": "annually"}

    if not salary_text:
        return result

    # Extract currency
    if "USD" in salary_text.upper():
        result["currency"] = "USD"
    elif "CAD" in salary_text.upper():
        result["currency"] = "CAD"

    # Extract period
    text_lower = salary_text.lower()
    if any(word in text_lower for word in ["hour", "hourly", "/hr", "per hour"]):
        result["period"] = "hourly"
    elif any(word in text_lower for word in ["month", "monthly", "/mo", "per month"]):
        result["period"] = "monthly"

    # Extract numbers
    numbers = re.findall(r"\d+(?:\.\d+)?", salary_text.replace(",", ""))
    if numbers:
        nums = [int(float(n)) for n in numbers]
        if len(nums) == 1:
            result["salary_low"] = result["salary_high"] = nums[0]
        elif len(nums) >= 2:
            result["salary_low"] = min(nums)
            result["salary_high"] = max(nums)

    return result
