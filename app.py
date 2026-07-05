# app.py
"""Compact 3-file stock analyzer using fetcher.py and indicators.py

Usage:
  python app.py RELIANCE.NS --period 1y --interval 1d --capital 50000
"""
import argparse
from fetcher import fetch
from indicators import ema, rsi, macd, bollinger, atr, support_resistance, volume_strength


def score_and_recommend(df, capital: float = 50000):
    close = df['Close']
    price = float(close.iloc[-1])

    # indicators
    r = float(rsi(close).iloc[-1])
    _, _, hist = macd(close)
    hist_cur = float(hist.iloc[-1])
    ema20 = float(ema(close, 20).iloc[-1])
    ema50 = float(ema(close, 50).iloc[-1])
    bb_upper, bb_mid, bb_lower = bollinger(close)
    atrv = float(atr(df).iloc[-1])
    support, resistance = support_resistance(df)
    vol_strength = volume_strength(df)

    # scoring
    score = 50
    reasons = []

    if ema20 > ema50:
        score += 15; reasons.append('Uptrend')
    else:
        score -= 10; reasons.append('Downtrend')

    if hist_cur > 0:
        score += 10; reasons.append('MACD bullish')
    else:
        score -= 8; reasons.append('MACD bearish')

    if r < 30:
        score += 8; reasons.append('RSI oversold')
    elif r > 70:
        score -= 8; reasons.append('RSI overbought')

    if vol_strength == 'STRONG':
        score += 5

    if atrv / max(1.0, price) > 0.03:
        score -= 4; reasons.append('High volatility')

    confidence = max(0, min(100, score))

    if confidence >= 80:
        action = 'STRONG_BUY'
    elif confidence >= 65:
        action = 'BUY'
    elif confidence >= 50:
        action = 'HOLD'
    elif confidence >= 30:
        action = 'SELL'
    else:
        action = 'STRONG_SELL'

    stop = support - 0.5 * atrv if support > 0 else price * 0.95
    target = resistance + 0.5 * atrv if resistance > 0 else price * 1.05
    risk_amount = capital * 0.02
    price_diff = abs(price - stop) if price != stop else 1.0
    position_size = max(0, int(risk_amount / price_diff)) if price_diff > 0 else 0
    rr = (target - price) / (price - stop) if (price - stop) != 0 else None

    return {
        'symbol': df.attrs.get('symbol','N/A'),
        'price': round(price,2),
        'rsi': round(r,2),
        'macd_hist': round(hist_cur,4),
        'ema20': round(ema20,2),
        'ema50': round(ema50,2),
        'atr': round(atrv,4),
        'support': round(support,2),
        'resistance': round(resistance,2),
        'volume_strength': vol_strength,
        'confidence': round(confidence,1),
        'action': action,
        'reasons': reasons,
        'stop_loss': round(stop,2),
        'target': round(target,2),
        'position_size': position_size,
        'risk_reward': round(rr,2) if rr is not None else None,
    }


def run_cli(symbol, period='1y', interval='1d', capital=50000):
    df = fetch(symbol, period=period, interval=interval)
    result = score_and_recommend(df, capital=capital)
    print(f"=== {symbol} ({period} @ {interval}) ===")
    print(f"Price: {result['price']} | Action: {result['action']} ({result['confidence']}%)")
    print(f"Stop: {result['stop_loss']} | Target: {result['target']} | RR: {result['risk_reward']}")
    print(f"Position Size (approx): {result['position_size']} shares")
    print("Indicators: RSI", result['rsi'], "MACD_hist", result['macd_hist'], "ATR", result['atr'])
    print("Reasons:", ", ".join(result['reasons'][:5]))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('symbol')
    p.add_argument('--period', default='1y')
    p.add_argument('--interval', default='1d')
    p.add_argument('--capital', type=float, default=50000.0)
    args = p.parse_args()
    run_cli(args.symbol, period=args.period, interval=args.interval, capital=args.capital)
