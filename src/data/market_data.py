"""Historical market data retrieval helpers."""

from datetime import date, timedelta

import pandas as pd
import yfinance as yf


REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def get_market_data(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    """Download daily OHLCV data for a ticker."""
    symbol = ticker.strip().upper()
    inclusive_end = end_date + timedelta(days=1)
    data = yf.download(
        symbol,
        start=start_date,
        end=inclusive_end,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if data.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Recent yfinance versions can return a MultiIndex for a single ticker.
    if isinstance(data.columns, pd.MultiIndex):
        if symbol in data.columns.get_level_values(-1):
            data = data.xs(symbol, axis=1, level=-1)
        else:
            data.columns = data.columns.get_level_values(0)

    available = [column for column in REQUIRED_COLUMNS if column in data.columns]
    cleaned = data[available].copy()
    for column in REQUIRED_COLUMNS:
        if column not in cleaned:
            cleaned[column] = pd.NA

    cleaned = cleaned[REQUIRED_COLUMNS]
    cleaned.index = pd.to_datetime(cleaned.index)
    return cleaned.sort_index().dropna(subset=["Close"])


def get_market_snapshot(data: pd.DataFrame) -> dict:
    """Return headline values derived from a historical price frame."""
    empty = {
        "recent_price": None,
        "period_return": None,
        "daily_return": None,
        "volume": None,
    }
    if data.empty:
        return empty

    close = data["Close"].dropna()
    if close.empty:
        return empty

    period_return = (close.iloc[-1] / close.iloc[0]) - 1 if len(close) > 1 else None
    daily_return = close.pct_change().iloc[-1] if len(close) > 1 else None
    volume = data["Volume"].dropna()
    return {
        "recent_price": float(close.iloc[-1]),
        "period_return": float(period_return) if period_return is not None else None,
        "daily_return": float(daily_return) if pd.notna(daily_return) else None,
        "volume": float(volume.iloc[-1]) if not volume.empty else None,
    }
