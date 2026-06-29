 Quant Trading Strategy Backtester

A Streamlit web app for backtesting classic technical-analysis trading strategies on real market data pulled live from Yahoo Finance. Run a single ticker or compare a whole portfolio, and inspect performance metrics, candlestick charts, equity curves, and trade logs — all in your browser.

##  Features

- **Six built-in strategies**: SMA, EMA, RSI, MACD, Bollinger Bands, and VWAP crossover/signal logic
- **Single-ticker or portfolio mode** — enter one ticker or a comma-separated list (e.g. `AAPL, MSFT, GOOGL`) to backtest and compare them together
- **Live data** via `yfinance` for any date range you choose
- **Interactive candlestick chart** with buy/sell markers and quick time-range filters (1W / 1M / 3M / 6M / 1Y / ALL)
- **Equity curve** comparing the strategy against a Buy & Hold benchmark
- **Performance metrics**: Total Return, Sharpe Ratio, Sortino Ratio, Calmar Ratio, Maximum Drawdown, Win Rate, and Total Trades
- **Portfolio comparison table** and equal-weight portfolio equity curve when multiple tickers are entered
- **Trade log** with entry/exit dates, prices, P&L, and percentage return — downloadable as CSV
- Dark-themed, custom-styled UI built with Streamlit + Plotly

##  Project Structure

.
├── app.py            # Streamlit UI — sidebar controls, charts, metrics, trade log
├── backtester.py      # Backtester class — runs strategies, computes returns & trade log
├── indicators.py      # Technical indicator calculations (SMA, EMA, RSI, MACD, Bollinger Bands, VWAP)
├── metrics.py          # Performance metric calculations (Sharpe, Sortino, Calmar, drawdown, etc.)
└── .gitignore

##  Getting Started

### Prerequisite
- Python 3.9+
### Run the app
Then open the local URL Streamlit prints (typically `http://localhost:8501`) in your browser.

##  How to Use

1. Enter one or more stock tickers in the sidebar (comma-separated for portfolio mode).
2. Choose a strategy: **SMA**, **EMA**, **RSI**, **MACD**, **Bollinger Bands**, or **VWAP**.
3. Adjust strategy parameters (e.g. short/long window for SMA/EMA, window and standard deviation for Bollinger Bands) — RSI, MACD, and VWAP use sensible defaults.
4. Pick a start and end date.
5. Click **Run Backtest**.
6. Review the performance metrics, candlestick chart with buy/sell signals, equity curve vs. Buy & Hold, and the downloadable trade log. In portfolio mode, you'll also get a comparison table and per-ticker detail tabs.

##  Strategy Logic

| Strategy | Signal Rule |
|---|---|
| **SMA** | Long when short-period SMA > long-period SMA |
| **EMA** | Long when short-period EMA > long-period EMA |
| **RSI** | Enter long when RSI < 30, exit when RSI > 70 |
| **MACD** | Long when MACD line > signal line |
| **Bollinger Bands** | Enter long when price closes below the lower band, exit when price closes above the upper band |
| **VWAP** | Long when price closes above VWAP |

All signals are shifted by one period before being applied as positions to avoid lookahead bias.

##  Metrics Explained

- **Total Return** – cumulative strategy return over the backtest period
- **Buy & Hold** – return from simply holding the asset over the same period, for comparison
- **Sharpe Ratio** – risk-adjusted return using total volatility
- **Sortino Ratio** – risk-adjusted return using only downside volatility
- **Calmar Ratio** – annualized return relative to maximum drawdown
- **Maximum Drawdown** – largest peak-to-trough decline in the equity curve
- **Win Rate** – percentage of profitable periods/trades
- **Total Trades** – number of completed buy/sell round trips

##  Tech Stack

- [Streamlit](https://streamlit.io/) — web app framework
- [yfinance](https://github.com/ranaroussi/yfinance) — market data
- [pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — data processing
- [Plotly](https://plotly.com/python/) — interactive charting

# <img width="1440" height="625" alt="Screenshot 2026-06-29 183735" src="https://github.com/user-attachments/assets/696100b5-666b-4da4-af57-5916fde7541d" />
<img width="1520" height="788" alt="Screenshot 2026-06-29 183727" src="https://github.com/user-attachments/assets/3ea2904f-5b78-4168-ad8e-fe77fbfbd67b" />
<img width="1861" height="791" alt="Screenshot 2026-06-29 183719" src="https://github.com/user-attachments/assets/1bba82a4-5d18-445e-b230-8aaf97874e79" />

##  Disclaimer

This project is for educational and research purposes only. It does not constitute financial advice, and past backtested performance is not indicative of future results. Use at your own risk.

## 📄 License

No license has been specified for this repository yet. Add a `LICENSE` file if you'd like to define usage terms.
