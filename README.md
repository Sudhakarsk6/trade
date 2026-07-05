# README.md

# 📈 Stock Trading Analysis Tool (sktrade)

A compact, high-performance Python stock analysis tool using technical indicators for real-time and historical trading analysis.

## ✨ Features

- **Real-time Analysis**: Supports 1-minute to monthly intervals for various timeframes
- **Technical Indicators**: EMA, SMA, RSI, MACD, Bollinger Bands, ATR
- **Support & Resistance**: Automatic level detection
- **Risk Management**: Position sizing, stop-loss, and take-profit calculations
- **Trading Recommendations**: Confidence-based BUY/SELL/HOLD signals
- **Volume Analysis**: Strong/Normal/Weak volume assessment
- **Risk-Reward Ratios**: Calculated for every trade setup

## 📋 Architecture

```
sktrade/
├── app.py              # Main CLI & analysis engine
├── fetcher.py          # yfinance data fetcher with error handling
├── indicators.py       # Technical indicators (7 functions)
├── requirements.txt    # Python dependencies
└── README.md          # Documentation (this file)
```

### Core Components

| File | Purpose | Functions |
|------|---------|-----------|
| **fetcher.py** | Data retrieval | `fetch()` - Get OHLCV data from yfinance |
| **indicators.py** | Technical analysis | `ema()`, `sma()`, `rsi()`, `macd()`, `bollinger()`, `atr()`, `support_resistance()`, `volume_strength()` |
| **app.py** | Analysis & CLI | `score_and_recommend()`, `print_analysis()`, `run_cli()` |

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sudhakarsk6/trade.git
   cd trade
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

```bash
# Daily analysis with 1-year history (default)
python app.py RELIANCE.NS

# Specify period and capital
python app.py AAPL --period 6mo --capital 100000

# Cryptocurrency with hourly intervals
python app.py BTC-USD --period 3mo --interval 1h
```

### Real-time Analysis Examples

```bash
# 5-minute intervals (near real-time)
python app.py AAPL --period 1d --interval 5m

# 1-minute candles (intraday)
python app.py NIFTY50.NS --period 1d --interval 1m

# 15-minute intervals
python app.py BTC-USD --period 5d --interval 15m
```

### Advanced Usage

```bash
# High-capital position sizing
python app.py TSLA --period 1y --interval 1d --capital 500000

# Multiple timeframe analysis (run separately)
python app.py RELIANCE.NS --period 1mo --interval 1h --capital 50000
python app.py RELIANCE.NS --period 1d --interval 5m --capital 50000
```

## 📊 Output Example

```
======================================================================
📊 TRADING ANALYSIS: AAPL
======================================================================

💰 Price & Action:
   Current Price: 185.42
   Recommendation: BUY (Confidence: 72.5%)

📈 Risk Management:
   Stop Loss: 180.15
   Target: 192.30
   Risk/Reward: 2.15
   Position Size: 54 units

📊 Technical Indicators:
   RSI(14): 45.32 | MACD Hist: 0.0245
   EMA(20): 184.56 | EMA(50): 183.20
   ATR(14): 2.85
   Bollinger Bands: 175.20 - 195.60

🔍 Support & Resistance:
   Support: 180.50 | Resistance: 190.80

📌 Volume & Analysis:
   Volume Strength: STRONG
   Key Reasons:
     1. Uptrend (EMA20: 184.56 > EMA50: 183.20)
     2. MACD bullish signal
     3. Strong volume
     4. RSI neutral (45.32)
======================================================================
```

## 🔄 Real-time vs Historical Analysis

### Real-time Analysis (≤ 5 minutes)
Use for **intraday trading, scalping, and quick decisions**:
```bash
python app.py AAPL --period 1d --interval 1m    # 1-minute candles
python app.py AAPL --period 1d --interval 5m    # 5-minute candles
python app.py AAPL --period 5d --interval 15m   # 15-minute candles
```

### Historical Analysis (Daily/Weekly)
Use for **swing trading, position trading, long-term investing**:
```bash
python app.py AAPL --period 1y --interval 1d    # Daily candles
python app.py AAPL --period 5y --interval 1wk   # Weekly candles
python app.py AAPL --period 10y --interval 1mo  # Monthly candles
```

