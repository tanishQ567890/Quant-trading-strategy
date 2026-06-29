import numpy as np


def sharpe_ratio(strategy_returns, risk_free_rate=0):

    strategy_returns = strategy_returns.dropna()

    if strategy_returns.std() == 0:
        return 0

    excess_returns = strategy_returns - (risk_free_rate / 252)

    sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    return sharpe


def sortino_ratio(strategy_returns, risk_free_rate=0):
    strategy_returns = strategy_returns.dropna()

    excess_returns = strategy_returns - (risk_free_rate / 252)

    downside = excess_returns[excess_returns < 0]

    if len(downside) == 0 or downside.std() == 0:
        return 0

    sortino = np.sqrt(252) * excess_returns.mean() / downside.std()

    return sortino


def calmar_ratio(strategy_returns, equity_curve):
    """
    Calmar Ratio — annualized return / max drawdown.
    """

    strategy_returns = strategy_returns.dropna()

    if len(strategy_returns) == 0:
        return 0

    annualized = strategy_returns.mean() * 252

    mdd = max_drawdown(equity_curve)

    if mdd == 0:
        return 0

    return annualized / abs(mdd)


def max_drawdown(equity_curve):

    rolling_max = equity_curve.cummax()

    drawdown = (equity_curve - rolling_max) / rolling_max

    return drawdown.min()


def total_return(equity_curve):

    equity_curve = equity_curve.dropna()

    if len(equity_curve) == 0:
        return 0

    return equity_curve.iloc[-1] - 1


def buy_hold_return(close):

    close = close.dropna()

    if len(close) < 2:
        return 0

    return close.iloc[-1] / close.iloc[0] - 1


def win_rate(strategy_returns):

    strategy_returns = strategy_returns.dropna()

    trades = strategy_returns[strategy_returns != 0]

    if len(trades) == 0:
        return 0

    wins = trades[trades > 0]

    return len(wins) / len(trades)


def total_trades(position):

    position_change = position.diff().fillna(0)

    return int((position_change != 0).sum())