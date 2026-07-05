# fetcher.py
"""Simple data fetcher using yfinance with error handling"""
import yfinance as yf
import pandas as pd
from typing import Optional


def fetch(symbol: str, period: str = "1y", interval: str = "1d", timeout: int = 15) -> pd.DataFrame:
    """Fetch OHLCV data for a symbol using yfinance.
    
    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE.NS', 'AAPL')
        period (str): Period of data (default: '1y'). Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval (str): Data interval (default: '1d'). Options: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
        timeout (int): API timeout in seconds (default: 15)
    
    Returns:
        pd.DataFrame: OHLCV data with 'symbol' attribute
        
    Raises:
        ValueError: If no data is fetched or symbol is invalid
        Exception: For network/API errors
    """
    try:
        # Validate inputs
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        
        symbol = symbol.strip().upper()
        
        # Validate period and interval
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        valid_intervals = ['1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo']
        
        if period not in valid_periods:
            raise ValueError(f"Invalid period '{period}'. Valid options: {', '.join(valid_periods)}")
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval '{interval}'. Valid options: {', '.join(valid_intervals)}")
        
        print(f"Fetching data for {symbol}...")
        t = yf.Ticker(symbol)
        df = t.history(period=period, interval=interval, timeout=timeout)
        
        if df is None or df.empty:
            raise ValueError(f"No data fetched for {symbol}. Please check the symbol.")
        
        # Remove rows with NaN values
        df = df.dropna()
        
        if df.empty:
            raise ValueError(f"No valid data after removing NaN for {symbol}")
        
        # Validate required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Store symbol in attributes for reference
        df.attrs['symbol'] = symbol
        
        print(f"✓ Fetched {len(df)} candles for {symbol}")
        return df
        
    except ValueError as ve:
        raise ValueError(f"Data fetching error: {str(ve)}")
    except Exception as e:
        raise Exception(f"Failed to fetch data for {symbol}: {str(e)}")
