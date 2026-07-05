# indicators.py
"""Core technical indicators (O(n) implementations)"""
import pandas as pd
import numpy as np


def ema(series: pd.Series, span: int):
    return series.ewm(span=span, adjust=False).mean()


def sma(series: pd.Series, window: int):
    return series.rolling(window=window).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta).clip(lower=0).rolling(window=period).mean()
    rs = gain / (loss.replace(0, np.nan))
    res = 100 - (100 / (1 + rs))
    return res.fillna(50)


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    efast = ema(series, fast)
    eslow = ema(series, slow)
    macd_line = efast - eslow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def bollinger(series: pd.Series, period: int = 20, dev: float = 2.0):
    mid = series.rolling(window=period).mean()
    sd = series.rolling(window=period).std()
    return mid + sd * dev, mid, mid - sd * dev


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().fillna(tr.mean())


def support_resistance(df: pd.DataFrame, lookback: int = 50):
    w = min(len(df), lookback)
    return float(df['Low'].tail(w).min()), float(df['High'].tail(w).max())


def volume_strength(df: pd.DataFrame, ma_period: int = 20, threshold: float = 1.2):
    vol = df['Volume']
    avg = vol.tail(ma_period).mean()
    cur = vol.iloc[-1]
    if cur > avg * threshold:
        return 'STRONG'
    if cur < avg * 0.8:
        return 'WEAK'
    return 'NORMAL'
