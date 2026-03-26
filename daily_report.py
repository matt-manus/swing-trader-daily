"""
daily_report.py — Swing Trader Daily Market Summary
====================================================
Single script that generates the complete daily report.

Usage:
    python3 daily_report.py [YYYY-MM-DD]
    If no date given, uses today (HKT).

Screenshots are saved to images/{DATE}/ and referenced as relative paths.
No external CDN required — works in GitHub Actions.

IMPORTANT: This script is the single source of truth for report generation.
Every change to MASTER_INSTRUCTION.md or WORKFLOW.md MUST be reflected here.
"""

import os, sys, json, re, time, subprocess, io, csv
from openai import OpenAI
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO = Path(__file__).parent.resolve()
EOD  = Path('/tmp/eod_data')
EOD.mkdir(exist_ok=True)

# ── Date / Time ────────────────────────────────────────────────────────────────
try:
    import pytz
    HKT = pytz.timezone('Asia/Hong_Kong')
    ET  = pytz.timezone('America/New_York')
    now_hkt = datetime.now(HKT)
    now_et  = datetime.now(ET)
except ImportError:
    HKT_OFFSET = timezone(timedelta(hours=8))
    now_hkt = datetime.now(HKT_OFFSET)
    now_et  = datetime.now(timezone(timedelta(hours=-4)))

if len(sys.argv) > 1:
    REPORT_DATE = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
else:
    REPORT_DATE = now_hkt.date()

DATE        = REPORT_DATE.strftime('%Y-%m-%d')
DATE_DISP   = REPORT_DATE.strftime('%a %b %-d, %Y')
DATE_SHORT  = REPORT_DATE.strftime('%b %-d, %Y')
DATE_MMDD   = REPORT_DATE.strftime('%b %-d')
REPORT_TIME = f"{now_hkt.strftime('%H:%M')} HKT / {now_et.strftime('%H:%M')} ET"

# Image folder for this date (relative to repo root)
IMG_DIR = REPO / 'images' / DATE
IMG_DIR.mkdir(parents=True, exist_ok=True)

print(f"=== Daily Report: {DATE} ===")
print(f"    Time: {REPORT_TIME}")
print(f"    Images: images/{DATE}/")

# ── Placeholder dict ───────────────────────────────────────────────────────────
P = {
    'REPORT_DATE':         DATE,
    'REPORT_DATE_DISPLAY': DATE_DISP,
    'REPORT_DATE_SHORT':   DATE_SHORT,
    'REPORT_DATE_MMDD':    DATE_MMDD,
    'REPORT_TIME':         REPORT_TIME,
    'SCREENSHOT_DATE':     DATE_SHORT,
}

def img_path(name):
    """Return relative path for HTML src attribute"""
    return f"images/{DATE}/{name}"

# ── Helper: run Playwright script ──────────────────────────────────────────────
def run_playwright(script_content, timeout=120):
    path = '/tmp/pw_script.py'
    with open(path, 'w') as f:
        f.write(script_content)
    r = subprocess.run(['python3', path], capture_output=True, text=True, timeout=timeout)
    return r.returncode == 0, r.stdout, r.stderr

# ── Helper: color/badge logic ──────────────────────────────────────────────────
def chg_color(v):
    return 'green' if float(v) >= 0 else 'red'

def fmt(v, decimals=2):
    v = float(v)
    sign = '+' if v >= 0 else ''
    return f"{sign}{v:.{decimals}f}"

def breadth_signal(val_str):
    """Return (color_class, badge_class, signal_text) for a breadth % value string."""
    try:
        v = float(str(val_str).replace('%',''))
    except:
        return 'yellow', 'badge-neutral', 'N/A'
    if v >= 70:
        return 'green', 'badge-bull', 'BULLISH'
    elif v >= 50:
        return 'green', 'badge-bull', 'ABOVE AVERAGE'
    elif v >= 30:
        return 'yellow', 'badge-warn', 'BELOW AVERAGE'
    elif v >= 15:
        return 'red', 'badge-bear', 'BEARISH'
    else:
        return 'red', 'badge-bear', 'EXTREME BEARISH'

def vix_badge(vix_price):
    if vix_price >= 30:
        return 'badge-bear', 'EXTREME FEAR (>30)'
    elif vix_price >= 20:
        return 'badge-warn', 'ELEVATED (>20)'
    else:
        return 'badge-bull', 'CALM (<20)'

def fg_badge(score):
    if score <= 25:
        return 'red', 'badge-bear', 'EXTREME FEAR'
    elif score <= 45:
        return 'red', 'badge-bear', 'FEAR'
    elif score <= 55:
        return 'yellow', 'badge-warn', 'NEUTRAL'
    elif score <= 75:
        return 'green', 'badge-bull', 'GREED'
    else:
        return 'green', 'badge-bull', 'EXTREME GREED'

def naaim_badge(val):
    if val >= 75:
        return 'green', 'badge-bull', 'OVERWEIGHT'
    elif val >= 50:
        return 'yellow', 'badge-warn', 'MODERATE'
    elif val >= 25:
        return 'red', 'badge-bear', 'UNDERWEIGHT'
    else:
        return 'red', 'badge-bear', 'HEAVILY UNDERWEIGHT'

def t2108_badge(val):
    if val >= 70:
        return 'red', 'badge-bear', 'OVERBOUGHT (>70%)'
    elif val >= 40:
        return 'yellow', 'badge-warn', 'NEUTRAL (40-70%)'
    elif val >= 20:
        return 'red', 'badge-bear', 'OVERSOLD (<40%)'
    else:
        return 'red', 'badge-bear', 'EXTREME OVERSOLD (<20%)'

def ratio_badge(val):
    if val is None:
        return 'yellow', 'badge-neutral', 'N/A'
    if val >= 1.5:
        return 'green', 'badge-bull', 'BULLISH (>1.5)'
    elif val >= 1.0:
        return 'green', 'badge-bull', 'POSITIVE (>1.0)'
    elif val >= 0.7:
        return 'yellow', 'badge-warn', 'BEARISH (<1.0)'
    else:
        return 'red', 'badge-bear', 'VERY BEARISH (<0.7)'

def movers_badge(up4, dn4):
    """Signal for up/down 4%+ movers."""
    if up4 is None or dn4 is None:
        return ('yellow', 'badge-neutral', 'N/A'), ('yellow', 'badge-neutral', 'N/A')
    up_sig = ('green', 'badge-bull', 'BUYING PRESSURE') if up4 > dn4 else ('red', 'badge-bear', 'SELLING PRESSURE')
    dn_sig = ('red', 'badge-bear', 'SELLING PRESSURE') if dn4 > up4 else ('green', 'badge-bull', 'BUYING PRESSURE')
    return up_sig, dn_sig

