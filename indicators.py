import pandas as pd


def SMA(data, window):
    """
    Simple Moving Average
    """
    return data["Close"].rolling(window=window).mean()


def EMA(data, window):
    """
    Exponential Moving Average
    """
    return data["Close"].ewm(span=window, adjust=False).mean()


def RSI(data, window=14):
    """
    Relative Strength Index
    """

    delta = data["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def MACD(data):
    """
    MACD Indicator
    """

    ema12 = EMA(data, 12)
    ema26 = EMA(data, 26)

    macd = ema12 - ema26

    signal = macd.ewm(span=9, adjust=False).mean()

    histogram = macd - signal

    return macd, signal, histogram


def BollingerBands(data, window=20, num_std=2):
    """
    Bollinger Bands
    Returns upper band, middle band (SMA), lower band
    """

    middle = data["Close"].rolling(window=window).mean()

    std = data["Close"].rolling(window=window).std()

    upper = middle + (num_std * std)
    lower = middle - (num_std * std)

    return upper, middle, lower


def VWAP(data):
    """
    Volume Weighted Average Price
    Cumulative VWAP calculated over the entire period.
    """

    typical_price = (
        data["High"] + data["Low"] + data["Close"]
    ) / 3

    cumulative_tp_vol = (typical_price * data["Volume"]).cumsum()
    cumulative_vol = data["Volume"].cumsum()

    vwap = cumulative_tp_vol / cumulative_vol

    return vwap