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
    return series.ewm(span=span, adjust=False).mean()


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average
    
    Args:
        series: Price series
        window: Number of periods for SMA calculation
        
    Returns:
        pd.Series: SMA values
    """
    return series.rolling(window=window).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index
    
    Args:
        series: Price series
        period: RSI period (default: 14)
        
    Returns:
        pd.Series: RSI values (0-100)
    """
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
    efast = ema(series, fast)
    eslow = ema(series, slow)
    macd_line = efast - eslow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
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
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().fillna(tr.mean())


def support_resistance(df: pd.DataFrame, lookback: int = 50) -> Tuple[float, float]:
    """Calculate support and resistance levels
    
    Args:
        df: DataFrame with High and Low columns
        lookback: Number of periods to look back (default: 50)
        
    Returns:
        Tuple of (Support level, Resistance level)
    """
    w = min(len(df), lookback)
    support = float(df['Low'].tail(w).min())
    resistance = float(df['High'].tail(w).max())
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
    vol = df['Volume']
    avg = vol.tail(ma_period).mean()
    cur = vol.iloc[-1]
    
    if cur > avg * threshold:
        return 'STRONG'
    if cur < avg * 0.8:
        return 'WEAK'
    return 'NORMAL'