def ad_ratio_badge(ratio_str):
    try:
        r = float(ratio_str)
        if r >= 2.0:
            return 'badge-bull'
        elif r >= 1.0:
            return 'badge-warn'
        else:
            return 'badge-bear'
    except:
        return 'badge-neutral'

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: MACRO DATA
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 1] Macro data via yfinance...")

import yfinance as yf
import numpy as np

def wilder_rsi(closes, period=14):
    """Wilder's Smoothed Moving Average RSI — matches Yahoo Finance/TradingView."""
    closes = np.array(closes, dtype=float)
    deltas = np.diff(closes)
    gains  = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - 100 / (1 + avg_gain / avg_loss), 1)

MACRO_TICKERS = {
    'SPY': 'SPY', 'QQQ': 'QQQ', 'IWM': 'IWM', 'DIA': 'DIA',
    'VIX': '^VIX', 'GLD': 'GLD', 'USO': 'USO',
    'TNX': '^TNX', 'DXY': 'DX-Y.NYB', 'BTC': 'BTC-USD',
}

macro = {}
for key, ticker in MACRO_TICKERS.items():
    try:
        df = yf.download(ticker, period='1y', interval='1d', progress=False, auto_adjust=True)
        if df.empty:
            continue
        closes = df['Close'].dropna().values.flatten()
        price  = float(closes[-1])
        prev   = float(closes[-2])
        chg    = (price - prev) / prev * 100
        ma20   = float(np.mean(closes[-20:]))
        ma50   = float(np.mean(closes[-50:]))
        ma200  = float(np.mean(closes[-200:]))
        rsi    = wilder_rsi(closes)
        macro[key] = {
            'price': price, 'chg': chg, 'rsi': rsi,
            'ma20': ma20, 'ma50': ma50, 'ma200': ma200,
            'vs20': (price-ma20)/ma20*100,
            'vs50': (price-ma50)/ma50*100,
            'vs200': (price-ma200)/ma200*100,
        }
        print(f"  {key}: ${price:.2f} ({chg:+.2f}%) RSI={rsi}")
    except Exception as e:
        print(f"  WARNING {key}: {e}")

def fill_ticker_placeholders(key):
    d = macro.get(key)
    if not d:
        return
    price = d['price']
    above_20  = price > d['ma20']
    above_50  = price > d['ma50']
    above_200 = price > d['ma200']
    if above_20 and above_50 and above_200:
        bc, sig = 'badge-bull', 'ABOVE ALL MAs'
    elif not above_20 and not above_50 and not above_200:
        bc, sig = 'badge-bear', 'BELOW ALL MAs'
    elif not above_20 and not above_50:
        bc, sig = 'badge-warn', 'BELOW 20/50MA'
    elif not above_200:
        bc, sig = 'badge-bear', 'BELOW 200MA'
    else:
        bc, sig = 'badge-warn', 'MIXED'

    P[f'{key}_PRICE']     = f"{price:.2f}"
    P[f'{key}_CHG']       = fmt(d['chg'])
    P[f'{key}_CHG_COLOR'] = chg_color(d['chg'])
    P[f'{key}_MA20']      = f"{d['ma20']:.2f}"
    P[f'{key}_MA50']      = f"{d['ma50']:.2f}"
    P[f'{key}_MA200']     = f"{d['ma200']:.2f}"
    # Aliases used in Step 4A table
    P[f'{key}_20MA']      = f"{d['ma20']:.2f}"
    P[f'{key}_50MA']      = f"{d['ma50']:.2f}"
    P[f'{key}_200MA']     = f"{d['ma200']:.2f}"
    P[f'{key}_VS_20MA']   = fmt(d['vs20'])
    P[f'{key}_VS_50MA']   = fmt(d['vs50'])
    P[f'{key}_VS_200MA']  = fmt(d['vs200'])
    P[f'{key}_20_COLOR']  = chg_color(d['vs20'])
    P[f'{key}_50_COLOR']  = chg_color(d['vs50'])
    P[f'{key}_200_COLOR'] = chg_color(d['vs200'])
    P[f'{key}_RSI']       = str(d['rsi'])
    P[f'{key}_RSI_COLOR'] = 'green' if d['rsi'] >= 60 else ('red' if d['rsi'] <= 40 else 'yellow')
    P[f'{key}_BADGE']     = bc
    P[f'{key}_SIGNAL']    = sig

for key in ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'USO', 'TNX', 'DXY', 'BTC']:
    fill_ticker_placeholders(key)

# BTC price with comma formatting
if 'BTC' in macro:
    P['BTC_PRICE'] = f"{macro['BTC']['price']:,.2f}"

# VIX special handling
if 'VIX' in macro:
    d = macro['VIX']
    P['VIX']           = f"{d['price']:.2f}"
    P['VIX_CHG']       = fmt(d['chg'])
    P['VIX_CHG_COLOR'] = chg_color(-d['chg'])  # VIX up = bearish = red
    vbc, vsig = vix_badge(d['price'])
    P['VIX_BADGE']  = vbc
    P['VIX_SIGNAL'] = vsig

# Macro summary note (dynamic)
spy_d = macro.get('SPY', {})
vix_d = macro.get('VIX', {})
btc_d = macro.get('BTC', {})
gld_d = macro.get('GLD', {})
uso_d = macro.get('USO', {})
tnx_d = macro.get('TNX', {})

macro_parts = []
if spy_d:
    macro_parts.append(f"SPY {fmt(spy_d['chg'])}%")
if vix_d:
    macro_parts.append(f"VIX {vix_d['price']:.2f} ({fmt(vix_d['chg'])}%)")
if gld_d:
    macro_parts.append(f"GLD {fmt(gld_d['chg'])}%")
if uso_d:
    macro_parts.append(f"USO {fmt(uso_d['chg'])}%")
if tnx_d:
    macro_parts.append(f"10Y Yield {tnx_d['price']:.2f}%")
if btc_d:
    macro_parts.append(f"BTC ${btc_d['price']:,.0f} ({fmt(btc_d['chg'])}%)")
P['MACRO_SUMMARY'] = '📌 宏觀總結: ' + ' | '.join(macro_parts) if macro_parts else '📌 宏觀總結: 數據載入中'

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: FEAR & GREED + NAAIM
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 3] Fear & Greed + NAAIM...")

