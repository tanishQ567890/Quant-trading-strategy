import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from backtester import Backtester

st.set_page_config(
    page_title="Quant Trading Strategy Backtester",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ---- Global ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #1b2838 100%);
}

/* ---- Header ---- */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem;
}

.main-header h1 {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 50%, #ff6bca 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    letter-spacing: -0.5px;
}

.main-header p {
    color: #8899aa;
    font-size: 1.05rem;
    font-weight: 400;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%);
    border-right: 1px solid rgba(0, 210, 255, 0.1);
}

section[data-testid="stSidebar"] .stMarkdown h2 {
    color: #00d2ff;
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ---- Metric Cards ---- */
div[data-testid="stMetric"] {
    background: rgba(17, 34, 64, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 210, 255, 0.15);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(0, 210, 255, 0.4);
    box-shadow: 0 8px 32px rgba(0, 210, 255, 0.1);
    transform: translateY(-2px);
}

div[data-testid="stMetric"] label {
    color: #8899aa !important;
    font-weight: 500;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #e8f0fe !important;
    font-weight: 700;
    font-size: 1.6rem;
}

/* ---- Section Headers ---- */
.section-header {
    color: #e8f0fe;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(0, 210, 255, 0.2);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ---- Dataframe ---- */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(0, 210, 255, 0.1);
}

/* ---- Buttons ---- */
.stDownloadButton > button {
    background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    letter-spacing: 0.5px;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 210, 255, 0.3);
}

section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1.5rem;
    font-weight: 700;
    font-size: 1rem;
    width: 100%;
    transition: all 0.3s ease;
    letter-spacing: 0.5px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 210, 255, 0.3);
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(17, 34, 64, 0.4);
    border-radius: 12px;
    padding: 0.3rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #8899aa;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
}

.stTabs [aria-selected="true"] {
    background: rgba(0, 210, 255, 0.15) !important;
    color: #00d2ff !important;
}

/* ---- Comparison Table ---- */
.comparison-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(0, 210, 255, 0.15);
    margin: 1rem 0;
}

.comparison-table th {
    background: rgba(0, 210, 255, 0.1);
    color: #00d2ff;
    padding: 0.8rem 1rem;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: left;
}

.comparison-table td {
    padding: 0.7rem 1rem;
    color: #e8f0fe;
    border-top: 1px solid rgba(255,255,255,0.05);
    font-size: 0.95rem;
}

.comparison-table tr:hover td {
    background: rgba(0, 210, 255, 0.05);
}

/* ---- Portfolio Badge ---- */
.portfolio-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 100%);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ---- Divider ---- */
.gradient-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0,210,255,0.3), transparent);
    margin: 2rem 0;
    border: none;
}

/* ---- Time Range Buttons ---- */
.time-range-bar {
    display: flex;
    gap: 0.4rem;
    margin-bottom: 1rem;
    padding: 0.4rem;
    background: rgba(17, 34, 64, 0.5);
    border-radius: 12px;
    border: 1px solid rgba(0, 210, 255, 0.1);
    width: fit-content;
}

.time-range-btn {
    padding: 0.4rem 1rem;
    border-radius: 8px;
    border: none;
    background: transparent;
    color: #8899aa;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.25s ease;
    letter-spacing: 0.5px;
}

.time-range-btn:hover {
    background: rgba(0, 210, 255, 0.1);
    color: #00d2ff;
}

.time-range-btn.active {
    background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(0, 210, 255, 0.25);
}
</style>
""", unsafe_allow_html=True)


PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(13,27,42,0.6)",
    plot_bgcolor="rgba(13,27,42,0.3)",
    font=dict(family="Inter", color="#e8f0fe"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.05)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.05)"
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899aa")
    ),
    margin=dict(l=40, r=20, t=40, b=40),
)


st.markdown("""
<div class="main-header">
    <h1>📈 Quant Trading Backtester</h1>
    <p>Backtest SMA, EMA, RSI, MACD, Bollinger Bands & VWAP strategies on real market data</p>
