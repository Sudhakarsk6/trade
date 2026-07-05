# fetcher.py
"""Simple data fetcher using yfinance"""
import yfinance as yf


def fetch(symbol: str, period: str = "1y", interval: str = "1d", timeout: int = 15):
    """Fetch OHLCV data for a symbol using yfinance.

    Returns a pandas DataFrame (raises ValueError if no data).
    """
    t = yf.Ticker(symbol)
    df = t.history(period=period, interval=interval, timeout=timeout)
    if df is None or df.empty:
        raise ValueError(f"No data fetched for {symbol}")
    df = df.dropna()
    df.attrs['symbol'] = symbol
    return df