import requests
req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Fear & Greed via CNN API
fg_score = 50
try:
    r = requests.get('https://production.dataviz.cnn.io/index/fearandgreed/graphdata',
                     headers=req_headers, timeout=10)
    fg = r.json()['fear_and_greed']
    fg_score  = int(float(fg['score']))
    fg_rating = fg.get('rating', 'N/A').replace('_', ' ').title()
    P['FEAR_GREED']        = str(fg_score)
    P['FEAR_GREED_RATING'] = fg_rating
    fg_color, fg_bc, fg_sig = fg_badge(fg_score)
    P['FEAR_GREED_COLOR'] = fg_color
    P['FEAR_GREED_BADGE'] = fg_bc
    print(f"  Fear & Greed: {fg_score} ({fg_rating})")
except Exception as e:
    print(f"  WARNING Fear & Greed: {e}")
    P['FEAR_GREED']        = 'N/A'
    P['FEAR_GREED_RATING'] = 'N/A'
    P['FEAR_GREED_COLOR']  = 'yellow'
    P['FEAR_GREED_BADGE']  = 'badge-neutral'

# NAAIM — download Excel, read row 2 (most recent)
try:
    import openpyxl, re as _re2
    naaim_page = requests.get('https://naaim.org/programs/naaim-exposure-index/', headers=req_headers, timeout=15)
    xlsx_links = _re2.findall(r'https://naaim\.org/wp-content/uploads/[^"\' ]+\.xlsx', naaim_page.text, _re2.I)
    if not xlsx_links:
        raise ValueError('No NAAIM Excel link found on page')
    naaim_url = xlsx_links[0]
    print(f"  NAAIM URL: {naaim_url}")
    r = requests.get(naaim_url, headers=req_headers, timeout=15)
    wb = openpyxl.load_workbook(io.BytesIO(r.content))
    ws = wb.active
    row2 = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))[0]
    naaim_val  = round(float(row2[1] if row2[1] is not None else row2[0]), 2)
    naaim_date = row2[0]
    naaim_date_str = naaim_date.strftime('%b %-d, %Y') if hasattr(naaim_date, 'strftime') else str(naaim_date)
    P['NAAIM']      = str(naaim_val)
    P['NAAIM_DATE'] = naaim_date_str
    nc, nbc, nsig = naaim_badge(naaim_val)
    P['NAAIM_COLOR']  = nc
    P['NAAIM_BADGE']  = nbc
    P['NAAIM_SIGNAL'] = nsig
    print(f"  NAAIM: {naaim_val} ({naaim_date_str})")
except Exception as e:
    print(f"  WARNING NAAIM: {e}")
    P['NAAIM']        = 'N/A'
    P['NAAIM_DATE']   = 'N/A'
    P['NAAIM_COLOR']  = 'yellow'
    P['NAAIM_BADGE']  = 'badge-neutral'
    P['NAAIM_SIGNAL'] = 'N/A'

# Sentiment summary note
P['SENTIMENT_SUMMARY'] = (
    f"📌 情緒總結: Fear & Greed {P.get('FEAR_GREED','N/A')} ({P.get('FEAR_GREED_RATING','N/A')}) | "
    f"VIX {P.get('VIX','N/A')} | "
    f"T2108 {P.get('T2108','N/A')}% | "
    f"NAAIM {P.get('NAAIM','N/A')} (as of {P.get('NAAIM_DATE','N/A')})"
)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4C: STOCKCHARTS BREADTH SCREENSHOTS (9 charts)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 4C] StockCharts breadth screenshots (9 charts)...")

BREADTH = [
    ('SPXA20R',  '$SPXA20R'),
    ('SPXA50R',  '$SPXA50R'),
    ('SPXA200R', '$SPXA200R'),
    ('NDXA20R',  '$NDXA20R'),
    ('NDXA50R',  '$NDXA50R'),
    ('NDXA200R', '$NDXA200R'),
    ('NYA20R',   '$NYA20R'),
    ('NYA50R',   '$NYA50R'),
    ('NYA200R',  '$NYA200R'),
]

breadth_paths = {name: str(IMG_DIR / f'{name}.png') for name, _ in BREADTH}

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright

CHARTS = {json.dumps([(n, s, breadth_paths[n]) for n, s in BREADTH])}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, symbol, save_path in CHARTS:
            page = await browser.new_page(viewport={{'width': 1600, 'height': 700}})
            url = f'https://stockcharts.com/h-sc/ui?s={{symbol}}&p=D&yr=1&mn=0&dy=0'
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)
                await page.screenshot(path=save_path)
                print(f'done:{{name}}')
            except Exception as e:
                print(f'fail:{{name}}:{{e}}')
            await page.close()
        await browser.close()