## 📋 Command-line Arguments

```
usage: app.py [-h] [--period PERIOD] [--interval INTERVAL] [--capital CAPITAL] symbol

positional arguments:
  symbol                Stock symbol (e.g., RELIANCE.NS, AAPL, BTC-USD)

optional arguments:
  -h, --help            Show help message
  --period PERIOD       Period (default: 1y)
                        Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
  --interval INTERVAL   Interval (default: 1d)
                        Options: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
  --capital CAPITAL     Available capital (default: 50000)
```

## 🎯 Analysis Scoring System

The tool scores opportunities based on multiple factors:

| Factor | Weight | Condition |
|--------|--------|-----------|
| **Trend (EMA)** | ±15 | EMA20 > EMA50 = Bull; < = Bear |
| **MACD** | ±10 | Positive histogram = Bull; Negative = Bear |
| **RSI** | ±8 | <30 = Oversold (Buy); >70 = Overbought (Sell) |
| **Volume** | ±5 | Current > 1.2x avg = Strong |
| **Volatility** | ±4 | ATR/Price > 3% = High (Risky) |
| **Bollinger Bands** | ±5 | Price near bands = Extreme |
| **Base Score** | 50 | Starting point |

**Confidence Score**: Final score clamped between 0-100

**Trading Action**:
- **80+%**: STRONG_BUY
- **65-79%**: BUY
- **50-64%**: HOLD
- **30-49%**: SELL
- **<30%**: STRONG_SELL

## ⚙️ Technical Indicators Explained

### EMA (Exponential Moving Average)
- **Purpose**: Trend identification
- **Default**: 20 & 50 periods
- **Signal**: Crossover indicates trend change

### RSI (Relative Strength Index)
- **Purpose**: Overbought/Oversold detection
- **Range**: 0-100
- **Signals**: <30 (Oversold), >70 (Overbought)

### MACD (Moving Average Convergence Divergence)
- **Purpose**: Trend & momentum
- **Signal**: Histogram crossing zero = Trend change

### Bollinger Bands
- **Purpose**: Volatility & Support/Resistance
- **Calculation**: SMA ± (2 × Standard Deviation)

### ATR (Average True Range)
- **Purpose**: Volatility measurement
- **Use**: Stop-loss and take-profit placement

## 💡 Trading Tips

1. **Confirm signals across multiple timeframes** before trading
2. **Always use stop-losses** - Never risk more than 2% per trade
3. **Watch volume** - Strong moves have strong volume
4. **RSI oversold ≠ automatic buy** - Confirm with other indicators
5. **Test on historical data first** before live trading

## ⚠️ Risk Disclaimer

**This tool is for educational purposes only. Use at your own risk.**

- Past performance does not guarantee future results
- Always do your own research
- Use proper risk management
- Never trade with money you can't afford to lose
- Consider consulting a financial advisor

## 🐛 Error Handling

The tool includes robust error handling for:
- Invalid symbols
- Network timeouts
- Missing or corrupt data
- API rate limits
- Invalid parameters

## 📦 Dependencies

```
yfinance>=0.2.28    # Real-time market data
pandas>=1.5.0       # Data manipulation
numpy>=1.23.0       # Numerical operations
```

## 🔗 Data Source

All market data comes from **Yahoo Finance** via the `yfinance` library. The tool fetches:
- Open, High, Low, Close prices
- Trading volume
- Adjusted close prices (when available)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional indicators (Stochastic, Williams %R, etc.)
- Alert system integration
- Multiple symbol analysis
- Machine learning predictions
- Web UI/Dashboard

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Sudhakar SK**  
GitHub: [@Sudhakarsk6](https://github.com/Sudhakarsk6)

## 📞 Support

For issues, questions, or suggestions:
1. Check existing [GitHub Issues](https://github.com/Sudhakarsk6/trade/issues)
2. Create a new issue with detailed description
3. Include symbol, period, interval, and error message

## 🗓️ Changelog

### v1.0.0 (2026-07-05)
- ✅ Initial release
- ✅ Core 7 technical indicators
- ✅ Real-time & historical analysis
- ✅ Risk management calculations
- ✅ Comprehensive error handling
- ✅ Complete documentation

---

**Happy Trading! 📈**
