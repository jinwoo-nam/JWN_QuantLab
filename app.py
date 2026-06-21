"""Streamlit entry point for the ValueQuant AI MVP."""

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analysis.indicators import add_technical_indicators
from src.analysis.report import generate_research_report
from src.data.financial_data import get_financial_metrics
from src.data.market_data import get_market_data, get_market_snapshot
from src.data.news_data import get_recent_news
from src.utils.config import APP_TITLE, DEFAULT_LOOKBACK_DAYS, DEFAULT_TICKER, DISCLAIMER


st.set_page_config(page_title=APP_TITLE, page_icon="📈", layout="wide")


@st.cache_data(ttl=900, show_spinner=False)
def load_market_data(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    return get_market_data(ticker, start_date, end_date)


@st.cache_data(ttl=3600, show_spinner=False)
def load_financial_metrics(ticker: str) -> dict:
    return get_financial_metrics(ticker)


@st.cache_data(ttl=900, show_spinner=False)
def load_news(ticker: str) -> list[dict]:
    return get_recent_news(ticker)


def format_number(value: object, kind: str = "number") -> str:
    """Format optional numeric values for metric cards."""
    if value is None or pd.isna(value):
        return "N/A"
    number = float(value)
    if kind == "currency":
        return f"${number:,.2f}"
    if kind == "percent":
        return f"{number * 100:,.2f}%"
    if kind == "large":
        for suffix, divisor in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
            if abs(number) >= divisor:
                return f"{number / divisor:,.2f}{suffix}"
        return f"{number:,.0f}"
    return f"{number:,.2f}"


def build_price_chart(data: pd.DataFrame, ticker: str) -> go.Figure:
    """Create a price chart with moving-average overlays."""
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(x=data.index, y=data["Close"], name="Close", line={"color": "#2563eb", "width": 2})
    )
    figure.add_trace(
        go.Scatter(x=data.index, y=data["MA20"], name="20-day MA", line={"color": "#f59e0b"})
    )
    figure.add_trace(
        go.Scatter(x=data.index, y=data["MA60"], name="60-day MA", line={"color": "#dc2626"})
    )
    figure.update_layout(
        title=f"{ticker} Price History",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
        legend={"orientation": "h", "y": 1.02, "x": 0},
        margin={"l": 20, "r": 20, "t": 70, "b": 20},
    )
    return figure


def show_financial_metrics(metrics: dict) -> None:
    first_row = st.columns(3)
    first_row[0].metric("Market Cap", format_number(metrics.get("market_cap"), "large"))
    first_row[1].metric("Trailing P/E", format_number(metrics.get("trailing_pe")))
    first_row[2].metric("Price to Book", format_number(metrics.get("price_to_book")))
    second_row = st.columns(3)
    second_row[0].metric("Return on Equity", format_number(metrics.get("return_on_equity"), "percent"))
    second_row[1].metric("Debt to Equity", format_number(metrics.get("debt_to_equity")))
    second_row[2].metric("Profit Margin", format_number(metrics.get("profit_margins"), "percent"))


def show_news(news_items: list[dict]) -> None:
    if not news_items:
        st.info("No recent news was available for this ticker.")
        return
    for item in news_items:
        title = item.get("title", "Untitled article")
        publisher = item.get("publisher", "Unknown publisher")
        link = item.get("link")
        published = item.get("published")
        if link:
            st.markdown(f"**[{title}]({link})**")
        else:
            st.markdown(f"**{title}**")
        st.caption(" · ".join(part for part in (publisher, published) if part))


st.title(APP_TITLE)
st.caption("A beginner-friendly stock research dashboard powered by public market data.")

with st.sidebar:
    st.header("Research Settings")
    ticker_input = st.text_input("Stock ticker", value=DEFAULT_TICKER)
    default_end = date.today()
    default_start = default_end - timedelta(days=DEFAULT_LOOKBACK_DAYS)
    date_range = st.date_input("Date range", value=(default_start, default_end), max_value=default_end)
    analyze = st.button("Analyze", type="primary", use_container_width=True)
    st.divider()
    st.warning(DISCLAIMER)

if not analyze:
    st.info("Enter a ticker, choose a date range, and click **Analyze** to begin.")
    st.stop()

ticker = ticker_input.strip().upper()
if not ticker:
    st.error("Please enter a stock ticker.")
    st.stop()
if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.error("Please select both a start date and an end date.")
    st.stop()

start_date, end_date = date_range
if start_date >= end_date:
    st.error("The start date must be earlier than the end date.")
    st.stop()

with st.spinner(f"Researching {ticker}..."):
    try:
        market_data = load_market_data(ticker, start_date, end_date)
        financial_metrics = load_financial_metrics(ticker)
        news = load_news(ticker)
    except Exception as error:
        st.error(f"Unable to complete the analysis: {error}")
        st.stop()

if market_data.empty:
    st.error("No market data was found. Check the ticker and selected date range.")
    st.stop()

market_data = add_technical_indicators(market_data)
snapshot = get_market_snapshot(market_data)

st.subheader(f"{ticker} Market Snapshot")
snapshot_columns = st.columns(4)
snapshot_columns[0].metric("Recent Price", format_number(snapshot.get("recent_price"), "currency"))
snapshot_columns[1].metric("Period Return", format_number(snapshot.get("period_return"), "percent"))
snapshot_columns[2].metric("Latest Daily Return", format_number(snapshot.get("daily_return"), "percent"))
snapshot_columns[3].metric("Latest Volume", format_number(snapshot.get("volume"), "large"))
st.plotly_chart(build_price_chart(market_data, ticker), use_container_width=True)

overview_tab, financials_tab, news_tab, report_tab = st.tabs(
    ["Market Data", "Financial Metrics", "Recent News", "AI-Style Report"]
)
with overview_tab:
    display_columns = [
        "Open", "High", "Low", "Close", "Volume", "MA20", "MA60", "Daily Return", "Cumulative Return"
    ]
    st.dataframe(
        market_data[display_columns].tail(20).sort_index(ascending=False),
        use_container_width=True,
    )
with financials_tab:
    show_financial_metrics(financial_metrics)
    if not any(value is not None for value in financial_metrics.values()):
        st.info("Financial metrics are currently unavailable for this ticker.")
with news_tab:
    show_news(news)
with report_tab:
    st.markdown(generate_research_report(ticker, market_data, financial_metrics))

st.divider()
st.error(f"⚠️ {DISCLAIMER}")