asyncio.run(main())
""", timeout=360)

print(out)
for name, _ in BREADTH:
    path = IMG_DIR / f'{name}.png'
    if path.exists():
        P[f'IMG_{name}'] = img_path(f'{name}.png')
    else:
        P[f'IMG_{name}'] = ''
        print(f"  WARNING Missing: {name}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4C (PART 2): BARCHART EXACT % VALUES
# Barchart is the authoritative source for exact numeric values.
# StockCharts screenshots are for visual reference only.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 4C-values] Barchart exact breadth values...")

from bs4 import BeautifulSoup as BS
import re as _re

BARCHART_BREADTH = [
    ('SPXA20R',  'S5TW',  'S&P 500 % above 20MA'),
    ('SPXA50R',  'S5FI',  'S&P 500 % above 50MA'),
    ('SPXA200R', 'S5TH',  'S&P 500 % above 200MA'),
    ('NDXA20R',  'NDTW',  'Nasdaq 100 % above 20MA'),
    ('NDXA50R',  'NDFI',  'Nasdaq 100 % above 50MA'),
    ('NDXA200R', 'NDTH',  'Nasdaq 100 % above 200MA'),
    ('NYA20R',   'MMTW',  'NYSE % above 20MA'),
    ('NYA50R',   'MMFI',  'NYSE % above 50MA'),
    ('NYA200R',  'MMTH',  'NYSE % above 200MA'),
]

for placeholder, symbol, desc in BARCHART_BREADTH:
    try:
        bc_url = f'https://www.barchart.com/stocks/quotes/%24{symbol}/overview'
        bc_resp = requests.get(bc_url, headers=req_headers, timeout=12)
        bc_soup = BS(bc_resp.text, 'html.parser')
        val_str = None
        # Method 1: JSON lastPrice in script tags
        for script in bc_soup.find_all('script'):
            txt = script.get_text()
            m = _re.search(r'"lastPrice"\s*:\s*([\d.]+)', txt)
            if m:
                val_str = m.group(1)
                break
        # Method 2: look for number near 'Last Price' label
        if not val_str:
            for elem in bc_soup.find_all(string=_re.compile(r'Last Price', _re.I)):
                parent = elem.parent
                sibling = parent.find_next_sibling()
                if sibling:
                    txt = sibling.get_text(strip=True).replace('%','')
                    if _re.match(r'^[\d.]+$', txt):
                        val_str = txt
                        break
        # Method 3: og:description meta tag
        if not val_str:
            meta_desc = bc_soup.find('meta', {'property': 'og:description'})
            if meta_desc:
                m = _re.search(r'([\d.]+)%?\s+(?:last|price|value)', meta_desc.get('content',''), _re.I)
                if m:
                    val_str = m.group(1)
        if val_str:
            val = round(float(val_str), 2)
            val_display = f'{val:.2f}%'
            P[placeholder] = val_display
            col, bc, sig = breadth_signal(val)
            P[f'{placeholder}_COLOR']  = col
            P[f'{placeholder}_BADGE']  = bc
            P[f'{placeholder}_SIGNAL'] = sig
            print(f"  {desc} ({symbol}): {val_display}")
        else:
            P[placeholder] = 'N/A'
            P[f'{placeholder}_COLOR']  = 'yellow'
            P[f'{placeholder}_BADGE']  = 'badge-neutral'
            P[f'{placeholder}_SIGNAL'] = 'N/A'
            print(f"  WARNING {symbol}: value not found in page")
    except Exception as _e:
        P[placeholder] = 'N/A'
        P[f'{placeholder}_COLOR']  = 'yellow'
        P[f'{placeholder}_BADGE']  = 'badge-neutral'
        P[f'{placeholder}_SIGNAL'] = 'N/A'
        print(f"  WARNING {symbol}: {_e}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4B: SECTOR ETF RSI (Wilder SMMA, sorted high→low)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 4B] Sector ETF RSI...")

SECTOR_ETFS = [
    ('XLK', 'Technology'),
    ('XLF', 'Financials'),
    ('XLE', 'Energy'),
    ('XLV', 'Health Care'),
    ('XLI', 'Industrials'),
    ('XLY', 'Consumer Discret.'),
    ('XLP', 'Consumer Staples'),
    ('XLB', 'Materials'),
    ('XLU', 'Utilities'),
    ('XLRE', 'Real Estate'),
    ('XLC', 'Comm. Services'),
    ('SPY', 'S&P 500 (ref)'),
]

sector_rows = []
for ticker, sector_name in SECTOR_ETFS:
    try:
        df = yf.download(ticker, period='1y', interval='1d', progress=False, auto_adjust=True)
        closes = df['Close'].dropna().values.flatten()
        price  = float(closes[-1])
        prev   = float(closes[-2])
        chg    = (price - prev) / prev * 100
        ma20   = float(np.mean(closes[-20:]))
        ma50   = float(np.mean(closes[-50:]))
        ma200  = float(np.mean(closes[-200:]))
        rsi    = wilder_rsi(closes)
        sector_rows.append({
            'ticker': ticker, 'sector': sector_name,
            'price': price, 'chg': chg, 'rsi': rsi,
            'vs20': (price-ma20)/ma20*100,
            'vs50': (price-ma50)/ma50*100,
            'vs200': (price-ma200)/ma200*100,
        })
    except Exception as e:
        print(f"  WARNING {ticker}: {e}")

sector_rows.sort(key=lambda x: x['rsi'], reverse=True)
if sector_rows:
    print(f"  Top sector: {sector_rows[0]['ticker']} RSI={sector_rows[0]['rsi']}")

def sector_row_html(i, s):
    chg_cls = 'green' if s['chg'] >= 0 else 'red'
    chg_str = f"{s['chg']:+.2f}%"
    rsi = s['rsi']
    rsi_badge = 'badge-warn' if rsi >= 70 else ('badge-bear' if rsi <= 30 else 'badge-neutral')
    signal = 'OVERBOUGHT' if rsi >= 70 else ('OVERSOLD' if rsi <= 30 else 'NEUTRAL')

    def ma_td(v):
        c = 'green' if v >= 0 else 'red'
        return f'<td style="color:{c};">{v:+.2f}%</td>'

    # Highlight SPY row
    row_style = ' style="background:#1c2128;border-left:3px solid #f39c12;"' if s['ticker'] == 'SPY' else ''

    return (f'<tr{row_style}>'
            f'<td>{i}</td>'
            f'<td><strong>{s["ticker"]}</strong>'
            + (' <span class="badge badge-info">BENCHMARK</span>' if s['ticker'] == 'SPY' else '') +
            f'</td>'
            f'<td>{s["sector"]}</td>'
            f'<td>${s["price"]:.2f}</td>'
            f'<td style="color:{chg_cls};">{chg_str}</td>'
            + ma_td(s['vs20']) + ma_td(s['vs50']) + ma_td(s['vs200']) +
            f'<td><span class="badge {rsi_badge}">{rsi:.1f}</span></td>'
            f'<td><span class="badge {rsi_badge}">{signal}</span></td>'
            f'</tr>\n')

SECTOR_ROWS_HTML = ''
for i, s in enumerate(sector_rows, 1):
    SECTOR_ROWS_HTML += sector_row_html(i, s)

P['SECTOR_ROWS'] = SECTOR_ROWS_HTML

# Sector summary note
if sector_rows:
    top = sector_rows[0]
    bot = sector_rows[-1]
    P['SECTOR_SUMMARY'] = (
        f"📌 板塊 ETF 總結 (RSI 排序): {top['ticker']} ({top['sector']}) RSI {top['rsi']:.1f} 最強。"
        f"{bot['ticker']} ({bot['sector']}) RSI {bot['rsi']:.1f} 最弱。"
        f"SPY RSI {next((s['rsi'] for s in sector_rows if s['ticker']=='SPY'), 'N/A')}。"
    )
else:
    P['SECTOR_SUMMARY'] = '📌 板塊 ETF 數據載入中'

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4D / 5B: FINVIZ INDUSTRY LEADERS (Top 10, with parent sector)
# ═══════════════════════════════════════════════════════════════════════════════
print("[Step 4D] Finviz Industry data...")
P["IMG_5A_SECTORS"] = ""

import requests as _req
from bs4 import BeautifulSoup as _BS

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
_hdrs = {
    "User-Agent": _UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}
_industry_html = ""
try:
    _resp = _req.get("https://finviz.com/groups.ashx?g=industry&o=-change&v=110",
                     headers=_hdrs, timeout=15)
    _soup = _BS(_resp.text, "html.parser")
    _tables = _soup.find_all("table")
    _data_table = None
    for _t in _tables:
        _rows = _t.find_all("tr")
        if len(_rows) > 20:
            _hdrow = [c.get_text(strip=True) for c in _rows[0].find_all(["td","th"])]
            if "Name" in _hdrow and "Change" in _hdrow:
                _data_table = _t
                _col_names = _hdrow
                break
    if _data_table:
        _chg_idx    = _col_names.index("Change")
        _name_idx   = _col_names.index("Name")
        _stocks_idx = _col_names.index("Stocks") if "Stocks" in _col_names else None
        _sector_idx = _col_names.index("Sector") if "Sector" in _col_names else None
        _rows_data = []
        for _row in _data_table.find_all("tr")[1:]:
            _cells = [c.get_text(strip=True) for c in _row.find_all("td")]
            if len(_cells) > _chg_idx:
                _rows_data.append(_cells)
        # Top 10 gainers only (already sorted desc by change)
        _top10 = _rows_data[:10]
        def _row_html(cells, idx):
            name    = cells[_name_idx]
            chg     = cells[_chg_idx]
            stocks  = cells[_stocks_idx] if _stocks_idx else ""
            sector  = cells[_sector_idx] if _sector_idx else "—"
            color   = "#2ecc71" if not chg.startswith("-") else "#e74c3c"
            return f"""<tr>
  <td style="color:#8b949e;padding:4px 8px;">{idx}</td>
  <td style="color:#e6edf3;padding:4px 8px;font-weight:600;">{name}</td>
  <td style="color:#8b949e;padding:4px 8px;">{sector}</td>
  <td style="color:#8b949e;padding:4px 8px;">{stocks}</td>
  <td style="color:{color};padding:4px 8px;font-weight:700;">{chg}</td>
