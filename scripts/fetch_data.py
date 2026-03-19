import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ── Indices ──────────────────────────────────────────────────────────────────
indices = {
    'SPY':  'S&P 500 ETF',
    'QQQ':  'Nasdaq 100 ETF',
    'IWM':  'Russell 2000 ETF',
    'DIA':  'Dow Jones ETF',
}

# ── Sector ETFs ───────────────────────────────────────────────────────────────
sectors = {
    'XLE': 'Energy',
    'XLF': 'Financials',
    'XLK': 'Technology',
    'XLV': 'Health Care',
    'XLI': 'Industrials',
    'XLY': 'Consumer Discret.',
    'XLP': 'Consumer Staples',
    'XLU': 'Utilities',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLC': 'Comm. Services',
}

# ── Macro ─────────────────────────────────────────────────────────────────────
macro = {
    'VIX':  '^VIX',
    'GLD':  'GLD',
    'USO':  'USO',
    'TLT':  'TLT',
    'UUP':  'UUP',
    'TNX':  '^TNX',
}

all_tickers = list(indices.keys()) + list(sectors.keys()) + list(macro.values())
all_tickers = list(set(all_tickers))

print("Fetching data for:", all_tickers)
raw = yf.download(all_tickers, period='1y', auto_adjust=True, progress=False)
close = raw['Close']
print("Data shape:", close.shape)
print("Last date:", close.index[-1].strftime('%Y-%m-%d'))

results = {}

def get_row(ticker):
    if ticker not in close.columns:
        return None
    s = close[ticker].dropna()
    if len(s) < 200:
        print(f"  WARNING: {ticker} only has {len(s)} rows")
    price = s.iloc[-1]
    prev  = s.iloc[-2] if len(s) >= 2 else price
    chg1d = (price - prev) / prev * 100

    ma20  = s.tail(20).mean()  if len(s) >= 20  else None
    ma50  = s.tail(50).mean()  if len(s) >= 50  else None
    ma200 = s.tail(200).mean() if len(s) >= 200 else None

    rsi14 = calc_rsi(s).iloc[-1] if len(s) >= 15 else None

    return {
        'price': round(price, 2),
        'chg1d': round(chg1d, 2),
        'ma20':  round(ma20, 2)  if ma20  else 'N/A',
        'ma50':  round(ma50, 2)  if ma50  else 'N/A',
        'ma200': round(ma200, 2) if ma200 else 'N/A',
        'rsi14': round(rsi14, 1) if rsi14 else 'N/A',
        'vs_ma20':  round((price/ma20 - 1)*100, 2)  if ma20  else 'N/A',
        'vs_ma50':  round((price/ma50 - 1)*100, 2)  if ma50  else 'N/A',
        'vs_ma200': round((price/ma200 - 1)*100, 2) if ma200 else 'N/A',
    }

print("\n=== INDICES ===")
for t, name in indices.items():
    r = get_row(t)
    results[t] = r
    if r:
        print(f"{t} ({name}): ${r['price']} ({r['chg1d']:+.2f}%) | MA20={r['ma20']} MA50={r['ma50']} MA200={r['ma200']} | RSI={r['rsi14']} | vs200={r['vs_ma200']}%")

print("\n=== SECTOR ETFs ===")
for t, name in sectors.items():
    r = get_row(t)
    results[t] = r
    if r:
        print(f"{t} ({name}): ${r['price']} ({r['chg1d']:+.2f}%) | RSI={r['rsi14']} | vs200={r['vs_ma200']}%")

print("\n=== MACRO ===")
for name, t in macro.items():
    r = get_row(t)
    results[name] = r
    if r:
        print(f"{name} ({t}): ${r['price']} ({r['chg1d']:+.2f}%)")

# Save
with open('/home/ubuntu/eod_data/mar19_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nSaved to mar19_data.json")
