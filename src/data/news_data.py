"""Recent company news retrieval helpers."""

from datetime import datetime, timezone
from typing import Any

import yfinance as yf

from src.utils.config import MAX_NEWS_ITEMS


def _format_timestamp(value: Any) -> str | None:
    """Convert a Unix timestamp into a readable UTC date."""
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return None


def get_recent_news(ticker: str, limit: int = MAX_NEWS_ITEMS) -> list[dict]:
    """Return normalized news items from flat or nested yfinance payloads."""
    try:
        raw_news = yf.Ticker(ticker.strip().upper()).news or []
    except Exception:
        return []

    normalized: list[dict] = []
    for item in raw_news[:limit]:
        content = item.get("content") if isinstance(item, dict) else None
        source = content if isinstance(content, dict) else item
        if not isinstance(source, dict):
            continue

        provider = source.get("provider")
        publisher = provider.get("displayName") if isinstance(provider, dict) else None
        publisher = publisher or source.get("publisher")

        canonical_url = source.get("canonicalUrl")
        click_url = source.get("clickThroughUrl")
        link = canonical_url.get("url") if isinstance(canonical_url, dict) else None
        if not link and isinstance(click_url, dict):
            link = click_url.get("url")
        link = link or source.get("link")

        published = source.get("pubDate")
        if isinstance(published, str):
            published = published[:10]
        else:
            published = _format_timestamp(source.get("providerPublishTime"))

        title = source.get("title")
        if title:
            normalized.append(
                {
                    "title": title,
                    "publisher": publisher or "Unknown publisher",
                    "link": link,
                    "published": published,
                }
            )
    return normalized
