import os
from dotenv import load_dotenv

load_dotenv()

# Risk limits
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", 0.1))
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.05))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.10))
MAX_DRAWDOWN_LIMIT = float(os.getenv("MAX_DRAWDOWN_LIMIT", 0.20))
MAX_LEVERAGE = float(os.getenv("MAX_LEVERAGE", 1.0))

def check_position_size(capital, price, max_position_pct=MAX_POSITION_SIZE):
    """Make sure we never put more than max_position_pct of capital in one stock"""
    max_dollars = capital * max_position_pct
    max_shares = int(max_dollars / price)
    return max_shares

def check_stop_loss(entry_price, current_price, stop_loss_pct=STOP_LOSS_PCT):
    """Return True if we should stop out of position"""
    loss_pct = (current_price - entry_price) / entry_price
    if loss_pct <= -stop_loss_pct:
        return True
    return False

def check_take_profit(entry_price, current_price, take_profit_pct=TAKE_PROFIT_PCT):
    """Return True if we should take profit"""
    gain_pct = (current_price - entry_price) / entry_price
    if gain_pct >= take_profit_pct:
        return True
    return False

def check_max_drawdown(peak_value, current_value, max_drawdown=MAX_DRAWDOWN_LIMIT):
    """Return True if drawdown exceeds limit — stop trading"""
    drawdown = (current_value - peak_value) / peak_value
    if drawdown <= -max_drawdown:
        return True
    return False

def check_leverage(total_exposure, total_capital, max_leverage=MAX_LEVERAGE):
    """Make sure we never exceed max leverage"""
    leverage = total_exposure / total_capital
    if leverage > max_leverage:
        return False
    return True

def calculate_position_size(capital, price, signal_strength=1.0):
    """Calculate how many shares to buy based on capital and risk limits"""
    max_shares = check_position_size(capital, price)
    adjusted_shares = int(max_shares * signal_strength)
    return max(1, adjusted_shares)

if __name__ == "__main__":
    print("Risk Management Module")
    print(f"Max Position Size: {MAX_POSITION_SIZE*100}%")
    print(f"Stop Loss: {STOP_LOSS_PCT*100}%")
    print(f"Take Profit: {TAKE_PROFIT_PCT*100}%")
    print(f"Max Drawdown Limit: {MAX_DRAWDOWN_LIMIT*100}%")
    print(f"Max Leverage: {MAX_LEVERAGE}x")