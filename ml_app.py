import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from ml_strategy import (get_data, engineer_features, train_model,
                          generate_signals, run_ml_backtest, calculate_metrics)

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

st.title("🤖 ML Trading Signal Platform")
st.caption("Paper Trading Only — No Real Money Used")

symbol = st.selectbox("Select a ticker:", ["AAPL", "MSFT", "SPY", "QQQ", "NVDA"])

if "model_ready" not in st.session_state:
    st.session_state.model_ready = False
if "df" not in st.session_state:
    st.session_state.df = None
if "trades" not in st.session_state:
    st.session_state.trades = []
if "accuracy" not in st.session_state:
    st.session_state.accuracy = None
if "cumulative_variance" not in st.session_state:
    st.session_state.cumulative_variance = None

if st.button("Run ML Strategy"):
    with st.spinner("Downloading data..."):
        df = get_data(symbol)
    with st.spinner("Engineering features..."):
        df = engineer_features(df)
    with st.spinner("Training Random Forest model..."):
        model, pca, scaler, features, accuracy, cumulative_variance = train_model(df)
    with st.spinner("Generating signals and running backtest..."):
        df = generate_signals(df, model, pca, scaler, features)
        df, trades = run_ml_backtest(df)

    st.session_state.df = df
    st.session_state.trades = trades
    st.session_state.accuracy = accuracy
    st.session_state.cumulative_variance = cumulative_variance
    st.session_state.model_ready = True
    st.session_state.latest_signal = int(df['ML_Signal'].iloc[-1])
    st.session_state.latest_prob = float(df['ML_Probability'].iloc[-1])

if st.session_state.model_ready:
    df = st.session_state.df
    trades = st.session_state.trades
    accuracy = st.session_state.accuracy
    cumulative_variance = st.session_state.cumulative_variance

    st.success(f"Model trained! Accuracy: {accuracy:.2%}")

    initial_capital = 100000
    shares_bh = int(initial_capital / df['close'].iloc[0])
    df['BH_Portfolio'] = shares_bh * df['close']

    st.subheader("📊 Performance Comparison")
    ml_metrics = calculate_metrics(df['ML_Portfolio'])
    bh_metrics = calculate_metrics(df['BH_Portfolio'])
    metrics_df = pd.DataFrame({
        'Buy & Hold': bh_metrics,
        'ML Strategy': ml_metrics
    })
    st.dataframe(metrics_df)

    if len(trades) > 1:
        buy_trades = [t for t in trades if t['type'] == 'BUY']
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        wins = sum(1 for b, s in zip(buy_trades, sell_trades) if s['price'] > b['price'])
        win_rate = wins / len(sell_trades) * 100 if sell_trades else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
        st.metric("Total Trades", len(trades))

    st.subheader("💰 Equity Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['BH_Portfolio'], name='Buy & Hold'))
    fig.add_trace(go.Scatter(x=df.index, y=df['ML_Portfolio'], name='ML Strategy'))
    fig.update_layout(title=f"{symbol} - Equity Curves",
                      xaxis_title="Date",
                      yaxis_title="Portfolio Value ($)",
                      height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔬 PCA Explained Variance")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=list(range(1, len(cumulative_variance)+1)),
        y=cumulative_variance * 100,
        mode='lines+markers',
        name='Cumulative Variance'
    ))
    fig2.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% threshold")
    fig2.update_layout(title="PCA Cumulative Explained Variance",
                       xaxis_title="Number of Components",
                       yaxis_title="Cumulative Variance (%)",
                       height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📈 Price Chart with ML Signals")
    buys = df[df['ML_Signal'] == 1]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df.index, y=df['close'], name='Price', line=dict(color='blue')))
    fig3.add_trace(go.Scatter(x=buys.index, y=buys['close'], mode='markers',
                              name='Buy Signal', marker=dict(color='green', size=6, symbol='triangle-up')))
    fig3.update_layout(title=f"{symbol} - ML Buy Signals", height=500)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📉 Drawdown Comparison")
    fig4 = go.Figure()
    for label, portfolio in [('Buy & Hold', df['BH_Portfolio']), ('ML Strategy', df['ML_Portfolio'])]:
        rolling_max = portfolio.cummax()
        drawdown = (portfolio - rolling_max) / rolling_max * 100
        fig4.add_trace(go.Scatter(x=df.index, y=drawdown, name=label))
    fig4.update_layout(title="Drawdown Comparison", yaxis_title="Drawdown (%)", height=400)
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("📋 Paper Trading")
    st.info("This is paper trading only — no real money is used")

    latest_signal = st.session_state.latest_signal
    latest_prob = st.session_state.latest_prob

    st.write(f"**Latest Signal:** {'🟢 LONG (Buy)' if latest_signal == 1 else '⚪ FLAT (No Position)'}")
    st.write(f"**Model Confidence:** {latest_prob:.2%}")

    if st.button("Execute Paper Trade"):
        try:
            order = MarketOrderRequest(
                symbol=symbol,
                qty=1,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            result = trading_client.submit_order(order)
            st.success(f"✅ BUY order submitted for 1 share of {symbol}")
            st.write(f"Order ID: {result.id}")
            st.write(f"Status: {result.status}")
        except Exception as e:
            st.error(f"Order failed: {e}")

    if trades:
        st.subheader("📝 Trade Log")
        trades_df = pd.DataFrame(trades)
        st.dataframe(trades_df.tail(20))