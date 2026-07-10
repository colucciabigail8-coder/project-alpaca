import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import sys
import time
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

from connector import get_historical_bars
from backtest import get_historical_data, run_backtest, calculate_metrics, buy_and_hold
from strategies import trend_following_strategy, mean_reversion_strategy, custom_strategy
from ml_strategy import get_data, engineer_features, train_model, generate_signals, run_ml_backtest

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

st.set_page_config(
    page_title="Project Alpaca Trading System",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Project Alpaca — Systematic Trading System")
st.caption("Paper Trading Only — No Real Money Used")

# Sidebar
st.sidebar.title("⚙️ System Controls")
mode = st.sidebar.selectbox("Mode", ["Live Market Data", "Backtest", "ML Strategy", "Paper Trading"])
symbol = st.sidebar.selectbox("Ticker", ["AAPL", "MSFT", "SPY", "QQQ", "NVDA"])
initial_capital = st.sidebar.number_input("Initial Capital ($)", value=100000, step=10000)

st.sidebar.subheader("Risk Controls")
max_position = st.sidebar.slider("Max Position Size (%)", 1, 100, 10)
stop_loss = st.sidebar.slider("Stop Loss (%)", 1, 20, 5)
take_profit = st.sidebar.slider("Take Profit (%)", 1, 50, 10)

st.sidebar.subheader("System Status")
try:
    account = trading_client.get_account()
    st.sidebar.success("🟢 Connected to Alpaca")
    st.sidebar.write(f"Buying Power: ${float(account.buying_power):,.2f}")
    st.sidebar.write(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    st.sidebar.write("Mode: Paper Trading")
except:
    st.sidebar.error("🔴 Disconnected")

# Main content
if mode == "Live Market Data":
    st.header("📡 Live Market Data")

    try:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = data_client.get_stock_latest_quote(request)
        q = quote[symbol]

        col1, col2, col3 = st.columns(3)
        col1.metric("Bid Price", f"${q.bid_price:.2f}")
        col2.metric("Ask Price", f"${q.ask_price:.2f}")
        col3.metric("Spread", f"${(q.ask_price - q.bid_price):.2f}")
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        st.error(f"Could not fetch live quote: {e}")

    st.subheader(f"Historical Data — {symbol}")
    with st.spinner("Loading chart..."):
        df = get_historical_bars(symbol, days=30)
        df = df.reset_index()

    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])
    fig.update_layout(title=f"{symbol} — Last 30 Days", height=500)
    st.plotly_chart(fig, use_container_width=True)

    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Open", f"${latest['open']:.2f}")
    col2.metric("Close", f"${latest['close']:.2f}")
    col3.metric("Volume", f"{latest['volume']:,.0f}")

    time.sleep(5)
    st.rerun()

elif mode == "Backtest":
    st.header("📊 Strategy Backtesting")
    years = st.slider("Years of historical data:", 1, 5, 5)

    if st.button("▶️ Run Backtest"):
        with st.spinner("Running backtest..."):
            df = get_historical_data(symbol, years)
            bh_df = buy_and_hold(df.copy(), initial_capital)
            tf_df, tf_trades = run_backtest(df.copy(), trend_following_strategy, initial_capital)
            mr_df, mr_trades = run_backtest(df.copy(), mean_reversion_strategy, initial_capital)
            cs_df, cs_trades = run_backtest(df.copy(), custom_strategy, initial_capital)

        st.subheader("Performance Comparison")
        metrics_df = pd.DataFrame({
            'Buy & Hold': calculate_metrics(bh_df),
            'Trend Following': calculate_metrics(tf_df),
            'Mean Reversion': calculate_metrics(mr_df),
            'Custom Strategy': calculate_metrics(cs_df)
        })
        st.dataframe(metrics_df)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bh_df.index, y=bh_df['Portfolio'], name='Buy & Hold'))
        fig.add_trace(go.Scatter(x=tf_df.index, y=tf_df['Portfolio'], name='Trend Following'))
        fig.add_trace(go.Scatter(x=mr_df.index, y=mr_df['Portfolio'], name='Mean Reversion'))
        fig.add_trace(go.Scatter(x=cs_df.index, y=cs_df['Portfolio'], name='Custom Strategy'))
        fig.update_layout(title=f"{symbol} — Equity Curves", height=500)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        for label, d in [('Buy & Hold', bh_df), ('Trend Following', tf_df),
                         ('Mean Reversion', mr_df), ('Custom', cs_df)]:
            rolling_max = d['Portfolio'].cummax()
            drawdown = (d['Portfolio'] - rolling_max) / rolling_max * 100
            fig2.add_trace(go.Scatter(x=d.index, y=drawdown, name=label))
        fig2.update_layout(title="Drawdown Comparison", height=400)
        st.plotly_chart(fig2, use_container_width=True)

