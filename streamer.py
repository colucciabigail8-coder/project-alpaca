import os
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

wss_client = StockDataStream(API_KEY, SECRET_KEY)

async def quote_handler(data):
    print(f"Symbol: {data.symbol}")
    print(f"Bid: ${data.bid_price:.2f}")
    print(f"Ask: ${data.ask_price:.2f}")
    print("---")

wss_client.subscribe_quotes(quote_handler, "AAPL")

if __name__ == "__main__":
    wss_client.run()