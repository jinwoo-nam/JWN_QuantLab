"""Technical indicator calculations used by the dashboard."""

import pandas as pd


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Add moving averages and return series to OHLCV data."""
    enriched = data.copy()
    close = enriched["Close"]
    enriched["MA20"] = close.rolling(window=20, min_periods=1).mean()
    enriched["MA60"] = close.rolling(window=60, min_periods=1).mean()
    enriched["Daily Return"] = close.pct_change()
    enriched["Cumulative Return"] = (
        (close / close.iloc[0]) - 1 if not close.empty and close.iloc[0] != 0 else pd.NA
    )
    return enriched
