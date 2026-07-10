import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from strategies import trend_following_strategy, mean_reversion_strategy, custom_strategy

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

def get_historical_data(symbol, years=5):
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=datetime.now() - timedelta(days=years*365),
        end=datetime.now()
    )
    bars = client.get_stock_bars(request)
    df = bars.df.reset_index()
    df = df[df['symbol'] == symbol].copy()
    df = df.set_index('timestamp')
    return df

def run_backtest(df, strategy_func, initial_capital=100000):
    df = strategy_func(df.copy())
    capital = initial_capital
    position = 0
    portfolio_values = []
    trades = []
    for i in range(len(df)):
        row = df.iloc[i]
        price = row['close']
        signal = row['Signal']
        if signal == 1 and position == 0:
            shares = int(capital / price)
            position = shares
            capital -= shares * price
            trades.append({'date': df.index[i], 'type': 'BUY', 'price': price, 'shares': shares})
        elif signal == -1 and position > 0:
            capital += position * price
            trades.append({'date': df.index[i], 'type': 'SELL', 'price': price, 'shares': position})
            position = 0
        portfolio_values.append(capital + position * price)
    df['Portfolio'] = portfolio_values
    return df, trades

def calculate_metrics(df, initial_capital=100000):
    if isinstance(df, pd.DataFrame):
        portfolio = df['Portfolio']
    else:
        portfolio = df
    returns = portfolio.pct_change().dropna()
    total_return = (portfolio.iloc[-1] - initial_capital) / initial_capital * 100
    years = len(portfolio) / 252
    cagr = ((portfolio.iloc[-1] / initial_capital) ** (1/years) - 1) * 100
    volatility = returns.std() * np.sqrt(252) * 100
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    negative_returns = returns[returns < 0]
    sortino = (returns.mean() * 252) / (negative_returns.std() * np.sqrt(252))
    rolling_max = portfolio.cummax()
    drawdown = (portfolio - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    return {
        'Total Return (%)': round(total_return, 2),
        'CAGR (%)': round(cagr, 2),
        'Volatility (%)': round(volatility, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Sortino Ratio': round(sortino, 2),
        'Max Drawdown (%)': round(max_drawdown, 2)
    }

def buy_and_hold(df, initial_capital=100000):
    shares = int(initial_capital / df['close'].iloc[0])
    df['Portfolio'] = shares * df['close']
    return df