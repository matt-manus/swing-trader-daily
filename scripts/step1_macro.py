#!/usr/bin/env python3
"""Step 1: Collect macro data for Mar 24, 2026 using yfinance with Wilder's SMMA RSI"""
import yfinance as yf
import json
import numpy as np
from datetime import datetime

def wilder_rsi(prices, period=14):
    """Calculate RSI using Wilder's Smoothed Moving Average (SMMA)"""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Seed with simple average for first period
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    # Apply Wilder's smoothing
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)

def get_ticker_data(ticker, name):
    t = yf.Ticker(ticker)
    hist = t.history(period="1y")
    if hist.empty:
        return None
    
    close = hist['Close']
    price = round(float(close.iloc[-1]), 2)
    prev = round(float(close.iloc[-2]), 2)
    chg_1d = round((price - prev) / prev * 100, 2)
    
    ma20 = round(float(close.rolling(20).mean().iloc[-1]), 2)
    ma50 = round(float(close.rolling(50).mean().iloc[-1]), 2)
    ma200 = round(float(close.rolling(200).mean().iloc[-1]), 2)
    
    vs_20ma = round((price - ma20) / ma20 * 100, 2)
    vs_50ma = round((price - ma50) / ma50 * 100, 2)
    vs_200ma = round((price - ma200) / ma200 * 100, 2)
    
    rsi = wilder_rsi(close.values)
    
    return {
        "name": name,
        "ticker": ticker,
        "price": price,
        "chg_1d": chg_1d,
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "vs_20ma": vs_20ma,
        "vs_50ma": vs_50ma,
        "vs_200ma": vs_200ma,
        "rsi14": rsi
    }

# Tickers to collect
tickers = [
    ("SPY", "SPY (S&P 500)"),
    ("QQQ", "QQQ (Nasdaq 100)"),
    ("IWM", "IWM (Russell 2000)"),
    ("DIA", "DIA (Dow Jones)"),
    ("^VIX", "VIX"),
    ("GLD", "GLD (Gold)"),
    ("USO", "USO (Oil)"),
    ("TLT", "TLT (20Y Treasury)"),
    ("^TNX", "10Y Yield (^TNX)"),
    ("DX-Y.NYB", "DXY (US Dollar)"),
]

results = {}
for ticker, name in tickers:
    print(f"Fetching {ticker}...", end=" ")
    data = get_ticker_data(ticker, name)
    if data:
        results[ticker] = data
        print(f"✓ ${data['price']} ({data['chg_1d']:+.2f}%) RSI={data['rsi14']}")
    else:
        print("✗ FAILED")

# Save
with open('/home/ubuntu/eod_data/step1_macro_mar24.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n=== Step 1 Macro Data Saved ===")
print(f"SPY: ${results['SPY']['price']} ({results['SPY']['chg_1d']:+.2f}%)")
print(f"VIX: {results['^VIX']['price']} ({results['^VIX']['chg_1d']:+.2f}%)")
print(f"DXY: {results['DX-Y.NYB']['price']} ({results['DX-Y.NYB']['chg_1d']:+.2f}%)")