</tr>"""
        _rows_html_top = "".join([_row_html(r, i+1) for i, r in enumerate(_top10)])
        _industry_html = f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
<thead><tr>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">#</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">Industry</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">Sector</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">Stocks</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">1D Change</th>
</tr></thead>
<tbody>
{_rows_html_top}
</tbody></table>"""
        print(f"  ✅ Finviz Industry: {len(_rows_data)} industries scraped, top 10 shown")
    else:
        print("  WARNING: Industry table not found")
except Exception as _e:
    print(f"  WARNING Finviz Industry: {_e}")

P["IMG_5B_INDUSTRY"] = _industry_html

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6A: ADVANCE/DECLINE RATIO (StockCharts Market Summary)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6A] StockCharts A/D Ratio...")

AD_INDICES = [
    ('SP500',   'S&P 500',      'sp500'),
    ('NDX100',  'Nasdaq 100',   'ndx'),
    ('DJIA',    'DJIA',         'djia'),
    ('RUT',     'Russell 2000', 'rut'),
]

ad_rows_html = ''
try:
    sc_resp = requests.get(
        'https://stockcharts.com/docs/doku.php?id=market_summary',
        headers=req_headers, timeout=15
    )
    sc_soup = BS(sc_resp.text, 'html.parser')

    ad_data = {}
    for tbl in sc_soup.find_all('table'):
        hdrs = [th.get_text(strip=True).lower() for th in tbl.find_all(['th','td'])[:10]]
        if any('advancing' in h for h in hdrs) and any('declining' in h for h in hdrs):
            rows = tbl.find_all('tr')
            hdr_row = rows[0].find_all(['th','td'])
            hdr_texts = [c.get_text(strip=True).lower() for c in hdr_row]
            adv_idx  = next((i for i, h in enumerate(hdr_texts) if 'advancing' in h), None)
            dec_idx  = next((i for i, h in enumerate(hdr_texts) if 'declining' in h), None)
            unch_idx = next((i for i, h in enumerate(hdr_texts) if 'unchanged' in h), None)
            name_idx = 0
            for data_row in rows[1:]:
                cells = data_row.find_all(['th','td'])
                if len(cells) < 2:
                    continue
                row_name = cells[name_idx].get_text(strip=True).lower()
                def safe_int(cells, idx):
                    if idx is None or idx >= len(cells):
                        return None
                    txt = cells[idx].get_text(strip=True).replace(',','')
                    try: return int(txt)
                    except: return None
                adv  = safe_int(cells, adv_idx)
                dec  = safe_int(cells, dec_idx)
                unch = safe_int(cells, unch_idx)
                for key, label, match in AD_INDICES:
                    if match in row_name or label.lower() in row_name:
                        ad_data[key] = {'label': label, 'adv': adv, 'dec': dec, 'unch': unch}
            break

    ad_table_rows = ''
    for key, label, _ in AD_INDICES:
        d = ad_data.get(key, {})
        adv  = d.get('adv')
        dec  = d.get('dec')
        unch = d.get('unch')
        if adv and dec and dec > 0:
            ratio = round(adv / dec, 2)
            ratio_color = '#2ecc71' if ratio >= 1.0 else '#e74c3c'
        else:
            ratio = None
            ratio_color = '#8b949e'
        adv_str   = f"{adv:,}"   if adv   is not None else 'N/A'
        dec_str   = f"{dec:,}"   if dec   is not None else 'N/A'
        unch_str  = f"{unch:,}"  if unch  is not None else 'N/A'
        ratio_str = f"{ratio:.2f}" if ratio is not None else 'N/A'
        ad_table_rows += (
            f'<tr style="border-bottom:1px solid #30363d;">'
            f'<td style="padding:8px 10px;color:#e6edf3;font-weight:600;">{label}</td>'
            f'<td style="padding:8px 10px;color:#2ecc71;text-align:right;">{adv_str}</td>'
            f'<td style="padding:8px 10px;color:#e74c3c;text-align:right;">{dec_str}</td>'
            f'<td style="padding:8px 10px;color:#8b949e;text-align:right;">{unch_str}</td>'
            f'<td style="padding:8px 10px;color:{ratio_color};text-align:right;font-weight:700;">{ratio_str}</td>'
            f'</tr>\n'
        )
        P[f'AD_{key}_ADV']   = adv_str
        P[f'AD_{key}_DEC']   = dec_str
        P[f'AD_{key}_UNCH']  = unch_str
        P[f'AD_{key}_RATIO'] = ratio_str
        P[f'AD_{key}_BADGE'] = ad_ratio_badge(ratio_str)
        print(f"  {label}: Adv={adv_str} Dec={dec_str} Ratio={ratio_str}")

    # Alias for SP500 in regime box
    P['AD_SP500_ADV']   = P.get('AD_SP500_ADV', 'N/A')
    P['AD_SP500_DEC']   = P.get('AD_SP500_DEC', 'N/A')
    P['AD_SP500_RATIO'] = P.get('AD_SP500_RATIO', 'N/A')
    P['AD_SP500_BADGE'] = P.get('AD_SP500_BADGE', 'badge-neutral')

    AD_TABLE_HTML = f'''<table style="width:100%;border-collapse:collapse;font-size:13px;">
<thead><tr style="background:#0d1117;border-bottom:1px solid #30363d;">
  <th style="padding:8px 10px;text-align:left;color:#8b949e;">Index</th>
  <th style="padding:8px 10px;text-align:right;color:#2ecc71;">Advancing</th>
  <th style="padding:8px 10px;text-align:right;color:#e74c3c;">Declining</th>
  <th style="padding:8px 10px;text-align:right;color:#8b949e;">Unchanged</th>
  <th style="padding:8px 10px;text-align:right;color:#f1c40f;">AD Ratio</th>
</tr></thead>
<tbody>
{ad_table_rows}</tbody></table>'''
    P['AD_RATIO_TABLE'] = AD_TABLE_HTML
    print("  ✅ StockCharts A/D Ratio done")