elif mode == "ML Strategy":
    st.header("🤖 ML Trading Signal")

    if st.button("▶️ Run ML Strategy"):
        with st.spinner("Training model..."):
            df = get_data(symbol)
            df = engineer_features(df)
            model, pca, scaler, features, accuracy, cumulative_variance = train_model(df)
            df = generate_signals(df, model, pca, scaler, features)
            df, trades = run_ml_backtest(df, initial_capital)

        st.success(f"Model trained! Accuracy: {accuracy:.2%}")

        shares_bh = int(initial_capital / df['close'].iloc[0])
        df['BH_Portfolio'] = shares_bh * df['close']

        metrics_df = pd.DataFrame({
            'Buy & Hold': calculate_metrics(df['BH_Portfolio'], initial_capital),
            'ML Strategy': calculate_metrics(df['ML_Portfolio'], initial_capital)
        })
        st.dataframe(metrics_df)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['BH_Portfolio'], name='Buy & Hold'))
        fig.add_trace(go.Scatter(x=df.index, y=df['ML_Portfolio'], name='ML Strategy'))
        fig.update_layout(title=f"{symbol} — Equity Curves", height=500)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=list(range(1, len(cumulative_variance)+1)),
            y=cumulative_variance * 100,
            mode='lines+markers'
        ))
        fig2.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% threshold")
        fig2.update_layout(title="PCA Explained Variance", height=400)
        st.plotly_chart(fig2, use_container_width=True)

elif mode == "Paper Trading":
    st.header("🏦 Paper Trading")
    st.info("This is paper trading only — no real money is used")

    try:
        account = trading_client.get_account()
        col1, col2, col3 = st.columns(3)
        col1.metric("Portfolio Value", f"${float(account.portfolio_value):,.2f}")
        col2.metric("Buying Power", f"${float(account.buying_power):,.2f}")
        col3.metric("Cash", f"${float(account.cash):,.2f}")
    except Exception as e:
        st.error(f"Could not fetch account info: {e}")

    st.subheader("Current Positions")
    try:
        positions = trading_client.get_all_positions()
        if positions:
            pos_data = [{
                'Symbol': p.symbol,
                'Qty': p.qty,
                'Entry Price': f"${float(p.avg_entry_price):.2f}",
                'Current Price': f"${float(p.current_price):.2f}",
                'P&L': f"${float(p.unrealized_pl):.2f}",
                'P&L %': f"{float(p.unrealized_plpc)*100:.2f}%"
            } for p in positions]
            st.dataframe(pd.DataFrame(pos_data))
        else:
            st.write("No open positions")
    except Exception as e:
        st.error(f"Could not fetch positions: {e}")

    st.subheader("Recent Orders")
    try:
        orders = trading_client.get_orders()
        if orders:
            order_data = [{
                'Symbol': o.symbol,
                'Side': o.side,
                'Qty': o.qty,
                'Type': o.type,
                'Status': o.status,
                'Submitted': o.submitted_at
            } for o in orders[:10]]
            st.dataframe(pd.DataFrame(order_data))
        else:
            st.write("No recent orders")
    except Exception as e:
        st.error(f"Could not fetch orders: {e}")

    st.subheader("Execute Trade")
    col1, col2, col3 = st.columns(3)
    trade_symbol = col1.text_input("Symbol", value=symbol)
    trade_qty = col2.number_input("Quantity", min_value=1, value=1)
    trade_side = col3.selectbox("Side", ["BUY", "SELL"])

    if st.button("🚀 Submit Paper Trade"):
        try:
            side = OrderSide.BUY if trade_side == "BUY" else OrderSide.SELL
            order = MarketOrderRequest(
                symbol=trade_symbol,
                qty=trade_qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            result = trading_client.submit_order(order)
            st.success(f"✅ {trade_side} order submitted for {trade_qty} share(s) of {trade_symbol}")
            st.write(f"Order ID: {result.id}")
            st.write(f"Status: {result.status}")
        except Exception as e:
            st.error(f"Order failed: {e}")