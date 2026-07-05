# test_trade.py
"""Test script to verify all components work correctly"""
import sys
import traceback
from fetcher import fetch
from indicators import ema, rsi, macd, bollinger, atr, support_resistance, volume_strength
from app import score_and_recommend, print_analysis


def test_fetcher():
    """Test 1: Verify data fetching works"""
    print("\n" + "="*70)
    print("TEST 1: Data Fetcher")
    print("="*70)
    try:
        df = fetch("AAPL", period="1mo", interval="1d")
        assert not df.empty, "DataFrame is empty"
        assert 'Close' in df.columns, "Close column missing"
        assert 'Volume' in df.columns, "Volume column missing"
        print(f"✓ Successfully fetched {len(df)} candles for AAPL")
        print(f"✓ Columns present: {list(df.columns)}")
        print(f"✓ Date range: {df.index[0]} to {df.index[-1]}")
        return True
    except Exception as e:
        print(f"✗ Fetcher test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_indicators(df):
    """Test 2: Verify all indicators calculate without errors"""
    print("\n" + "="*70)
    print("TEST 2: Technical Indicators")
    print("="*70)
    try:
        close = df['Close']
        
        # Test EMA
        ema20 = ema(close, 20)
        assert not ema20.empty, "EMA20 is empty"
        print(f"✓ EMA(20): {ema20.iloc[-1]:.2f}")
        
        # Test SMA
        from indicators import sma
        sma50 = sma(close, 50)
        assert not sma50.empty, "SMA50 is empty"
        print(f"✓ SMA(50): {sma50.iloc[-1]:.2f}")
        
        # Test RSI
        rsi14 = rsi(close, 14)
        assert 0 <= rsi14.iloc[-1] <= 100, f"RSI out of range: {rsi14.iloc[-1]}"
        print(f"✓ RSI(14): {rsi14.iloc[-1]:.2f}")
        
        # Test MACD
        macd_line, signal_line, hist = macd(close)
        assert not macd_line.empty, "MACD line is empty"
        print(f"✓ MACD Line: {macd_line.iloc[-1]:.4f}")
        print(f"✓ Signal Line: {signal_line.iloc[-1]:.4f}")
        print(f"✓ Histogram: {hist.iloc[-1]:.4f}")
        
        # Test Bollinger Bands
        bb_upper, bb_mid, bb_lower = bollinger(close)
        assert bb_upper.iloc[-1] > bb_mid.iloc[-1] > bb_lower.iloc[-1], "BB bands invalid"
        print(f"✓ Bollinger Bands: {bb_lower.iloc[-1]:.2f} - {bb_upper.iloc[-1]:.2f}")
        
        # Test ATR
        atr14 = atr(df)
        assert atr14.iloc[-1] > 0, "ATR is zero or negative"
        print(f"✓ ATR(14): {atr14.iloc[-1]:.4f}")
        
        # Test Support/Resistance
        support, resistance = support_resistance(df)
        assert support > 0 and resistance > 0, "S/R levels invalid"
        assert support < resistance, "Support should be less than resistance"
        print(f"✓ Support: {support:.2f}, Resistance: {resistance:.2f}")
        
        # Test Volume Strength
        vol_str = volume_strength(df)
        assert vol_str in ['STRONG', 'NORMAL', 'WEAK'], f"Invalid volume strength: {vol_str}"
        print(f"✓ Volume Strength: {vol_str}")
        
        return True
    except Exception as e:
        print(f"✗ Indicators test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_analysis(df):
    """Test 3: Verify scoring and recommendations work"""
    print("\n" + "="*70)
    print("TEST 3: Analysis & Scoring")
    print("="*70)
    try:
        result = score_and_recommend(df, capital=50000)
        
        # Validate all required keys exist
        required_keys = [
            'symbol', 'price', 'rsi', 'macd_hist', 'ema20', 'ema50',
            'bb_upper', 'bb_lower', 'atr', 'support', 'resistance',
            'volume_strength', 'confidence', 'action', 'reasons',
            'stop_loss', 'target', 'position_size', 'risk_reward'
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        # Validate value ranges
        assert 0 <= result['confidence'] <= 100, "Confidence out of range"
        assert result['action'] in ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'], "Invalid action"
        assert result['position_size'] >= 0, "Position size negative"
        assert result['price'] > 0, "Price invalid"
        
        print(f"✓ Symbol: {result['symbol']}")
        print(f"✓ Price: {result['price']}")
        print(f"✓ Action: {result['action']} (Confidence: {result['confidence']}%)")
        print(f"✓ Stop Loss: {result['stop_loss']}, Target: {result['target']}")
        print(f"✓ Position Size: {result['position_size']}")
        print(f"✓ Risk/Reward: {result['risk_reward']}")
        print(f"✓ Reasons: {len(result['reasons'])} factors analyzed")
        
        return True
    except Exception as e:
        print(f"✗ Analysis test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_output(df):
    """Test 4: Verify formatted output works"""
    print("\n" + "="*70)
    print("TEST 4: Formatted Output")
    print("="*70)
    try:
        result = score_and_recommend(df, capital=50000)
        print("✓ Print analysis function:")
        print_analysis(result)
        return True
    except Exception as e:
        print(f"✗ Output test failed: {str(e)}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = []
    
    # Test 1: Fetcher
    test1_pass = test_fetcher()
    tests.append(("Fetcher", test1_pass))
    
    if not test1_pass:
        print("\n❌ Cannot proceed without data. Stopping tests.")
        return tests
    
    # Get data for remaining tests
    df = fetch("AAPL", period="1mo", interval="1d")
    
    # Test 2: Indicators
    test2_pass = test_indicators(df)
    tests.append(("Indicators", test2_pass))
    
    # Test 3: Analysis
    test3_pass = test_analysis(df)
    tests.append(("Analysis", test3_pass))
    
    # Test 4: Output
    test4_pass = test_output(df)
    tests.append(("Output", test4_pass))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    for test_name, passed in tests:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in tests)
    print("\n" + "="*70)
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("Code is working perfectly!")
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("Please review errors above.")
    print("="*70 + "\n")
    
    return tests


if __name__ == '__main__':
    try:
        tests = run_all_tests()
        all_passed = all(result for _, result in tests)
        sys.exit(0 if all_passed else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