except Exception as _e:
    print(f"  WARNING Step 6A StockCharts A/D: {_e}")
    P['AD_RATIO_TABLE'] = '<p style="color:#8b949e;">A/D Ratio data unavailable</p>'
    for key, _, __ in AD_INDICES:
        P[f'AD_{key}_ADV']   = 'N/A'
        P[f'AD_{key}_DEC']   = 'N/A'
        P[f'AD_{key}_UNCH']  = 'N/A'
        P[f'AD_{key}_RATIO'] = 'N/A'
        P[f'AD_{key}_BADGE'] = 'badge-neutral'
    P['AD_SP500_ADV']   = 'N/A'
    P['AD_SP500_DEC']   = 'N/A'
    P['AD_SP500_RATIO'] = 'N/A'
    P['AD_SP500_BADGE'] = 'badge-neutral'

# Legacy placeholder — no longer used
P['IMG_MARKETINOUT'] = ''

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6B: STOCKBEE T2108 (Google Sheets CSV + screenshot)
# Source: https://stockbee.blogspot.com/p/mm.html (no login needed)
# T2108 data is inside a Google Sheets iframe on that page.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6B] Stockbee T2108...")

STOCKBEE_CSV  = 'https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=csv'
STOCKBEE_HTML = 'https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=html&widget=true'

t2108_val = up4_val = dn4_val = r5d_val = r10d_val = None

try:
    r = requests.get(STOCKBEE_CSV, timeout=15)
    rows = list(csv.reader(io.StringIO(r.text)))

    header_idx = 0
    for i, row in enumerate(rows[:5]):
        if any('t2108' in str(c).lower() or 'date' in str(c).lower() for c in row):
            header_idx = i
            break

    hdr  = rows[header_idx]
    data = rows[header_idx + 1]

    def find_col(*keywords):
        for i, h in enumerate(hdr):
            h_lower = str(h).lower()
            if all(k in h_lower for k in keywords):
                return i
        return None

    t2108_col = find_col('t2108') or find_col('t21')
    up4_col   = next((i for i, h in enumerate(hdr) if 'up' in str(h).lower() and '4' in str(h)), None)
    dn4_col   = next((i for i, h in enumerate(hdr) if 'down' in str(h).lower() and '4' in str(h)), None)
    r5d_col   = next((i for i, h in enumerate(hdr) if '5' in str(h) and 'ratio' in str(h).lower()), None)
    r10d_col  = next((i for i, h in enumerate(hdr) if '10' in str(h) and 'ratio' in str(h).lower()), None)

    if t2108_col is not None and data[t2108_col]:
        t2108_val = round(float(data[t2108_col]), 2)
    if up4_col is not None and data[up4_col]:
        up4_val = int(float(data[up4_col]))
    if dn4_col is not None and data[dn4_col]:
        dn4_val = int(float(data[dn4_col]))
    if r5d_col is not None and data[r5d_col]:
        r5d_val = round(float(data[r5d_col]), 2)
    if r10d_col is not None and data[r10d_col]:
        r10d_val = round(float(data[r10d_col]), 2)

    print(f"  T2108: {t2108_val}% | Up4%+: {up4_val} | Down4%+: {dn4_val}")
    print(f"  5D ratio: {r5d_val} | 10D ratio: {r10d_val}")

except Exception as e:
    print(f"  WARNING Stockbee CSV: {e}")

P['T2108']     = str(t2108_val) if t2108_val is not None else 'N/A'
P['UP4PCT']    = str(up4_val)   if up4_val   is not None else 'N/A'
P['DOWN4PCT']  = str(dn4_val)   if dn4_val   is not None else 'N/A'
P['RATIO_5D']  = str(r5d_val)   if r5d_val   is not None else 'N/A'
P['RATIO_10D'] = str(r10d_val)  if r10d_val  is not None else 'N/A'

# T2108 color/badge/zone
if t2108_val is not None:
    if t2108_val >= 70:
        t2108_color = '#e74c3c'
        t2108_zone  = 'Overbought'
        t2108_color_class = 'red'
        t2108_badge = 'badge-bear'
    elif t2108_val <= 20:
        t2108_color = '#2ecc71'
        t2108_zone  = 'Extreme Oversold'
        t2108_color_class = 'green'
        t2108_badge = 'badge-bear'
    elif t2108_val <= 40:
        t2108_color = '#e74c3c'
        t2108_zone  = 'Oversold'
        t2108_color_class = 'red'
        t2108_badge = 'badge-bear'
    else:
        t2108_color = '#f1c40f'
        t2108_zone  = 'Neutral'
        t2108_color_class = 'yellow'
        t2108_badge = 'badge-warn'
else:
    t2108_color = '#8b949e'
    t2108_zone  = 'N/A'
    t2108_color_class = 'yellow'
    t2108_badge = 'badge-neutral'

P['T2108_COLOR']       = t2108_color
P['T2108_ZONE']        = t2108_zone
P['T2108_COLOR_CLASS'] = t2108_color_class
P['T2108_BADGE']       = t2108_badge