</div>
""", unsafe_allow_html=True)


st.sidebar.markdown("## ⚙️ Backtest Settings")

ticker_input = st.sidebar.text_input(
    "Ticker(s)",
    "AAPL",
    help="Enter one or more tickers separated by commas (e.g. AAPL, MSFT, GOOGL)"
)

tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

strategy = st.sidebar.selectbox(
    "Strategy",
    ["SMA", "EMA", "RSI", "MACD", "Bollinger Bands", "VWAP"]
)


st.sidebar.markdown("---")
st.sidebar.markdown(" Strategy Parameters")

kwargs = {}

if strategy == "SMA":
    kwargs["short_window"] = st.sidebar.slider(
        "Short Window", 5, 100, 20
    )
    kwargs["long_window"] = st.sidebar.slider(
        "Long Window", 10, 200, 50
    )

elif strategy == "EMA":
    kwargs["short_window"] = st.sidebar.slider(
        "Short Window", 5, 50, 12
    )
    kwargs["long_window"] = st.sidebar.slider(
        "Long Window", 10, 100, 26
    )

elif strategy == "Bollinger Bands":
    kwargs["window"] = st.sidebar.slider(
        "Window", 10, 50, 20
    )
    kwargs["num_std"] = st.sidebar.slider(
        "Std Deviations", 1.0, 3.0, 2.0, 0.1
    )

else:
    st.sidebar.info(
        f"{strategy} uses default parameters."
    )

st.sidebar.markdown("---")

start_date = st.sidebar.date_input(
    "Start Date",
    value=pd.to_datetime("2022-01-01")
)

end_date = st.sidebar.date_input(
    "End Date",
    value=pd.to_datetime("today")
)

portfolio_mode = len(tickers) > 1

if portfolio_mode:
    st.sidebar.markdown(
        '<span class="portfolio-badge">📊 Portfolio Mode</span>',
        unsafe_allow_html=True
    )

run = st.sidebar.button("🚀 Run Backtest", use_container_width=True)


def render_single_result(df, stats, trades, ticker):

    st.markdown(
        '<div class="section-header"> Performance Metrics</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Return", f"{stats['Total Return']}%")
    c2.metric("Sharpe Ratio", stats["Sharpe Ratio"])
    c3.metric("Sortino Ratio", stats["Sortino Ratio"])
    c4.metric("Win Rate", f"{stats['Win Rate']}%")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Max Drawdown", f"{stats['Maximum Drawdown']}%")
    c6.metric("Calmar Ratio", stats["Calmar Ratio"])
    c7.metric("Buy & Hold", f"{stats['Buy & Hold']}%")
    c8.metric("Total Trades", stats["Total Trades"])

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">🕯️ Candlestick Chart</div>',
        unsafe_allow_html=True
    )

    # Time range selector (Groww / Zerodha style)
    time_ranges = {
        "1W": 7, "1M": 30, "3M": 90,
        "6M": 180, "1Y": 365, "ALL": None
    }

    range_key = f"timerange_{ticker}"

    if range_key not in st.session_state:
        st.session_state[range_key] = "ALL"

    cols = st.columns(len(time_ranges))

    for i, (label, days) in enumerate(time_ranges.items()):
        with cols[i]:
            if st.button(
                label,
                key=f"{range_key}_{label}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state[range_key] == label
                    else "secondary"
                )
            ):
                st.session_state[range_key] = label
                st.rerun()

    # Filter data by selected time range
    selected_range = st.session_state[range_key]
    selected_days = time_ranges[selected_range]

    if selected_days is not None and len(df) > 0:
        cutoff = df.index[-1] - pd.Timedelta(days=selected_days)
        chart_df = df[df.index >= cutoff]
    else:
        chart_df = df

    fig = go.Figure()

    # Check if we have OHLC columns
    has_ohlc = all(
        col in chart_df.columns
        for col in ["Open", "High", "Low", "Close"]
    )

    if has_ohlc:
        fig.add_trace(
            go.Candlestick(
                x=chart_df.index,
                open=chart_df["Open"],
                high=chart_df["High"],
                low=chart_df["Low"],
                close=chart_df["Close"],
                name="OHLC",
                increasing_line_color="#00ff88",
                decreasing_line_color="#ff4466"
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Close"],
                mode="lines",
                name="Close",
                line=dict(color="#00d2ff", width=2)
            )
        )

    # Buy / Sell markers (only in visible range)
    buy_signals = chart_df[
        (chart_df["Position"] == 1) &
        (chart_df["Position"].shift(1) == 0)
    ]

    sell_signals = chart_df[
        (chart_df["Position"] == 0) &
        (chart_df["Position"].shift(1) == 1)
    ]

    fig.add_trace(
        go.Scatter(
            x=buy_signals.index,
            y=buy_signals["Close"],
            mode="markers",
            marker=dict(
                color="#00ff88",
                size=12,
                symbol="triangle-up",
                line=dict(color="white", width=1)
            ),
            name="Buy"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=sell_signals.index,
            y=sell_signals["Close"],
            mode="markers",
            marker=dict(
                color="#ff4466",
                size=12,
                symbol="triangle-down",
                line=dict(color="white", width=1)
            ),
            name="Sell"
        )
    )

    # Range period label
    if len(chart_df) > 0:
        period_start = chart_df.index[0].strftime("%b %d, %Y")
        period_end = chart_df.index[-1].strftime("%b %d, %Y")
        range_label = f"{period_start}  →  {period_end}  ({len(chart_df)} trading days)"
    else:
        range_label = "No data"

    fig.update_layout(
        height=550,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        title=dict(
            text=f"<span style='font-size:13px;color:#8899aa'>{range_label}</span>",
            x=0.5,
            xanchor="center"
        ),
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Equity Curve ---

    st.markdown(
        '<div class="section-header">💰 Equity Curve</div>',
        unsafe_allow_html=True
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Equity Curve"],
            name="Strategy",
            line=dict(color="#00d2ff", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(0, 210, 255, 0.08)"
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Buy & Hold"],
            name="Buy & Hold",
            line=dict(color="#7b2ff7", width=2, dash="dash")
        )
    )

    fig2.update_layout(
        height=450,
        xaxis_title="Date",
        yaxis_title="Portfolio Value",
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(fig2, use_container_width=True)

    # --- Trade Log ---

    st.markdown(
        '<div class="section-header">📋 Trade Log</div>',
        unsafe_allow_html=True
    )

    if not trades.empty:

        st.dataframe(
            trades,
            use_container_width=True,
            hide_index=True
        )

        csv = trades.to_csv(index=False)

        st.download_button(
            label="📥 Download Trade Log",
            data=csv,
            file_name=f"trade_log_{ticker}.csv",
            mime="text/csv"
        )

    else:
        st.info("No trades were generated for this strategy/period.")



if run:

    if portfolio_mode:

        with st.spinner("Downloading data for portfolio..."):
            results, portfolio_df = Backtester.run_portfolio(
                tickers, strategy, start_date, end_date, **kwargs
            )

        if not results:
            st.error("No data found for any ticker.")
            st.stop()

        st.session_state["bt_mode"] = "portfolio"
        st.session_state["bt_results"] = results
        st.session_state["bt_portfolio_df"] = portfolio_df


    else:

        ticker = tickers[0]

        with st.spinner(f"Downloading {ticker} data..."):
            try:
                data = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    auto_adjust=True,
                    progress=False
                )
                if data.empty:
                    st.error(f"No data found for ticker '{ticker}'. Please verify the symbol and date range.")
                    st.stop()
            except Exception as e:
                st.error(f"Error downloading data for ticker '{ticker}': {str(e)}")
                st.stop()

        bt = Backtester(data)
        df = bt.run(strategy, **kwargs)
        stats = bt.performance(df)
        trades = bt.trade_log(df)

        st.session_state["bt_mode"] = "single"
        st.session_state["bt_ticker"] = ticker
        st.session_state["bt_df"] = df
        st.session_state["bt_stats"] = stats
        st.session_state["bt_trades"] = trades



if "bt_mode" in st.session_state:

    if st.session_state["bt_mode"] == "portfolio":

        results = st.session_state["bt_results"]
        portfolio_df = st.session_state["bt_portfolio_df"]

        # --- Comparison Table ---

        st.markdown(
            '<div class="section-header">📊 Portfolio Comparison</div>',
            unsafe_allow_html=True
        )

        table_html = '<table class="comparison-table"><tr>'
        table_html += "<th>Ticker</th>"
        table_html += "<th>Total Return</th>"
        table_html += "<th>Sharpe</th>"
        table_html += "<th>Sortino</th>"
        table_html += "<th>Max DD</th>"
        table_html += "<th>Win Rate</th>"
        table_html += "<th>Trades</th>"
        table_html += "</tr>"

        for t, r in results.items():
            s = r["stats"]
            table_html += f"<tr>"
            table_html += f"<td><strong>{t}</strong></td>"
            table_html += f"<td>{s['Total Return']}%</td>"
            table_html += f"<td>{s['Sharpe Ratio']}</td>"
            table_html += f"<td>{s['Sortino Ratio']}</td>"
            table_html += f"<td>{s['Maximum Drawdown']}%</td>"
            table_html += f"<td>{s['Win Rate']}%</td>"
            table_html += f"<td>{s['Total Trades']}</td>"
            table_html += f"</tr>"

        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # --- Portfolio Equity Curve ---

        st.markdown(
            '<div class="section-header">💰 Portfolio Equity Curves</div>',
            unsafe_allow_html=True
        )

        colors = [
            "#00d2ff", "#7b2ff7", "#ff6bca",
            "#00ff88", "#ffaa00", "#ff4466"
        ]

        fig_port = go.Figure()

        for i, t in enumerate(results.keys()):
            if t in portfolio_df.columns:
                fig_port.add_trace(
                    go.Scatter(
                        x=portfolio_df.index,
                        y=portfolio_df[t],
                        name=t,
                        line=dict(
                            color=colors[i % len(colors)],
                            width=2
                        )
                    )
                )

        if "Portfolio" in portfolio_df.columns:
            fig_port.add_trace(
                go.Scatter(
                    x=portfolio_df.index,
                    y=portfolio_df["Portfolio"],
                    name="Equal-Weight Portfolio",
                    line=dict(
                        color="#ffffff",
                        width=3,
                        dash="dot"
                    )
                )
            )

        fig_port.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Portfolio Value",
            **PLOTLY_LAYOUT
        )

        st.plotly_chart(fig_port, use_container_width=True)

        # --- Per-Ticker Detail Tabs ---

        st.markdown(
            '<div class="section-header">🔍 Individual Ticker Details</div>',
            unsafe_allow_html=True
        )

        tabs = st.tabs(list(results.keys()))

        for tab, (t, r) in zip(tabs, results.items()):

            with tab:
                render_single_result(
                    r["df"], r["stats"], r["trades"], t
                )

    elif st.session_state["bt_mode"] == "single":

        render_single_result(
            st.session_state["bt_df"],
            st.session_state["bt_stats"],
            st.session_state["bt_trades"],
            st.session_state["bt_ticker"]
        )