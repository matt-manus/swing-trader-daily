#!/usr/bin/env python3
"""Compute 14-day RSI for sector ETFs using yfinance"""
import yfinance as yf
import pandas as pd
import json

SECTOR_ETFS = [
    ("XLK", "Technology"),
    ("XLV", "Healthcare"),
    ("XLF", "Financials"),
    ("XLE", "Energy"),
    ("XLI", "Industrials"),
    ("XLY", "Consumer Discret."),
    ("XLP", "Consumer Staples"),
    ("XLU", "Utilities"),
    ("XLB", "Materials"),
    ("XLRE", "Real Estate"),
    ("XLC", "Comm. Services"),
]

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

results = []
for ticker, sector in SECTOR_ETFS:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 15:
            results.append({"ticker": ticker, "sector": sector, "rsi": None, "close": None, "pct_1d": None})
            continue
        close = df["Close"].squeeze()
        rsi_series = compute_rsi(close)
        rsi = round(float(rsi_series.iloc[-1]), 1)
        close_price = round(float(close.iloc[-1]), 2)
        prev_close = round(float(close.iloc[-2]), 2)
        pct_1d = round((close_price - prev_close) / prev_close * 100, 2)
        results.append({"ticker": ticker, "sector": sector, "rsi": rsi, "close": close_price, "pct_1d": pct_1d})
        print(f"{ticker} ({sector}): Close={close_price}, 1D={pct_1d}%, RSI={rsi}")
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        results.append({"ticker": ticker, "sector": sector, "rsi": None, "close": None, "pct_1d": None})

with open("/home/ubuntu/eod_data/sector_rsi.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved to /home/ubuntu/eod_data/sector_rsi.json")
