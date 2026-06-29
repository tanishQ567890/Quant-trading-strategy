import pandas as pd
import yfinance as yf
import numpy as np
from indicators import SMA, EMA, RSI, MACD, BollingerBands, VWAP
from metrics import (sharpe_ratio,sortino_ratio,calmar_ratio,max_drawdown,total_return,buy_hold_return,win_rate,total_trades)

class Backtester:

    def __init__(self, data):
        self.data = data.copy()
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.droplevel(1)

    def calculate_returns(self, df):

        df["Market Return"] = df["Close"].pct_change()

        df["Strategy Return"] = (df["Position"] * df["Market Return"])

        df["Equity Curve"] = (1 + df["Strategy Return"]).cumprod()

        df["Buy & Hold"] = (1 + df["Market Return"]).cumprod()

        return df


    def sma_strategy(self, short_window=20, long_window=50):

        df = self.data.copy()

        df["SMA Short"] = SMA(df, short_window)
        df["SMA Long"] = SMA(df, long_window)

        df["Signal"] = 0

        df.loc[df["SMA Short"] > df["SMA Long"],"Signal"] = 1

        df["Position"] = df["Signal"].shift(1).fillna(0)

        df = self.calculate_returns(df)

        return df


    def ema_strategy(self, short_window=12, long_window=26):

        df = self.data.copy()

        df["EMA Short"] = EMA(df, short_window)
        df["EMA Long"] = EMA(df, long_window)

        df["Signal"] = 0

        df.loc[df["EMA Short"] > df["EMA Long"],"Signal"] = 1

        df["Position"] = df["Signal"].shift(1).fillna(0)

        df = self.calculate_returns(df)

        return df


    def rsi_strategy(self):

        df = self.data.copy()

        df["RSI"] = RSI(df)

        df["Signal"] = np.nan

        buy = df["RSI"] < 30
        sell = df["RSI"] > 70

        df.loc[buy, "Signal"] = 1
        df.loc[sell, "Signal"] = 0

        df["Position"] = df["Signal"].ffill().fillna(0)

        df = self.calculate_returns(df)

        return df


    def macd_strategy(self):

        df = self.data.copy()

        macd, signal, hist = MACD(df)

        df["MACD"] = macd
        df["Signal Line"] = signal
        df["Histogram"] = hist

        df["Signal"] = 0

        df.loc[df["MACD"] > df["Signal Line"],"Signal"] = 1

        df["Position"] = df["Signal"].shift(1).fillna(0)

        df = self.calculate_returns(df)

        return df


    def bollinger_strategy(self, window=20, num_std=2):
        df = self.data.copy()

        upper, middle, lower = BollingerBands(df, window, num_std)

        df["BB Upper"] = upper
        df["BB Middle"] = middle
        df["BB Lower"] = lower

        df["Signal"] = np.nan
        df.loc[df["Close"] < df["BB Lower"], "Signal"] = 1
        df.loc[df["Close"] > df["BB Upper"], "Signal"] = 0

        df["Position"] = df["Signal"].ffill().fillna(0)

        df = self.calculate_returns(df)

        return df


    def vwap_strategy(self):
        
        df = self.data.copy()

        df["VWAP"] = VWAP(df)

        df["Signal"] = 0

        df.loc[df["Close"] > df["VWAP"], "Signal"] = 1

        df["Position"] = df["Signal"].shift(1).fillna(0)

        df = self.calculate_returns(df)

        return df


    def run(self, strategy, **kwargs):

        if strategy == "SMA":
            return self.sma_strategy(**kwargs)

        elif strategy == "EMA":
            return self.ema_strategy(**kwargs)

        elif strategy == "RSI":
            return self.rsi_strategy()

        elif strategy == "MACD":
            return self.macd_strategy()

        elif strategy == "Bollinger Bands":
            return self.bollinger_strategy(**kwargs)

        elif strategy == "VWAP":
            return self.vwap_strategy()

        else:
            raise ValueError("Invalid Strategy")


    def trade_log(self, df):

        trades = []

        position = 0
        entry_price = None
        entry_date = None

        for i in range(len(df)):

            # Buy Signal
            if df["Position"].iloc[i] == 1 and position == 0:

                position = 1
                entry_price = df["Close"].iloc[i]
                entry_date = df.index[i]

            # Sell Signal
            elif df["Position"].iloc[i] == 0 and position == 1:

                exit_price = df["Close"].iloc[i]
                exit_date = df.index[i]

                pnl = exit_price - entry_price
                pct_return = (exit_price - entry_price) / entry_price

                trades.append({
                    "Entry Date": entry_date,
                    "Exit Date": exit_date,
                    "Entry Price": round(entry_price, 2),
                    "Exit Price": round(exit_price, 2),
                    "PnL": round(pnl, 2),
                    "Return %": round(pct_return * 100, 2)
                })

                position = 0

        return pd.DataFrame(trades)


    def performance(self, df):

        return {

            "Total Return":
                round(total_return(df["Equity Curve"]) * 100, 2),

            "Buy & Hold":
                round(buy_hold_return(df["Close"]) * 100, 2),

            "Sharpe Ratio":
                round(sharpe_ratio(df["Strategy Return"]), 2),

            "Sortino Ratio":
                round(sortino_ratio(df["Strategy Return"]), 2),

            "Calmar Ratio":
                round(calmar_ratio(
                    df["Strategy Return"], df["Equity Curve"]
                ), 2),

            "Maximum Drawdown":
                round(max_drawdown(df["Equity Curve"]) * 100, 2),

            "Win Rate":
                round(win_rate(df["Strategy Return"]) * 100, 2),

            "Total Trades":
                total_trades(df["Position"])
        }


    @staticmethod
    def run_portfolio(tickers, strategy, start, end, **kwargs):

        results = {}
        portfolio_curves = {}

        for t in tickers:
            try:
                data = yf.download(
                    t, start=start, end=end,
                    auto_adjust=True, progress=False
                )

                if data.empty:
                    continue

                bt = Backtester(data)
                df = bt.run(strategy, **kwargs)
                stats = bt.performance(df)
                trades = bt.trade_log(df)

                results[t] = {
                    "df": df,
                    "stats": stats,
                    "trades": trades
                }

                portfolio_curves[t] = df["Equity Curve"]
            except Exception as e:
                continue

        # Equal-weight portfolio
        if portfolio_curves:
            portfolio_df = pd.DataFrame(portfolio_curves)
            portfolio_df["Portfolio"] = portfolio_df.mean(axis=1)
        else:
            portfolio_df = pd.DataFrame()

        return results, portfolio_df