# Update sentiment summary now that T2108 is known
P['SENTIMENT_SUMMARY'] = (
    f"📌 情緒總結: Fear & Greed {P.get('FEAR_GREED','N/A')} ({P.get('FEAR_GREED_RATING','N/A')}) | "
    f"VIX {P.get('VIX','N/A')} | "
    f"T2108 {P.get('T2108','N/A')}% ({t2108_zone}) | "
    f"NAAIM {P.get('NAAIM','N/A')} (as of {P.get('NAAIM_DATE','N/A')})"
)

# Movers badges
up_sig, dn_sig = movers_badge(up4_val, dn4_val)
P['UP4PCT_COLOR']    = up_sig[0]
P['UP4PCT_BADGE']    = up_sig[1]
P['UP4PCT_SIGNAL']   = up_sig[2]
P['DOWN4PCT_COLOR']  = dn_sig[0]
P['DOWN4PCT_BADGE']  = dn_sig[1]
P['DOWN4PCT_SIGNAL'] = dn_sig[2]

# Ratio badges
r5_color, r5_badge, r5_sig = ratio_badge(r5d_val)
r10_color, r10_badge, r10_sig = ratio_badge(r10d_val)
P['RATIO_5D_COLOR']   = r5_color
P['RATIO_5D_BADGE']   = r5_badge
P['RATIO_5D_SIGNAL']  = r5_sig
P['RATIO_10D_COLOR']  = r10_color
P['RATIO_10D_BADGE']  = r10_badge
P['RATIO_10D_SIGNAL'] = r10_sig

# Breadth summary note
P['BREADTH_SUMMARY'] = (
    f"📌 廣度總結: T2108 {P['T2108']}% ({t2108_zone})。"
    f"今日上漲 4%+ 股票 {P['UP4PCT']} 隻，下跌 4%+ 股票 {P['DOWN4PCT']} 隻。"
    f"5日比率 {P['RATIO_5D']}，10日比率 {P['RATIO_10D']}。"
)

