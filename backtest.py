import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    returns = df['Portfolio'].pct_change().dropna()
    total_return = (df['Portfolio'].iloc[-1] - initial_capital) / initial_capital * 100
    years = len(df) / 252
    cagr = ((df['Portfolio'].iloc[-1] / initial_capital) ** (1/years) - 1) * 100
    volatility = returns.std() * np.sqrt(252) * 100
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    negative_returns = returns[returns < 0]
    sortino = (returns.mean() * 252) / (negative_returns.std() * np.sqrt(252))
    rolling_max = df['Portfolio'].cummax()
    drawdown = (df['Portfolio'] - rolling_max) / rolling_max * 100
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

# Streamlit UI
st.title("📊 Strategy Backtesting Platform")

symbol = st.selectbox("Select a ticker:", ["AAPL", "MSFT", "SPY", "QQQ", "NVDA"])
years = st.slider("Years of historical data:", 1, 5, 5)

if st.button("Run Backtest"):
    with st.spinner("Downloading data and running backtest..."):
        df = get_historical_data(symbol, years)
        
        # Run all strategies
        bh_df = buy_and_hold(df.copy())
        tf_df, tf_trades = run_backtest(df.copy(), trend_following_strategy)
        mr_df, mr_trades = run_backtest(df.copy(), mean_reversion_strategy)
        cs_df, cs_trades = run_backtest(df.copy(), custom_strategy)
        
        # Calculate metrics
        bh_metrics = calculate_metrics(bh_df)
        tf_metrics = calculate_metrics(tf_df)
        mr_metrics = calculate_metrics(mr_df)
        cs_metrics = calculate_metrics(cs_df)
        
        # Performance table
        st.subheader("📈 Performance Comparison")
        metrics_df = pd.DataFrame({
            'Buy & Hold': bh_metrics,
            'Trend Following': tf_metrics,
            'Mean Reversion': mr_metrics,
            'Custom Strategy': cs_metrics
        })
        st.dataframe(metrics_df)
        
        # Equity curve
        st.subheader("💰 Equity Curve")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bh_df.index, y=bh_df['Portfolio'], name='Buy & Hold'))
        fig.add_trace(go.Scatter(x=tf_df.index, y=tf_df['Portfolio'], name='Trend Following'))
        fig.add_trace(go.Scatter(x=mr_df.index, y=mr_df['Portfolio'], name='Mean Reversion'))
        fig.add_trace(go.Scatter(x=cs_df.index, y=cs_df['Portfolio'], name='Custom Strategy'))
        fig.update_layout(title=f"{symbol} - Equity Curves", xaxis_title="Date", yaxis_title="Portfolio Value ($)", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Price chart with signals
        st.subheader("📉 Price Chart with Signals")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=tf_df.index, y=tf_df['close'], name='Price', line=dict(color='blue')))
        fig2.add_trace(go.Scatter(x=tf_df.index, y=tf_df['SMA_20'], name='SMA 20', line=dict(color='orange')))
        fig2.add_trace(go.Scatter(x=tf_df.index, y=tf_df['SMA_50'], name='SMA 50', line=dict(color='red')))
        
        buys = tf_df[tf_df['Signal'] == 1]
        sells = tf_df[tf_df['Signal'] == -1]
        fig2.add_trace(go.Scatter(x=buys.index, y=buys['close'], mode='markers', name='Buy', marker=dict(color='green', size=8, symbol='triangle-up')))
        fig2.add_trace(go.Scatter(x=sells.index, y=sells['close'], mode='markers', name='Sell', marker=dict(color='red', size=8, symbol='triangle-down')))
        fig2.update_layout(title=f"{symbol} - Price & Signals", height=500)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Drawdown chart
        st.subheader("📉 Drawdown Comparison")
        fig3 = go.Figure()
        for label, d in [('Buy & Hold', bh_df), ('Trend Following', tf_df), ('Mean Reversion', mr_df), ('Custom', cs_df)]:
            rolling_max = d['Portfolio'].cummax()
            drawdown = (d['Portfolio'] - rolling_max) / rolling_max * 100
            fig3.add_trace(go.Scatter(x=d.index, y=drawdown, name=label))
        fig3.update_layout(title="Drawdown Comparison", yaxis_title="Drawdown (%)", height=400)
        st.plotly_chart(fig3, use_container_width=True)
        
        st.success(f"Backtest complete! {len(tf_trades)} trades for Trend Following, {len(mr_trades)} for Mean Reversion, {len(cs_trades)} for Custom Strategy.")