import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from indicators import add_all_indicators

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

def get_data(symbol, years=5):
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

def engineer_features(df):
    df = add_all_indicators(df)
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['rolling_mean_10'] = df['close'].rolling(window=10).mean()
    df['rolling_std_10'] = df['close'].rolling(window=10).std()
    df['rolling_mean_20'] = df['close'].rolling(window=20).mean()
    df['rolling_std_20'] = df['close'].rolling(window=20).std()
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df = df.dropna()
    return df

def apply_pca(X_train, X_test, variance_threshold=0.80):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    pca = PCA()
    pca.fit(X_train_scaled)
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumulative_variance >= variance_threshold) + 1
    pca = PCA(n_components=n_components)
    X_train_pca = pca.fit_transform(X_train_scaled)
    X_test_pca = pca.transform(X_test_scaled)
    return X_train_pca, X_test_pca, pca, scaler, cumulative_variance

def train_model(df):
    features = ['SMA_20', 'SMA_50', 'EMA_20', 'MACD', 'MACD_Signal',
                'RSI', 'BB_Upper', 'BB_Lower', 'ATR', 'OBV',
                'log_return', 'rolling_mean_10', 'rolling_std_10',
                'rolling_mean_20', 'rolling_std_20']
    X = df[features]
    y = df['target']
    split = int(len(X) * 0.80)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    X_train_pca, X_test_pca, pca, scaler, cumulative_variance = apply_pca(X_train, X_test)
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_leaf=10,
        random_state=42
    )
    model.fit(X_train_pca, y_train)
    accuracy = model.score(X_test_pca, y_test)
    return model, pca, scaler, features, accuracy, cumulative_variance

def generate_signals(df, model, pca, scaler, features):
    split = int(len(df) * 0.80)
    X = df[features]
    X_scaled = scaler.transform(X)
    X_pca = pca.transform(X_scaled)
    probabilities = model.predict_proba(X_pca)[:, 1]
    signals = (probabilities > 0.5).astype(int)
    signals[:split] = 0
    df['ML_Signal'] = signals
    df['ML_Probability'] = probabilities
    return df

def run_ml_backtest(df, initial_capital=100000):
    capital = initial_capital
    position = 0
    portfolio_values = []
    trades = []
    for i in range(len(df)):
        row = df.iloc[i]
        price = row['close']
        signal = row['ML_Signal']
        if signal == 1 and position == 0:
            shares = int(capital / price)
            if shares > 0:
                position = shares
                capital -= shares * price
                trades.append({
                    'date': df.index[i],
                    'type': 'BUY',
                    'price': price,
                    'shares': shares
                })
        elif signal == 0 and position > 0:
            capital += position * price
            trades.append({
                'date': df.index[i],
                'type': 'SELL',
                'price': price,
                'shares': position
            })
            position = 0
        portfolio_values.append(capital + position * price)
    df['ML_Portfolio'] = portfolio_values
    return df, trades

def calculate_metrics(portfolio, initial_capital=100000):
    returns = portfolio.pct_change().dropna()
    total_return = (portfolio.iloc[-1] - initial_capital) / initial_capital * 100
    years = len(portfolio) / 252
    cagr = ((portfolio.iloc[-1] / initial_capital) ** (1/years) - 1) * 100
    volatility = returns.std() * np.sqrt(252) * 100
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    negative_returns = returns[returns < 0]
    sortino = (returns.mean() * 252) / (negative_returns.std() * np.sqrt(252))
    rolling_max = portfolio.cummax()
    drawdown = (portfolio - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    return {
        'Total Return (%)': round(total_return, 2),
        'CAGR (%)': round(cagr, 2),
        'Volatility (%)': round(volatility, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Sortino Ratio': round(sortino, 2),
        'Max Drawdown (%)': round(max_drawdown, 2)
    }