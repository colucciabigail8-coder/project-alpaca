# Project Alpaca — Systematic Trading System

## Overview
A complete end-to-end algorithmic trading system built with Python and Alpaca's 
paper trading API. This system includes a live data pipeline, three systematic 
trading strategies, a machine learning signal generator, and a unified dashboard 
for monitoring and control.

**This system uses paper trading only — no real money is used.**

## Architecture
The system is organized into the following modules:

- **data/** — Market data fetching, logging, and storage
- **strategy/** — Trading strategy logic (trend following, mean reversion, custom)
- **execution/** — Order execution and risk management
- **ui/** — Unified Streamlit dashboard
- **config/** — Configuration files

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/yourusername/project-alpaca

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set up environment variables
Copy config/config.env.example to .env and add your Alpaca API keys:
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

### 4. Run the unified dashboard
streamlit run ui/dashboard.py

### 5. Run individual modules
streamlit run app.py          # Week 1: Live market terminal
streamlit run backtest.py     # Week 2: Strategy backtesting
streamlit run ml_app.py       # Week 3: ML trading signal

## Features

### Week 1: Live Market Data Terminal
- Real-time bid/ask quotes from Alpaca
- 30-day historical candlestick chart
- Auto-refreshing live quotes every 5 seconds
https://drive.google.com/file/d/1VKoA-xI4MW1mVA14V6-hyeQU6EswGzIe/view?usp=sharing

### Week 2: Strategy Backtesting Platform
- 5 years of historical daily OHLCV data
- 7 technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands, ATR, OBV)
- 3 trading strategies:
  - Trend Following (MACD + Moving Averages)
  - Mean Reversion (RSI + Bollinger Bands)
  - Custom Strategy (EMA + RSI + OBV)
- Performance metrics: Total Return, CAGR, Sharpe, Sortino, Max Drawdown
https://drive.google.com/file/d/1xf3kmBHdOnhuUffgqopxzqOop85E2-8M/view?usp=sharing

### Week 3: ML Trading Signal
- Random Forest classifier to predict next-day price direction
- 15 features including technical indicators and rolling statistics
- PCA applied to compress features while keeping 80% of variance
- Paper trading integration with Alpaca API
https://drive.google.com/file/d/1-CorXnHgzRK6ynssVW09-DCgv2mMrPgs/view?usp=sharing

### Final: Unified Dashboard
- Live market data with auto-refresh
- Backtest mode with all 3 strategies
- ML strategy mode
- Paper trading mode with position tracking and order execution
- Sidebar risk controls (position size, stop loss, take profit)
- System status showing Alpaca connection

## Trading Strategies

### Strategy 1: Trend Following
- Buy when MACD > Signal Line AND SMA20 > SMA50
- Sell when MACD < Signal Line
- Exploits momentum in trending markets

### Strategy 2: Mean Reversion
- Buy when RSI < 30 AND price below lower Bollinger Band
- Sell when RSI > 70 AND price above upper Bollinger Band
- Exploits price returning to average after extreme moves

### Strategy 3: Custom Strategy
- Buy when EMA20 > SMA50 AND RSI between 40-60 AND OBV rising
- Sell when EMA20 < SMA50 OR RSI > 70
- Combines trend, momentum, and volume confirmation

## Risk Controls
- Max position size: 10% of capital per asset
- Stop loss: 5% per position
- Take profit: 10% per position
- Max drawdown limit: 20%
- Long-only, no leverage

## Performance Results (AAPL, 5 Years)
| Strategy | Total Return | Sharpe Ratio | Max Drawdown |
|----------|-------------|--------------|--------------|
| Buy & Hold | 110.11% | 0.69 | -33.43% |
| Trend Following | 30.06% | 0.56 | -14.25% |
| Mean Reversion | 27.82% | 0.33 | -30.21% |
| Custom Strategy | 2.7% | 0.10 | -26.53% |
| ML Strategy | 22.47% | 0.70 | -5.60% |

## Requirements
See requirements.txt for full list of dependencies.

## Disclaimer
This system is for educational purposes only and uses Alpaca's paper trading 
environment. No real money is used at any point.
https://drive.google.com/file/d/1sXnzHkmlWQdo6uI733qqvGVXkZ5MvH5f/view?usp=sharing