# Screenshot the Google Sheets (wide viewport to show T2108 column)
# Step 1: Try Stockbee page directly; Step 2: Fall back to Google Sheets URL
t2108_sheet_path = str(IMG_DIR / 't2108_sheet.png')

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{'width': 1800, 'height': 600}})
        try:
            await page.goto('{STOCKBEE_HTML}', wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            await page.evaluate('''
                var containers = document.querySelectorAll(".waffle-container, .grid-container, iframe");
                containers.forEach(c => {{ c.scrollLeft = 500; }});
            ''')
            await page.wait_for_timeout(500)
            await page.screenshot(path='{t2108_sheet_path}')
            print('done')
        except Exception as e:
            print(f'fail:{{e}}')
        await browser.close()

asyncio.run(main())
""", timeout=60)

if (IMG_DIR / 't2108_sheet.png').exists():
    P['IMG_T2108_SHEET'] = img_path('t2108_sheet.png')
    print("  ✅ T2108 screenshot done")
else:
    P['IMG_T2108_SHEET'] = ''
    print("  WARNING T2108 screenshot failed")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7: BULL VS BEAR COMMENTARY (OpenAI, Traditional Chinese)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 7] Bull vs Bear commentary...")

# Regime determination
regime_score = 0
if spy_d:
    if spy_d['price'] < spy_d['ma200']: regime_score += 2
    if spy_d['price'] < spy_d['ma50']:  regime_score += 1
    if spy_d['price'] < spy_d['ma20']:  regime_score += 1
if vix_d.get('price', 0) > 25: regime_score += 2
elif vix_d.get('price', 0) > 20: regime_score += 1
fg_str = P.get('FEAR_GREED', '')
if fg_str.isdigit() and int(fg_str) < 25:
    regime_score += 1

REGIME = ('BEARISH' if regime_score >= 6
          else 'BEARISH-TO-NEUTRAL' if regime_score >= 4
          else 'NEUTRAL' if regime_score >= 2
          else 'BULLISH')
P['REGIME'] = REGIME

# Regime guidance note
spxa20r_val = P.get('SPXA20R', 'N/A')
P['REGIME_GUIDANCE'] = (
    f"📌 交易建議 Trading Guidance: Regime = {REGIME}。"
    f"VIX {P.get('VIX','N/A')} ({P.get('VIX_SIGNAL','N/A')})。"
    f"SPY vs 200MA: {P.get('SPY_VS_200MA','N/A')}%。"
    f"$SPXA20R: {spxa20r_val}。"
    f"T2108: {P.get('T2108','N/A')}%。"
    f"等待 VIX 回落至 20 以下、SPY 收復 200MA (${P.get('SPY_MA200','N/A')}) 才考慮加倉。"
)

context = f"""
Date: {DATE_DISP}
SPY: ${spy_d.get('price',0):.2f} ({spy_d.get('chg',0):+.2f}%) | vs 20MA: {spy_d.get('vs20',0):+.2f}% | vs 50MA: {spy_d.get('vs50',0):+.2f}% | vs 200MA: {spy_d.get('vs200',0):+.2f}%
QQQ: ${macro.get('QQQ',{}).get('price',0):.2f} ({macro.get('QQQ',{}).get('chg',0):+.2f}%)
IWM: ${macro.get('IWM',{}).get('price',0):.2f} ({macro.get('IWM',{}).get('chg',0):+.2f}%)
VIX: {vix_d.get('price',0):.2f} ({vix_d.get('chg',0):+.2f}%)
Fear & Greed: {P.get('FEAR_GREED','N/A')} ({P.get('FEAR_GREED_RATING','N/A')})
NAAIM: {P.get('NAAIM','N/A')} ({P.get('NAAIM_DATE','N/A')})
T2108: {P.get('T2108','N/A')}% ({t2108_zone})
Up 4%+: {P.get('UP4PCT','N/A')} | Down 4%+: {P.get('DOWN4PCT','N/A')}
5D ratio: {P.get('RATIO_5D','N/A')} | 10D ratio: {P.get('RATIO_10D','N/A')}
$SPXA20R: {P.get('SPXA20R','N/A')} | $SPXA50R: {P.get('SPXA50R','N/A')} | $SPXA200R: {P.get('SPXA200R','N/A')}
Top sector by RSI: {sector_rows[0]['ticker'] if sector_rows else 'N/A'} RSI={sector_rows[0]['rsi'] if sector_rows else 'N/A'}
Regime: {REGIME}
"""

bear_pts = bull_pts = table_rows = []
guidance = ''

try:
    client = OpenAI()
    resp = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[{
            'role': 'system',
            'content': '''You are a professional swing trader analyst. Generate a bull vs bear analysis in Traditional Chinese (繁體中文).
Every argument MUST cite exact data values from the context provided.
Return JSON with these exact keys:
{
  "bear_points": ["4-6 bear arguments in Traditional Chinese, each citing exact data values"],
  "bull_points": ["3-5 bull arguments in Traditional Chinese, each citing exact data values"],
  "table_rows": [{"indicator":"indicator name","bull":true/false,"neutral":true/false,"bear":true/false}],
  "guidance": "trading guidance in Traditional Chinese, 2-3 sentences citing exact values"
}
Indicators for table_rows: Long-term Trend, Market Breadth, Sentiment, Institutional Positioning, Macro, Short-term Technical, Fundamentals'''
        }, {
            'role': 'user',
            'content': context
        }],
        response_format={'type': 'json_object'},
        temperature=0.4
    )
    bb = json.loads(resp.choices[0].message.content)
    bear_pts   = bb.get('bear_points', [])
    bull_pts   = bb.get('bull_points', [])
    table_rows = bb.get('table_rows', [])
    guidance   = bb.get('guidance', '')
    print(f"  ✅ Commentary generated ({len(bear_pts)} bear, {len(bull_pts)} bull)")
except Exception as e:
    print(f"  WARNING OpenAI commentary: {e}")

bear_li = ''.join(f'<li style="margin-bottom:6px;">{p}</li>\n' for p in bear_pts)
bull_li = ''.join(f'<li style="margin-bottom:6px;">{p}</li>\n' for p in bull_pts)
table_body = ''
for row in table_rows:
    b  = '✔' if row.get('bull')    else ''
    n  = '✔' if row.get('neutral') else ''
    br = '✔' if row.get('bear')    else ''
    table_body += (f'<tr style="border-bottom:1px solid #333;">'
                   f'<td style="padding:10px;">{row.get("indicator","")}</td>'
                   f'<td style="text-align:center;color:#2ecc71;">{b}</td>'
                   f'<td style="text-align:center;color:#f1c40f;">{n}</td>'
                   f'<td style="text-align:center;color:#e74c3c;">{br}</td>'
                   f'</tr>\n')

BULL_BEAR_HTML = f'''<div style="background:#1c2128; border:1px solid #e74c3c; border-radius:8px; padding:16px; margin-bottom:16px;">
  <h3 style="color:#e74c3c; margin:0 0 12px 0;">🐻 空頭論點 Bearish Case</h3>
  <ol style="color:#ecf0f1; margin:0; padding-left:20px; line-height:1.7;">
    {bear_li}
  </ol>
</div>
<div style="background:#1c2128; border:1px solid #2ecc71; border-radius:8px; padding:16px; margin-bottom:16px;">
  <h3 style="color:#2ecc71; margin:0 0 12px 0;">🐂 多頭論點 Bullish Case</h3>
  <ol style="color:#ecf0f1; margin:0; padding-left:20px; line-height:1.7;">
    {bull_li}
  </ol>
</div>
<table style="width:100%; border-collapse:collapse; margin-bottom:16px; color:#ecf0f1; background:#1c2128; border-radius:8px; overflow:hidden;">
  <thead>
    <tr style="background:#0d1117; border-bottom:1px solid #444;">
      <th style="padding:12px; text-align:left;">關鍵指標</th>
      <th style="padding:12px; text-align:center; color:#2ecc71;">多頭</th>
      <th style="padding:12px; text-align:center; color:#f1c40f;">中性</th>
      <th style="padding:12px; text-align:center; color:#e74c3c;">空頭</th>
    </tr>
  </thead>
  <tbody>
    {table_body}
  </tbody>
</table>
<p style="background:#1c2128; padding:14px; border-radius:6px; border-left:4px solid #f1c40f; color:#ecf0f1;">
  <strong style="color:#f1c40f;">📋 交易指引：</strong>{guidance}
</p>'''

P['BULL_BEAR_CONTENT'] = BULL_BEAR_HTML

# Economic Calendar placeholder (manual entry or future automation)
P['ECONOMIC_CALENDAR'] = '📅 請查閱 <a href="https://forex.tradingcharts.com/economic_calendar/" style="color:#58a6ff">forex.tradingcharts.com</a> 獲取未來三個交易日的重要經濟數據。'

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL: BUILD HTML FROM TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Final] Building HTML from TEMPLATE.html...")

with open(REPO / 'TEMPLATE.html') as f:
    html = f.read()

# Apply all replacements
for key, value in P.items():
    html = html.replace(f'{{{{{key}}}}}', str(value))

# Check for remaining unfilled placeholders
remaining = re.findall(r'\{\{[A-Z0-9_]+\}\}', html)
if remaining:
    print(f"  WARNING Unfilled placeholders: {set(remaining)}")
else:
    print("  ✅ All placeholders filled")

# Save dated archive
out_path = REPO / f'{DATE}.html'
with open(out_path, 'w') as f:
    f.write(html)
print(f"  ✅ Saved: {DATE}.html")

# Also update index.html (the live page)
index_path = REPO / 'index.html'
with open(index_path, 'w') as f:
    f.write(html)
print(f"  ✅ Saved: index.html")

# ── Update MARKET_HISTORY.md ───────────────────────────────────────────────────
history_path = REPO / 'MARKET_HISTORY.md'
new_entry = (f"| [{DATE}](https://matt-manus.github.io/swing-trader-daily/{DATE}.html) "
             f"| {REGIME} "
             f"| ${spy_d.get('price',0):.2f} ({spy_d.get('chg',0):+.2f}%) "
             f"| {vix_d.get('price',0):.2f} "
             f"| {P.get('FEAR_GREED','N/A')} "
             f"| {P.get('NAAIM','N/A')} "
             f"| {P.get('T2108','N/A')}% |\n")

try:
    with open(history_path) as f:
        history = f.read()
    marker = '|---|---|---|---|---|---|---|\n'
    if marker in history and DATE not in history:
        history = history.replace(marker, marker + new_entry, 1)
        with open(history_path, 'w') as f:
            f.write(history)
        print("  ✅ MARKET_HISTORY.md updated")
except Exception as e:
    print(f"  WARNING MARKET_HISTORY: {e}")

# ── Report complete ────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"🌐 Report ready: {DATE}.html")
print(f"🌐 https://matt-manus.github.io/swing-trader-daily/{DATE}.html")
print(f"{'='*60}")
print("\n=== Done ===")
