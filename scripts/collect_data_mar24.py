#!/usr/bin/env python3
"""
Daily Market Data Collector — Mar 24, 2026
Collects Step 1 (yfinance) and Step 1B (Finviz news + OpenAI filter) data
Uses Wilder's SMMA for RSI calculation (not simple rolling mean)
Uses DXY (DX-Y.NYB) not UUP for USD index
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import os
import time

# ─── RSI using Wilder's SMMA ───────────────────────────────────────────────
def calc_rsi_wilder(series, period=14):
    """Calculate RSI using Wilder's Smoothed Moving Average (SMMA/RMA)"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Use EWM with com=period-1 to replicate Wilder's SMMA
    # alpha = 1/period, so com = period - 1
    avg_gain = gain.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ─── Download price data ───────────────────────────────────────────────────
def get_ticker_data(ticker, period="1y"):
    """Download ticker data and compute key metrics"""
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if df.empty or len(df) < 50:
            return None
        
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        close = df['Close'].dropna()
        
        price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2])
        chg_1d = (price - prev_price) / prev_price * 100
        
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        
        vs_20 = (price - ma20) / ma20 * 100
        vs_50 = (price - ma50) / ma50 * 100
        vs_200 = (price - ma200) / ma200 * 100
        
        rsi = float(calc_rsi_wilder(close).iloc[-1])
        
        return {
            'ticker': ticker,
            'price': round(price, 2),
            'chg_1d': round(chg_1d, 2),
            'ma20': round(ma20, 2),
            'ma50': round(ma50, 2),
            'ma200': round(ma200, 2),
            'vs_20ma': round(vs_20, 2),
            'vs_50ma': round(vs_50, 2),
            'vs_200ma': round(vs_200, 2),
            'rsi14': round(rsi, 1)
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# ─── Main indices ──────────────────────────────────────────────────────────
print("=== Fetching main indices ===")
indices = ['SPY', 'QQQ', 'IWM', 'DIA']
index_data = {}
for t in indices:
    d = get_ticker_data(t)
    if d:
        index_data[t] = d
        print(f"{t}: ${d['price']} ({d['chg_1d']:+.2f}%) RSI={d['rsi14']}")
    time.sleep(0.3)

# ─── Macro assets ──────────────────────────────────────────────────────────
print("\n=== Fetching macro assets ===")
macro_tickers = {
    '^VIX': 'VIX',
    'GLD': 'GLD',
    'USO': 'USO',
    'TLT': 'TLT',
    '^TNX': 'TNX',
    'DX-Y.NYB': 'DXY'
}
macro_data = {}
for ticker, label in macro_tickers.items():
    d = get_ticker_data(ticker)
    if d:
        macro_data[label] = d
        print(f"{label}: {d['price']} ({d['chg_1d']:+.2f}%) RSI={d['rsi14']}")
    time.sleep(0.3)

# ─── Sector ETFs ───────────────────────────────────────────────────────────
print("\n=== Fetching sector ETFs ===")
sector_tickers = {
    'XLK': 'Technology',
    'XLE': 'Energy',
    'XLF': 'Financials',
    'XLV': 'Health Care',
    'XLI': 'Industrials',
    'XLP': 'Consumer Staples',
    'XLB': 'Materials',
    'XLU': 'Utilities',
    'XLRE': 'Real Estate',
    'XLY': 'Consumer Discret.',
    'XLC': 'Comm. Services'
}
sector_data = {}
for ticker, sector_name in sector_tickers.items():
    d = get_ticker_data(ticker)
    if d:
        d['sector_name'] = sector_name
        sector_data[ticker] = d
        print(f"{ticker} ({sector_name}): ${d['price']} ({d['chg_1d']:+.2f}%) RSI={d['rsi14']}")
    time.sleep(0.3)

# Sort sectors by RSI descending
sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1]['rsi14'], reverse=True)
print("\n=== Sector ETFs sorted by RSI 14 (descending) ===")
for ticker, d in sorted_sectors:
    print(f"  {ticker}: RSI={d['rsi14']} | {d['chg_1d']:+.2f}%")

# ─── SPY for benchmark ─────────────────────────────────────────────────────
spy_data = index_data.get('SPY', {})

# ─── Determine signal badge ────────────────────────────────────────────────
def get_signal(vs_20, vs_50, vs_200):
    above_20 = vs_20 > 0
    above_50 = vs_50 > 0
    above_200 = vs_200 > 0
    
    if above_20 and above_50 and above_200:
        return "ABOVE ALL MAs", "badge-bull"
    elif not above_20 and not above_50 and not above_200:
        return "BELOW ALL MAs", "badge-bear"
    elif above_200 and not above_20 and not above_50:
        return "BELOW 20/50MA", "badge-warn"
    elif above_200 and above_50 and not above_20:
        return "BELOW 20MA", "badge-warn"
    elif not above_200 and above_20 and above_50:
        return "ABOVE 20/50MA", "badge-warn"
    else:
        return "MIXED", "badge-warn"

# ─── Save all data to JSON ─────────────────────────────────────────────────
output = {
    'report_date': '2026-03-24',
    'indices': index_data,
    'macro': macro_data,
    'sectors': {k: v for k, v in sorted_sectors},
    'sectors_sorted': [k for k, v in sorted_sectors]
}

os.makedirs('/home/ubuntu/eod_data', exist_ok=True)
with open('/home/ubuntu/eod_data/mar24_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n=== Data saved to /home/ubuntu/eod_data/mar24_data.json ===")

# ─── Print summary for verification ───────────────────────────────────────
print("\n=== KEY LEVELS SUMMARY ===")
spy = index_data.get('SPY', {})
print(f"SPY: ${spy.get('price')} | 20MA: ${spy.get('ma20')} | 50MA: ${spy.get('ma50')} | 200MA: ${spy.get('ma200')}")
print(f"SPY vs 20MA: {spy.get('vs_20ma'):+.2f}% | vs 50MA: {spy.get('vs_50ma'):+.2f}% | vs 200MA: {spy.get('vs_200ma'):+.2f}%")
vix = macro_data.get('VIX', {})
print(f"VIX: {vix.get('price')} ({vix.get('chg_1d'):+.2f}%)")
dxy = macro_data.get('DXY', {})
print(f"DXY: {dxy.get('price')} ({dxy.get('chg_1d'):+.2f}%)")
