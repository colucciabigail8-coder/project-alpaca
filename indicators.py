import pandas as pd
import numpy as np

def add_sma(df, period=20):
    df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
    return df

def add_ema(df, period=20):
    df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def add_macd(df):
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df

def add_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def add_bollinger_bands(df, period=20):
    df['BB_Mid'] = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df['BB_Upper'] = df['BB_Mid'] + (2 * std)
    df['BB_Lower'] = df['BB_Mid'] - (2 * std)
    return df

def add_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=period).mean()
    return df

def add_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df

def add_all_indicators(df):
    df = add_sma(df, 20)
    df = add_sma(df, 50)
    df = add_ema(df, 20)
    df = add_macd(df)
    df = add_rsi(df)
    df = add_bollinger_bands(df)
    df = add_atr(df)
    df = add_obv(df)
    return df