# app.py
"""Compact 3-file stock analyzer using fetcher.py and indicators.py

Usage:
  python app.py RELIANCE.NS --period 1y --interval 1d --capital 50000
  python app.py AAPL --period 6mo --interval 1d --capital 100000
  python app.py BTC-USD --period 3mo --interval 1h --capital 50000
  python app.py AAPL --period 1d --interval 5m --capital 50000  (Near Real-time)
"""
import argparse
import sys
from typing import Dict, Any
from fetcher import fetch
from indicators import ema, rsi, macd, bollinger, atr, support_resistance, volume_strength


def score_and_recommend(df, capital: float = 50000) -> Dict[str, Any]:
    """Analyze stock data and generate trading recommendation
    
    Args:
        df: OHLCV DataFrame
        capital: Available capital in currency units (default: 50000)
        
    Returns:
        Dictionary with analysis results and trading recommendation
    """
    try:
        close = df['Close']
        price = float(close.iloc[-1])
        
        # Calculate indicators
        r = float(rsi(close).iloc[-1])
        _, _, hist = macd(close)
        hist_cur = float(hist.iloc[-1])
        ema20 = float(ema(close, 20).iloc[-1])
        ema50 = float(ema(close, 50).iloc[-1])
        bb_upper, bb_mid, bb_lower = bollinger(close)
        bb_upper_cur = float(bb_upper.iloc[-1])
        bb_lower_cur = float(bb_lower.iloc[-1])
        atrv = float(atr(df).iloc[-1])
        support, resistance = support_resistance(df)
        vol_strength = volume_strength(df)
        
        # Scoring logic
        score = 50
        reasons = []
        
        # Trend analysis (EMA crossover)
        if ema20 > ema50:
            score += 15
            reasons.append(f"Uptrend (EMA20: {ema20:.2f} > EMA50: {ema50:.2f})")
        else:
            score -= 10
            reasons.append(f"Downtrend (EMA20: {ema20:.2f} < EMA50: {ema50:.2f})")
        
        # MACD analysis
        if hist_cur > 0:
            score += 10
            reasons.append("MACD bullish signal")
        else:
            score -= 8
            reasons.append("MACD bearish signal")
        
        # RSI analysis
        if r < 30:
            score += 8
            reasons.append(f"RSI oversold ({r:.2f})")
        elif r > 70:
            score -= 8
            reasons.append(f"RSI overbought ({r:.2f})")
        else:
            reasons.append(f"RSI neutral ({r:.2f})")
        
        # Volume analysis
        if vol_strength == 'STRONG':
            score += 5
            reasons.append("Strong volume")
        elif vol_strength == 'WEAK':
            score -= 3
            reasons.append("Weak volume")
        
        # Volatility check
        if price > 0 and (atrv / price) > 0.03:
            score -= 4
            reasons.append(f"High volatility (ATR/Price: {(atrv/price):.2%})")
        
        # Bollinger Bands position
        if price < bb_lower_cur:
            score += 5
            reasons.append("Price near lower Bollinger Band")
        elif price > bb_upper_cur:
            score -= 5
            reasons.append("Price near upper Bollinger Band")
        
        # Ensure confidence is between 0-100
        confidence = max(0, min(100, score))
        
        # Action recommendation based on confidence
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
        
        # Risk management calculations
        stop = support - 0.5 * atrv if support > 0 else price * 0.95
        target = resistance + 0.5 * atrv if resistance > 0 else price * 1.05
        
        # Validate stop is below price for longs
        if stop >= price:
            stop = price * 0.95
        
        risk_amount = capital * 0.02
        price_diff = abs(price - stop) if price != stop else 1.0
        position_size = max(0, int(risk_amount / price_diff)) if price_diff > 0 else 0
        
        # Risk-Reward ratio
        rr = (target - price) / (price - stop) if (price - stop) != 0 else None
        
        return {
            'symbol': df.attrs.get('symbol', 'N/A'),
            'price': round(price, 2),
            'rsi': round(r, 2),
            'macd_hist': round(hist_cur, 4),
            'ema20': round(ema20, 2),
            'ema50': round(ema50, 2),
            'bb_upper': round(bb_upper_cur, 2),
            'bb_lower': round(bb_lower_cur, 2),
            'atr': round(atrv, 4),
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'volume_strength': vol_strength,
            'confidence': round(confidence, 1),
            'action': action,
            'reasons': reasons[:6],  # Top 6 reasons
            'stop_loss': round(stop, 2),
            'target': round(target, 2),
            'position_size': position_size,
            'risk_reward': round(rr, 2) if rr is not None else None,
        }
    except Exception as e:
        raise Exception(f"Error in score_and_recommend: {str(e)}")


def print_analysis(result: Dict[str, Any]):
    """Print analysis results in formatted output"""
    print("\n" + "="*70)
    print(f"📊 TRADING ANALYSIS: {result['symbol']}")
    print("="*70)
    
    print(f"\n💰 Price & Action:")
    print(f"   Current Price: {result['price']}")
    print(f"   Recommendation: {result['action']} (Confidence: {result['confidence']}%)")
    
    print(f"\n📈 Risk Management:")
    print(f"   Stop Loss: {result['stop_loss']}")
    print(f"   Target: {result['target']}")
    print(f"   Risk/Reward: {result['risk_reward']}")
    print(f"   Position Size: {result['position_size']} units")
    
    print(f"\n📊 Technical Indicators:")
    print(f"   RSI(14): {result['rsi']} | MACD Hist: {result['macd_hist']}")
    print(f"   EMA(20): {result['ema20']} | EMA(50): {result['ema50']}")
    print(f"   ATR(14): {result['atr']}")
    print(f"   Bollinger Bands: {result['bb_lower']} - {result['bb_upper']}")
    
    print(f"\n🔍 Support & Resistance:")
    print(f"   Support: {result['support']} | Resistance: {result['resistance']}")
    
    print(f"\n📌 Volume & Analysis:")
    print(f"   Volume Strength: {result['volume_strength']}")
    print(f"   Key Reasons:")
    for i, reason in enumerate(result['reasons'], 1):
        print(f"     {i}. {reason}")
    
    print("="*70 + "\n")


def run_cli(symbol: str, period: str = '1y', interval: str = '1d', capital: float = 50000) -> Dict[str, Any]:
    """Run CLI analysis for a symbol
    
    Args:
        symbol: Stock symbol
        period: Data period
        interval: Data interval
        capital: Available capital
        
    Returns:
        Analysis result dictionary
    """
    try:
        print(f"\n🔄 Analyzing {symbol}...")
        df = fetch(symbol, period=period, interval=interval)
        result = score_and_recommend(df, capital=capital)
        print_analysis(result)
        return result
        
    except ValueError as ve:
        print(f"❌ Error: {str(ve)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Stock technical analysis and trading recommendation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py RELIANCE.NS --period 1y --interval 1d --capital 50000
  python app.py AAPL --period 6mo --interval 1d --capital 100000
  python app.py BTC-USD --period 3mo --interval 1h --capital 50000
  python app.py AAPL --period 1d --interval 5m --capital 50000  (Near Real-time Analysis)
        """
    )
    parser.add_argument('symbol', help='Stock symbol (e.g., RELIANCE.NS, AAPL, BTC-USD)')
    parser.add_argument('--period', default='1y', help='Period (default: 1y). Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max')
    parser.add_argument('--interval', default='1d', help='Interval (default: 1d). Options: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo')
    parser.add_argument('--capital', type=float, default=50000.0, help='Available capital (default: 50000)')
    
    args = parser.parse_args()
    run_cli(args.symbol, period=args.period, interval=args.interval, capital=args.capital)
