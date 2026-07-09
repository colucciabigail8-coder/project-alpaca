# Project Alpaca - Mini Market Data Terminal

## Overview
A real-time market data terminal built with Python and Alpaca's paper trading API.

## Features
- Live bid/ask quote display
- 30-day historical candlestick chart
- Real-time data from Alpaca's API
- Simple and clean Streamlit UI

## Setup Instructions
1. Clone this repository
2. Install dependencies:
pip install -r requirements.txt
3. Create a .env file with your Alpaca API keys:
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
4. Run the app:
streamlit run app.py

## Files
- connector.py - Handles Alpaca API connection and historical data
- app.py - Main Streamlit UI application
- streamer.py - Real-time quote streaming module

## Technologies
- Python
- Alpaca API
- Streamlit
- Plotly
- Pandas
## Week 2: Strategy Backtesting Platform

### Features
- 5 years of historical daily OHLCV data from Alpaca
- 7 technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands, ATR, OBV)
- 3 trading strategies (Trend Following, Mean Reversion, Custom)
- Backtesting engine with $100,000 initial capital
- Performance metrics (Total Return, CAGR, Volatility, Sharpe, Sortino, Max Drawdown)
- Equity curve, price chart with signals, and drawdown comparison charts

### New Files
- indicators.py - Technical indicator calculations
- strategies.py - Trading strategy logic
- backtest.py - Backtesting engine and Streamlit UI
- report.md - Full performance analysis report

### How to Run Backtesting
streamlit run backtest.py
## Week 3: Machine Learning Trading Signal

### Features
- Random Forest classifier to predict next day price direction
- 15 features including technical indicators, log returns, rolling statistics
- PCA applied to compress features while keeping 80% of variance
- Paper trading integration with Alpaca API
- Comparison of ML Strategy vs Buy & Hold

### New Files
- ml_strategy.py - Feature engineering, PCA, Random Forest model, backtesting
- ml_app.py - Streamlit UI for ML platform and paper trading

### How to Run
streamlit run ml_app.py

### Results (AAPL)
- ML Strategy Total Return: 22.47%
- ML Strategy Sharpe Ratio: 0.70
- ML Strategy Max Drawdown: -5.6%
- Buy & Hold Total Return: 110.11%
- ML Strategy had significantly lower risk and similar Sharpe ratio

### Paper Trading
- Successfully executed paper trade on Alpaca
- Paper trading only — no real money used
https://drive.google.com/file/d/1-CorXnHgzRK6ynssVW09-DCgv2mMrPgs/view?usp=sharing
