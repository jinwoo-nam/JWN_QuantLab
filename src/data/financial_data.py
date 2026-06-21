"""Company fundamental data retrieval helpers."""

from typing import Any

import yfinance as yf


METRIC_KEYS = {
    "market_cap": "marketCap",
    "trailing_pe": "trailingPE",
    "price_to_book": "priceToBook",
    "return_on_equity": "returnOnEquity",
    "debt_to_equity": "debtToEquity",
    "profit_margins": "profitMargins",
}


def _safe_number(value: Any) -> float | None:
    """Convert a value to float while treating invalid data as missing."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_financial_metrics(ticker: str) -> dict[str, float | None]:
    """Load selected valuation and profitability metrics from yfinance."""
    empty_result = {name: None for name in METRIC_KEYS}
    try:
        info = yf.Ticker(ticker.strip().upper()).info or {}
    except Exception:
        return empty_result

    return {
        output_name: _safe_number(info.get(yfinance_name))
        for output_name, yfinance_name in METRIC_KEYS.items()
    }
