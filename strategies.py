import pandas as pd
import numpy as np
from indicators import add_all_indicators

def trend_following_strategy(df):
    df = add_all_indicators(df)
    df['Signal'] = 0
    
    # Buy when MACD > Signal and SMA20 > SMA50
    buy = (df['MACD'] > df['MACD_Signal']) & (df['SMA_20'] > df['SMA_50'])
    # Sell when MACD < Signal
    sell = (df['MACD'] < df['MACD_Signal'])
    
    df.loc[buy, 'Signal'] = 1
    df.loc[sell, 'Signal'] = -1
    
    return df

def mean_reversion_strategy(df):
    df = add_all_indicators(df)
    df['Signal'] = 0
    
    # Buy when RSI < 30 and price below lower Bollinger Band
    buy = (df['RSI'] < 30) & (df['close'] < df['BB_Lower'])
    # Sell when RSI > 70 and price above upper Bollinger Band
    sell = (df['RSI'] > 70) & (df['close'] > df['BB_Upper'])
    
    df.loc[buy, 'Signal'] = 1
    df.loc[sell, 'Signal'] = -1
    
    return df

def custom_strategy(df):
    df = add_all_indicators(df)
    df['Signal'] = 0
    
    # Custom: combines trend, momentum, and volume
    # Buy when EMA20 > SMA50, RSI between 40-60, and OBV rising
    buy = (
        (df['EMA_20'] > df['SMA_50']) &
        (df['RSI'] > 40) & (df['RSI'] < 60) &
        (df['OBV'] > df['OBV'].shift(5))
    )
    # Sell when EMA20 < SMA50 or RSI > 70
    sell = (
        (df['EMA_20'] < df['SMA_50']) |
        (df['RSI'] > 70)
    )
    
    df.loc[buy, 'Signal'] = 1
    df.loc[sell, 'Signal'] = -1
    
    return df