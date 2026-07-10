import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up logger
log_filename = f"logs/trading_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_data_update(symbol, price, volume, timestamp):
    """Log incoming market data"""
    logger.info(f"DATA | {symbol} | Price: ${price:.2f} | Volume: {volume:,} | Time: {timestamp}")

def log_signal(symbol, signal, confidence=None):
    """Log trading signals"""
    if confidence:
        logger.info(f"SIGNAL | {symbol} | Signal: {signal} | Confidence: {confidence:.2%}")
    else:
        logger.info(f"SIGNAL | {symbol} | Signal: {signal}")

def log_order(symbol, side, qty, price, order_id=None):
    """Log order submissions"""
    logger.info(f"ORDER | {symbol} | Side: {side} | Qty: {qty} | Price: ${price:.2f} | ID: {order_id}")

def log_fill(symbol, side, qty, fill_price, order_id=None):
    """Log order fills"""
    logger.info(f"FILL | {symbol} | Side: {side} | Qty: {qty} | Fill Price: ${fill_price:.2f} | ID: {order_id}")

def log_pnl(portfolio_value, daily_return, cumulative_return):
    """Log P&L updates"""
    logger.info(f"PNL | Portfolio: ${portfolio_value:,.2f} | Daily Return: {daily_return:.2%} | Cumulative: {cumulative_return:.2%}")

def log_risk_event(event_type, details):
    """Log risk management events"""
    logger.warning(f"RISK | {event_type} | {details}")

def log_error(error_type, details):
    """Log errors"""
    logger.error(f"ERROR | {error_type} | {details}")

if __name__ == "__main__":
    log_data_update("AAPL", 201.50, 54321, datetime.now())
    log_signal("AAPL", "BUY", 0.65)
    log_order("AAPL", "BUY", 10, 201.50, "order123")
    log_pnl(105000, 0.05, 0.05)
    log_risk_event("STOP_LOSS", "AAPL position stopped out at $190.00")
    print(f"Logs saved to {log_filename}")