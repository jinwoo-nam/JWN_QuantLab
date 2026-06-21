# ValueQuant AI

ValueQuant AI is an educational stock research dashboard built with Python and Streamlit. It combines public market data, selected financial metrics, recent news, technical indicators, and a transparent rule-based research report.

> **This is not financial advice.** ValueQuant AI is for education and research only. It does not execute trades or provide personalized investment recommendations.

## Features

- Search by public stock ticker
- Select a historical date range
- Download OHLCV data with `yfinance`
- View an interactive Plotly price chart
- Calculate 20-day and 60-day moving averages
- Calculate daily and cumulative returns
- Display recent price, returns, and volume
- Display valuation, profitability, and leverage metrics
- Show recent linked news headlines when available
- Generate a rule-based AI-style research note
- Handle missing data and network failures gracefully

## Project Structure

```text
JWN_QuantLab/
├── app.py
├── requirements.txt
├── README.md
└── src/
    ├── analysis/
    │   ├── indicators.py
    │   └── report.py
    ├── data/
    │   ├── financial_data.py
    │   ├── market_data.py
    │   └── news_data.py
    └── utils/
        └── config.py
```

## Installation

Python 3.10 or newer is recommended.

1. Clone the repository:

   ```bash
   git clone https://github.com/jinwoo-nam/JWN_QuantLab.git
   cd JWN_QuantLab
   ```

2. Create and activate a virtual environment.

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   macOS or Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run the App

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, enter a ticker such as `AAPL`, select a date range, and click **Analyze**.

## How the Report Works

The v0.1 report is fully rule-based. It uses price direction, moving averages, historical volatility, valuation ratios, profitability, and leverage to create a readable research note. It does not call OpenAI or any paid API. Its rules are visible in `src/analysis/report.py`.

## Limitations

- `yfinance` data may be delayed, unavailable, incomplete, or revised.
- Financial metrics are not available for every ticker or asset type.
- News availability and payload formats can vary.
- The report is descriptive and does not predict future returns.
- No brokerage connection or trade execution is included.

## Roadmap

- Add peer comparison and company screening
- Add financial statement trend analysis
- Add more indicators and risk analytics
- Add watchlists and optional SQLite persistence
- Add SEC filing and earnings transcript research
- Add retrieval-augmented generation over trusted sources
- Add an optional LLM report layer with source citations
- Add tests, deployment configuration, and continuous integration

## Progress Log

- 2026-06-21: GitHub repository setup and usage learned; Codex usage learned.
- 2026-06-21: ValueQuant AI v0.1 MVP codebase created.
