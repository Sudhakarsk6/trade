# indicators.py
"""Core technical indicators (O(n) implementations)"""
import pandas as pd
import numpy as np
from typing import Tuple


def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average
    
    Args:
        series: Price series
        span: Number of periods for EMA calculation
        
    Returns:
        pd.Series: EMA values
    """
    if series is None or series.empty:
        raise ValueError("Series cannot be empty")
    if span <= 0:
        raise ValueError("Span must be positive")
    return series.ewm(span=span, adjust=False).mean()


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average
    
    Args:
        series: Price series
        window: Number of periods for SMA calculation
        
    Returns:
        pd.Series: SMA values
    """
    if series is None or series.empty:
        raise ValueError("Series cannot be empty")
    if window <= 0:
        raise ValueError("Window must be positive")
    return series.rolling(window=window).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index
    
    Args:
        series: Price series
        period: RSI period (default: 14)
        
    Returns:
        pd.Series: RSI values (0-100)
    """
    if series is None or series.empty:
        raise ValueError("Series cannot be empty")
    if period <= 0:
        raise ValueError("Period must be positive")
    
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta).clip(lower=0).rolling(window=period).mean()
    rs = gain / (loss.replace(0, np.nan))
    res = 100 - (100 / (1 + rs))
    return res.fillna(50)


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """MACD Indicator
    
    Args:
        series: Price series
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
        
    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    if series is None or series.empty:
        raise ValueError("Series cannot be empty")
    if fast <= 0 or slow <= 0 or signal <= 0:
        raise ValueError("All periods must be positive")
    
    efast = ema(series, fast)
    eslow = ema(series, slow)
    macd_line = efast - eslow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    # Fill NaN values to prevent propagation
    hist = hist.fillna(0)
    return macd_line, signal_line, hist


def bollinger(series: pd.Series, period: int = 20, dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands
    
    Args:
        series: Price series
        period: Period for SMA (default: 20)
        dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        Tuple of (Upper band, Middle band, Lower band)
    """
    if series is None or series.empty:
        raise ValueError("Series cannot be empty")
    if period <= 0:
        raise ValueError("Period must be positive")
    if dev < 0:
        raise ValueError("Deviation must be non-negative")
    
    mid = series.rolling(window=period).mean()
    sd = series.rolling(window=period).std()
    upper = mid + sd * dev
    lower = mid - sd * dev
    return upper, mid, lower


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range
    
    Args:
        df: DataFrame with High, Low, Close columns
        period: ATR period (default: 14)
        
    Returns:
        pd.Series: ATR values
    """
    if df is None or df.empty:
        raise ValueError("DataFrame cannot be empty")
    if period <= 0:
        raise ValueError("Period must be positive")
    
    required_cols = ['High', 'Low', 'Close']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    
    atr_val = tr.rolling(window=period).mean()
    # Fill NaN with forward fill, then back fill as fallback
    atr_val = atr_val.bfill().fillna(tr.mean())
    return atr_val


def support_resistance(df: pd.DataFrame, lookback: int = 50) -> Tuple[float, float]:
    """Calculate support and resistance levels
    
    Args:
        df: DataFrame with High and Low columns
        lookback: Number of periods to look back (default: 50)
        
    Returns:
        Tuple of (Support level, Resistance level)
    """
    if df is None or df.empty:
        raise ValueError("DataFrame cannot be empty")
    if lookback <= 0:
        raise ValueError("Lookback must be positive")
    
    required_cols = ['High', 'Low']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    w = min(len(df), lookback)
    support = float(df['Low'].tail(w).min())
    resistance = float(df['High'].tail(w).max())
    
    # Validate support < resistance
    if support >= resistance:
        # If they're equal or inverted, adjust slightly
        mid = (support + resistance) / 2
        support = mid * 0.98
        resistance = mid * 1.02
    
    return support, resistance


def volume_strength(df: pd.DataFrame, ma_period: int = 20, threshold: float = 1.2) -> str:
    """Assess volume strength
    
    Args:
        df: DataFrame with Volume column
        ma_period: Period for volume moving average (default: 20)
        threshold: Multiplier for strong volume (default: 1.2)
        
    Returns:
        str: 'STRONG', 'NORMAL', or 'WEAK'
    """
    if df is None or df.empty:
        raise ValueError("DataFrame cannot be empty")
    if 'Volume' not in df.columns:
        raise ValueError("Missing Volume column")
    if ma_period <= 0:
        raise ValueError("MA period must be positive")
    if threshold <= 0:
        raise ValueError("Threshold must be positive")
    
    vol = df['Volume']
    avg = vol.tail(ma_period).mean()
    cur = vol.iloc[-1]
    
    # Handle zero or NaN average
    if avg == 0 or pd.isna(avg):
        return 'NORMAL'
    
    if cur > avg * threshold:
        return 'STRONG'
    if cur < avg * 0.8:
        return 'WEAK'
    return 'NORMAL'
