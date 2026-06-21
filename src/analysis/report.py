"""Rule-based research report generation for the MVP."""

import pandas as pd


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _price_trend(data: pd.DataFrame) -> tuple[str, list[str]]:
    close = data["Close"].dropna()
    risks: list[str] = []
    if len(close) < 2:
        return "There is not enough price history to evaluate the trend.", risks

    period_return = (close.iloc[-1] / close.iloc[0]) - 1
    latest = close.iloc[-1]
    ma20 = data["MA20"].iloc[-1] if "MA20" in data else None
    ma60 = data["MA60"].iloc[-1] if "MA60" in data else None

    direction = (
        "an upward trend"
        if period_return > 0.05
        else "a downward trend"
        if period_return < -0.05
        else "a mostly sideways trend"
    )
    note = f"The selected period shows {direction}, with a total return of {period_return:.2%}."
    if not _is_missing(ma20) and not _is_missing(ma60):
        if latest > ma20 > ma60:
            note += " Price is above both moving averages, indicating positive momentum."
        elif latest < ma20 < ma60:
            note += " Price is below both moving averages, indicating weak momentum."
        else:
            note += " The moving averages are mixed, so momentum is not decisive."

    daily_returns = close.pct_change().dropna()
    if not daily_returns.empty:
        volatility = daily_returns.std() * (252**0.5)
        if volatility > 0.40:
            risks.append(f"Historical volatility is elevated at roughly {volatility:.1%} annualized.")
        elif volatility > 0.25:
            risks.append(f"Historical volatility is moderate at roughly {volatility:.1%} annualized.")
    return note, risks


def _valuation_note(metrics: dict) -> str:
    pe = metrics.get("trailing_pe")
    price_to_book = metrics.get("price_to_book")
    notes: list[str] = []
    if not _is_missing(pe):
        if pe <= 0:
            notes.append("Trailing P/E is not meaningful because earnings are non-positive.")
        elif pe < 15:
            notes.append(f"Trailing P/E is {pe:.1f}, which appears relatively modest in isolation.")
        elif pe > 30:
            notes.append(f"Trailing P/E is {pe:.1f}, indicating a relatively high earnings multiple.")
        else:
            notes.append(f"Trailing P/E is {pe:.1f}, within a middle valuation range.")
    if not _is_missing(price_to_book):
        notes.append(f"Price-to-book is {price_to_book:.1f}.")
    return " ".join(notes) if notes else "Valuation metrics are unavailable."


def _profitability_note(metrics: dict) -> str:
    roe = metrics.get("return_on_equity")
    margin = metrics.get("profit_margins")
    notes: list[str] = []
    if not _is_missing(roe):
        notes.append(f"Return on equity is {roe:.1%}.")
    if not _is_missing(margin):
        quality = "healthy" if margin > 0.15 else "positive but modest" if margin > 0 else "negative"
        notes.append(f"Profit margin is {margin:.1%}, which is {quality}.")
    return " ".join(notes) if notes else "Profitability metrics are currently unavailable."


def _risk_notes(metrics: dict, price_risks: list[str]) -> list[str]:
    risks = list(price_risks)
    debt_to_equity = metrics.get("debt_to_equity")
    if not _is_missing(debt_to_equity):
        if debt_to_equity > 200:
            risks.append(f"Debt-to-equity is high at {debt_to_equity:.1f}.")
        elif debt_to_equity > 100:
            risks.append(f"Debt-to-equity is notable at {debt_to_equity:.1f}.")
    risks.append("Public market data may be delayed, incomplete, or revised.")
    risks.append("This rule-based report does not evaluate every company or macroeconomic factor.")
    return risks


def generate_research_report(ticker: str, data: pd.DataFrame, metrics: dict) -> str:
    """Generate a transparent, rule-based, LLM-style research note."""
    trend, price_risks = _price_trend(data)
    valuation = _valuation_note(metrics)
    profitability = _profitability_note(metrics)
    risks = _risk_notes(metrics, price_risks)

    close = data["Close"].dropna()
    overall = (
        f"{ticker} should be researched using quantitative data and company filings. "
        "The signals above are descriptive rather than predictive."
    )
    if len(close) > 1:
        period_return = (close.iloc[-1] / close.iloc[0]) - 1
        if period_return > 0 and (metrics.get("profit_margins") or 0) > 0:
            overall = (
                f"{ticker} combines positive selected-period price performance with reported profitability. "
                "Review earnings quality, competitive position, and valuation versus peers."
            )
        elif period_return < 0:
            overall = (
                f"{ticker} has shown weak selected-period price performance. Investigate whether the decline "
                "reflects temporary sentiment or deteriorating fundamentals."
            )

    risk_markdown = "\n".join(f"- {risk}" for risk in risks)
    return f"""
### Price Trend

{trend}

### Valuation

{valuation}

### Profitability

{profitability}

### Risk Factors

{risk_markdown}

### Overall Research Note

{overall}

> **This is not financial advice.**
"""
