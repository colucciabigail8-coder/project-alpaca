import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Connect to Alpaca
client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

def get_historical_bars(symbol, days=30):
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=datetime.now() - timedelta(days=days),
        end=datetime.now()
    )
    bars = client.get_stock_bars(request)
    return bars.df

if __name__ == "__main__":
    df = get_historical_bars("AAPL")
    print(df.tail())