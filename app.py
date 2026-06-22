import streamlit as st
import plotly.graph_objects as go
from connector import get_historical_bars
import time
import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

st.title("📈 Mini Market Data Terminal")

# Ticker input
symbol = st.text_input("Enter a ticker symbol:", value="AAPL").upper()

if symbol:
    # Live quote section
    st.subheader("Live Quotes")
    
    try:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = client.get_stock_latest_quote(request)
        q = quote[symbol]
        
        col1, col2 = st.columns(2)
        col1.metric("Bid Price", f"${q.bid_price:.2f}")
        col2.metric("Ask Price", f"${q.ask_price:.2f}")
    except Exception as e:
        st.error(f"Could not fetch quote: {e}")

    if st.button("🔄 Refresh Quotes"):
        st.rerun()

    st.subheader(f"Historical Data for {symbol}")
    
    with st.spinner("Loading historical data..."):
        df = get_historical_bars(symbol, days=30)
        df = df.reset_index()
    
    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])
    
    fig.update_layout(
        title=f"{symbol} - Last 30 Days",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show latest quote info
    st.subheader("Latest Price Info")
    latest = df.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Open", f"${latest['open']:.2f}")
    col2.metric("Close", f"${latest['close']:.2f}")
    col3.metric("Volume", f"{latest['volume']:,.0f}")

    st.subheader("Raw Data")
    st.dataframe(df.tail(10))