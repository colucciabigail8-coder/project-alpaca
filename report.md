\# Project Alpaca - Week 2: Strategy Backtesting Report



\## Overview

This report evaluates three algorithmic trading strategies using 5 years of 

historical daily OHLCV data from Alpaca's Market Data API for AAPL and MSFT.

All strategies start with $100,000 initial capital, are long-only, and use 

no leverage.



\## Technical Indicators Used

1\. SMA (Simple Moving Average) - 20 and 50 day periods

2\. EMA (Exponential Moving Average) - 20 day period

3\. MACD (Moving Average Convergence Divergence)

4\. RSI (Relative Strength Index) - 14 day period

5\. Bollinger Bands - 20 day period

6\. ATR (Average True Range) - 14 day period

7\. OBV (On Balance Volume)



\## Strategy Descriptions



\### Strategy 1: Trend Following

Uses MACD and Moving Averages to identify trends.

\- Entry: Buy when MACD > Signal Line AND SMA20 > SMA50

\- Exit: Sell when MACD < Signal Line

\- Intuition: Captures momentum when short term trend is above long term trend



\### Strategy 2: Mean Reversion

Uses RSI and Bollinger Bands to identify oversold/overbought conditions.

\- Entry: Buy when RSI < 30 AND price below lower Bollinger Band

\- Exit: Sell when RSI > 70 AND price above upper Bollinger Band

\- Intuition: Prices tend to revert to their mean after extreme moves



\### Strategy 3: Custom Strategy

Combines trend, momentum, and volume indicators.

\- Entry: Buy when EMA20 > SMA50 AND RSI between 40-60 AND OBV rising

\- Exit: Sell when EMA20 < SMA50 OR RSI > 70

\- Intuition: Confirms trend with momentum and volume to reduce false signals



\## Performance Results



\### AAPL (5 Years)

| Strategy        | Total Return | CAGR  | Volatility | Sharpe | Sortino | Max Drawdown |

|----------------|-------------|-------|------------|--------|---------|--------------|

| Buy \& Hold     | 105.03%     | 15.53%| 27.7%      | 0.66   | 0.96    | -33.43%      |

| Trend Following| 30.06%      | 5.43% | 10.51%     | 0.56   | 0.47    | -14.25%      |

| Mean Reversion | 27.82%      | 5.06% | 22.93%     | 0.33   | 0.36    | -30.21%      |

| Custom Strategy| 2.7%        | 0.54% | 11.94%     | 0.1    | 0.07    | -26.53%      |



\### MSFT (5 Years)

| Strategy        | Total Return | CAGR  | Volatility | Sharpe | Sortino | Max Drawdown |

|----------------|-------------|-------|------------|--------|---------|--------------|

| Buy \& Hold     | 35.63%      | 6.32% | 27%        | 0.36   | 0.52    | -37.56%      |

| Trend Following| -16.09%     | -3.47%| 10.25%     | -0.29  | -0.18   | -23.76%      |

| Mean Reversion | 7.37%       | 1.44% | 20.79%     | 0.17   | 0.17    | -32.02%      |

| Custom Strategy| -8.01%      | -1.66%| 11.41%     | -0.09  | -0.07   | -32.36%      |



\## Discussion of Results



\### Key Findings

1\. Buy \& Hold outperformed all active strategies on both stocks

2\. Trend Following worked well on AAPL but lost money on MSFT

3\. Mean Reversion was the most consistent active strategy across both stocks

4\. Custom Strategy underperformed on both stocks



\### Why Buy \& Hold Won

Both AAPL and MSFT are strong growth stocks that trended upward over 5 years.

Active strategies missed significant portions of the uptrend by being out of 

the market during signal transitions.



\### Limitations

1\. No transaction costs or slippage modeled

2\. Long-only strategies miss shorting opportunities

3\. Strategies use fixed parameters not optimized per stock

4\. Past performance does not guarantee future results



\### Potential Improvements

1\. Add transaction cost modeling

2\. Implement parameter optimization per ticker

3\. Combine strategies into an ensemble approach

4\. Add short selling capability

5\. Include more stocks for diversification

