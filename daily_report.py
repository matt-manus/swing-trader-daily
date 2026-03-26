#!/usr/bin/env python3
"""
daily_report.py — Swing Trader Daily Market Summary
====================================================
Single script that generates the complete daily report.

Usage:
    python3 daily_report.py [YYYY-MM-DD]
    If no date given, uses today (HKT).

Screenshots are saved to images/{DATE}/ and referenced as relative paths.
No external CDN required — works in GitHub Actions.
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
REPORT_TIME = f"{now_hkt.strftime('%H:%M')} HKT ({now_et.strftime('%H:%M')} ET)"

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

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: MACRO DATA
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 1] Macro data via yfinance...")

import yfinance as yf
import numpy as np

def wilder_rsi(closes, period=14):
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

def color(v):
    return 'green' if float(v) >= 0 else 'red'

def fmt(v, decimals=2):
    v = float(v)
    sign = '+' if v >= 0 else ''
    return f"{sign}{v:.{decimals}f}"

MACRO_TICKERS = {
    'SPY': 'SPY', 'QQQ': 'QQQ', 'IWM': 'IWM', 'DIA': 'DIA',
    'VIX': '^VIX', 'GLD': 'GLD', 'USO': 'USO', 'TLT': 'TLT',
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
    # Determine MA signal badge
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
    P[f'{key}_CHG_COLOR'] = color(d['chg'])
    P[f'{key}_MA20']      = f"{d['ma20']:.2f}"
    P[f'{key}_MA50']      = f"{d['ma50']:.2f}"
    P[f'{key}_MA200']     = f"{d['ma200']:.2f}"
    P[f'{key}_VS_20MA']   = fmt(d['vs20'])
    P[f'{key}_VS_50MA']   = fmt(d['vs50'])
    P[f'{key}_VS_200MA']  = fmt(d['vs200'])
    P[f'{key}_20_COLOR']  = color(d['vs20'])
    P[f'{key}_50_COLOR']  = color(d['vs50'])
    P[f'{key}_200_COLOR'] = color(d['vs200'])
    P[f'{key}_RSI']       = str(d['rsi'])
    P[f'{key}_RSI_COLOR'] = 'green' if d['rsi'] >= 60 else ('red' if d['rsi'] <= 40 else 'yellow')
    P[f'{key}_BADGE']     = bc
    P[f'{key}_SIGNAL']    = sig

for key in ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'USO', 'TLT', 'TNX', 'DXY', 'BTC']:
    fill_ticker_placeholders(key)

# BTC display placeholders (price shown without $ prefix convention, uses comma formatting)
if 'BTC' in macro:
    P['BTC_PRICE']     = f"{macro['BTC']['price']:,.2f}"
    P['BTC_CHG']       = fmt(macro['BTC']['chg'])
    P['BTC_CHG_COLOR'] = color(macro['BTC']['chg'])
    print(f"  BTC: ${macro['BTC']['price']:,.2f} ({macro['BTC']['chg']:+.2f}%)")
else:
    P['BTC_PRICE']     = 'N/A'
    P['BTC_CHG']       = 'N/A'
    P['BTC_CHG_COLOR'] = 'grey'

# Add template-compatible aliases (template uses SPY_20MA, SPY_50MA, SPY_200MA, SPY_CHANGE_PCT)
# while fill_ticker_placeholders sets SPY_MA20, SPY_MA50, SPY_MA200, SPY_CHG
for key in ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'USO', 'TLT', 'TNX', 'DXY', 'BTC']:
    if f'{key}_MA20' in P:
        P[f'{key}_20MA']      = P[f'{key}_MA20']
        P[f'{key}_50MA']      = P[f'{key}_MA50']
        P[f'{key}_200MA']     = P[f'{key}_MA200']
        P[f'{key}_CHANGE_PCT'] = P[f'{key}_CHG'] + '%'

if 'VIX' in macro:
    d = macro['VIX']
    P['VIX']           = f"{d['price']:.2f}"
    P['VIX_CHG']       = fmt(d['chg'])
    P['VIX_CHG_COLOR'] = color(-d['chg'])  # VIX up = bearish

# ===============================================================================
# STEP 1B: NEWS (disabled)
# ===============================================================================
print("[Step 1B] News disabled.")
P['NEWS_ITEMS'] = ''
P['IMG_FULLSTACK'] = ''  # Step 2 removed per updated instructions

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
try:
    r = requests.get('https://production.dataviz.cnn.io/index/fearandgreed/graphdata',
                     headers=req_headers, timeout=10)
    fg = r.json()['fear_and_greed']
    fg_score  = int(float(fg['score']))
    fg_rating = fg.get('rating', 'N/A').replace('_', ' ').title()
    P['FEAR_GREED']        = str(fg_score)
    P['FEAR_GREED_RATING'] = fg_rating
    print(f"  Fear & Greed: {fg_score} ({fg_rating})")
except Exception as e:
    print(f"  WARNING Fear & Greed: {e}")
    P['FEAR_GREED']        = 'N/A'
    P['FEAR_GREED_RATING'] = 'N/A'

# NAAIM — download Excel, read row 2 (most recent, newest-first)
try:
    import openpyxl
    # Try current year first, then previous year
    for year in [REPORT_DATE.year, REPORT_DATE.year - 1]:
        naaim_url = f'https://naaim.org/wp-content/uploads/{year}/03/NAAIM-Exposure-Index.xlsx'
        try:
            r = requests.get(naaim_url, headers=req_headers, timeout=15)
            if r.status_code == 200:
                break
        except Exception:
            continue
    wb = openpyxl.load_workbook(io.BytesIO(r.content))
    ws = wb.active
    row2 = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))[0]
    # Column index 3 = Mean (0-indexed), column 0 = Date
    naaim_val  = round(float(row2[3] if row2[3] is not None else row2[1]), 2)
    naaim_date = row2[0]
    naaim_date_str = naaim_date.strftime('%b %-d, %Y') if hasattr(naaim_date, 'strftime') else str(naaim_date)
    P['NAAIM']      = str(naaim_val)
    P['NAAIM_DATE'] = naaim_date_str
    print(f"  NAAIM: {naaim_val} ({naaim_date_str})")
except Exception as e:
    print(f"  WARNING NAAIM: {e}")
    P['NAAIM']      = 'N/A'
    P['NAAIM_DATE'] = 'N/A'

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4C: STOCKCHARTS BREADTH SCREENSHOTS (9 charts, 1600px wide)
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
""", timeout=150)

print(out)
for name, _ in BREADTH:
    path = IMG_DIR / f'{name}.png'
    if path.exists():
        P[f'IMG_{name}'] = img_path(f'{name}.png')
    else:
        P[f'IMG_{name}'] = ''
        print(f"  WARNING Missing: {name}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4C (PART 2): BARCHART EXACT % VALUES FOR BREADTH
# Barchart is the authoritative source for exact numeric values.
# StockCharts screenshots are for visual reference only.
# Barchart symbols: $S5TW/$S5FI/$S5TH (SPX), $NDTW/$NDFI/$NDTH (NDX), $MMTW/$MMFI/$MMTH (NYSE)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 4C-values] Barchart exact breadth values...")

BARCHART_BREADTH = [
    # (placeholder_key, barchart_symbol, description)
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
        # Barchart shows the last price in a span with class 'last-price' or data-ng-bind
        # Try multiple selectors
        val_str = None
        # Method 1: og:description meta tag often has the price
        meta_desc = bc_soup.find('meta', {'property': 'og:description'})
        if meta_desc:
            import re as _re
            m = _re.search(r'([\d.]+)%?\s+(?:last|price|value)', meta_desc.get('content',''), _re.I)
            if not m:
                m = _re.search(r'last\s+price[^\d]*([\d.]+)', meta_desc.get('content',''), _re.I)
            if m:
                val_str = m.group(1)
        # Method 2: look for the price in the page title
        if not val_str:
            title_tag = bc_soup.find('title')
            if title_tag:
                m = _re.search(r'\$([\d.]+)', title_tag.get_text())
                if m:
                    val_str = m.group(1)
        # Method 3: look for spans/divs with the value near the symbol
        if not val_str:
            for span in bc_soup.find_all(['span','div'], class_=_re.compile(r'last.?price|price.?value|quote.?price', _re.I)):
                txt = span.get_text(strip=True).replace('%','')
                if _re.match(r'^[\d.]+$', txt):
                    val_str = txt
                    break
        if val_str:
            val = round(float(val_str), 2)
            P[placeholder] = f'{val:.2f}%'
            print(f"  {desc} ({symbol}): {val:.2f}%")
        else:
            P[placeholder] = 'N/A'
            print(f"  WARNING {symbol}: value not found in page")
    except Exception as _e:
        P[placeholder] = 'N/A'
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

    return (f'<tr>'
            f'<td>{i}</td>'
            f'<td><strong>{s["ticker"]}</strong></td>'
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

# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5A/5B: FINVIZ SECTOR (removed) + INDUSTRY (scraped via requests)
# ═══════════════════════════════════════════════════════════════════════════════
print("[Step 5A/5B] Finviz Industry data (requests)...")
P["IMG_5A_SECTORS"] = ""  # Sector screenshot removed

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
        _chg_idx = _col_names.index("Change")
        _name_idx = _col_names.index("Name")
        _stocks_idx = _col_names.index("Stocks") if "Stocks" in _col_names else None
        _rows_data = []
        for _row in _data_table.find_all("tr")[1:]:
            _cells = [c.get_text(strip=True) for c in _row.find_all("td")]
            if len(_cells) > _chg_idx:
                _rows_data.append(_cells)
        # Top 10 gainers (already sorted desc by change)
        _top10 = _rows_data[:10]
        # Bottom 5 losers
        _bot5 = [r for r in _rows_data if r[_chg_idx].startswith("-")][-5:]
        def _row_html(cells, idx):
            name = cells[_name_idx]
            chg = cells[_chg_idx]
            stocks = cells[_stocks_idx] if _stocks_idx else ""
            color = "#2ecc71" if not chg.startswith("-") else "#e74c3c"
            return f"""<tr>
  <td style="color:#8b949e;padding:4px 8px;">{idx}</td>
  <td style="color:#e6edf3;padding:4px 8px;font-weight:600;">{name}</td>
  <td style="color:#8b949e;padding:4px 8px;">{stocks}</td>
  <td style="color:{color};padding:4px 8px;font-weight:700;">{chg}</td>
</tr>"""
        _rows_html_top = "".join([_row_html(r, i+1) for i, r in enumerate(_top10)])
        _rows_html_bot = "".join([_row_html(r, len(_rows_data)-4+i) for i, r in enumerate(_bot5)])
        _industry_html = f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
<thead><tr>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">#</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">Industry</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">Stocks</th>
  <th style="color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;">1D Change</th>
</tr></thead>
<tbody>
<tr><td colspan="4" style="color:#f39c12;padding:6px 8px;font-weight:700;border-bottom:1px solid #30363d;">Top 10 Gainers</td></tr>
{_rows_html_top}
<tr><td colspan="4" style="color:#e74c3c;padding:6px 8px;font-weight:700;border-bottom:1px solid #30363d;">Bottom 5 Losers</td></tr>
{_rows_html_bot}
</tbody></table>"""
        print(f"  ✅ Finviz Industry: {len(_rows_data)} industries scraped")
    else:
        print("  WARNING: Industry table not found")
except Exception as _e:
    print(f"  WARNING Finviz Industry: {_e}")

P["IMG_5B_INDUSTRY"] = _industry_html

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6A: ADVANCE/DECLINE RATIO (StockCharts Market Summary)
# Source: https://stockcharts.com/docs/doku.php?id=market_summary
# Scrapes Advancing/Declining counts for S&P 500, Nasdaq 100, DJIA, Russell 2000
# Calculates AD Ratio = Advancing ÷ Declining for each index
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6A] StockCharts A/D Ratio...")

from bs4 import BeautifulSoup as BS

AD_INDICES = [
    ('SP500',   'S&P 500',     'sp500'),
    ('NDX100',  'Nasdaq 100',  'ndx'),
    ('DJIA',    'DJIA',        'djia'),
    ('RUT',     'Russell 2000','rut'),
]

ad_rows_html = ''
try:
    sc_resp = requests.get(
        'https://stockcharts.com/docs/doku.php?id=market_summary',
        headers=req_headers, timeout=15
    )
    sc_soup = BS(sc_resp.text, 'html.parser')

    # StockCharts Market Summary page has a table with Advancing/Declining columns
    # Find all tables and look for one with 'Advancing' and 'Declining' headers
    ad_data = {}  # key -> {'adv': int, 'dec': int, 'unch': int}
    for tbl in sc_soup.find_all('table'):
        hdrs = [th.get_text(strip=True).lower() for th in tbl.find_all(['th','td'])[:10]]
        if any('advancing' in h for h in hdrs) and any('declining' in h for h in hdrs):
            rows = tbl.find_all('tr')
            hdr_row = rows[0].find_all(['th','td'])
            hdr_texts = [c.get_text(strip=True).lower() for c in hdr_row]
            adv_idx = next((i for i, h in enumerate(hdr_texts) if 'advancing' in h), None)
            dec_idx = next((i for i, h in enumerate(hdr_texts) if 'declining' in h), None)
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
                adv = safe_int(cells, adv_idx)
                dec = safe_int(cells, dec_idx)
                unch = safe_int(cells, unch_idx)
                for key, label, match in AD_INDICES:
                    if match in row_name or label.lower() in row_name:
                        ad_data[key] = {'label': label, 'adv': adv, 'dec': dec, 'unch': unch}
            break

    # Build HTML table rows for each index
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
        print(f"  {label}: Adv={adv_str} Dec={dec_str} Ratio={ratio_str}")

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
        P[f'AD_{key}_ADV'] = P[f'AD_{key}_DEC'] = P[f'AD_{key}_UNCH'] = P[f'AD_{key}_RATIO'] = 'N/A'

# Keep placeholder for any legacy template references
P['IMG_MARKETINOUT'] = ''

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6B: STOCKBEE T2108 (Google Sheets CSV + screenshot)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6B] Stockbee T2108...")

STOCKBEE_CSV  = 'https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=csv'
STOCKBEE_HTML = 'https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=html&widget=true'

t2108_val = up4_val = dn4_val = r5d_val = r10d_val = None

try:
    r = requests.get(STOCKBEE_CSV, timeout=15)
    rows = list(csv.reader(io.StringIO(r.text)))

    # Find header row (first row containing 'T2108' or 'Date')
    header_idx = 0
    for i, row in enumerate(rows[:5]):
        if any('t2108' in str(c).lower() or 'date' in str(c).lower() for c in row):
            header_idx = i
            break

    hdr  = rows[header_idx]
    data = rows[header_idx + 1]

    # Find columns by keyword
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

# T2108 progress bar color
if t2108_val is not None:
    if t2108_val >= 70:
        t2108_color = '#e74c3c'
        t2108_zone  = 'Overbought'
    elif t2108_val <= 20:
        t2108_color = '#2ecc71'
        t2108_zone  = 'Oversold'
    else:
        t2108_color = '#f1c40f'
        t2108_zone  = 'Neutral'
else:
    t2108_color = '#8b949e'
    t2108_zone  = 'N/A'

P['T2108_COLOR'] = t2108_color
P['T2108_ZONE']  = t2108_zone

# Screenshot the Google Sheets (wide viewport to show T2108 column)
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

spy_d = macro.get('SPY', {})
vix_d = macro.get('VIX', {})

# Determine regime
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

context = f"""
Date: {DATE_DISP}
SPY: ${spy_d.get('price',0):.2f} ({spy_d.get('chg',0):+.2f}%) | vs 20MA: {spy_d.get('vs20',0):+.2f}% | vs 50MA: {spy_d.get('vs50',0):+.2f}% | vs 200MA: {spy_d.get('vs200',0):+.2f}%
VIX: {vix_d.get('price',0):.2f} ({vix_d.get('chg',0):+.2f}%)
Fear & Greed: {P.get('FEAR_GREED','N/A')} ({P.get('FEAR_GREED_RATING','N/A')})
NAAIM: {P.get('NAAIM','N/A')} ({P.get('NAAIM_DATE','N/A')})
T2108: {P.get('T2108','N/A')}% ({P.get('T2108_ZONE','N/A')})
Up 4%+: {P.get('UP4PCT','N/A')} | Down 4%+: {P.get('DOWN4PCT','N/A')}
5D ratio: {P.get('RATIO_5D','N/A')} | 10D ratio: {P.get('RATIO_10D','N/A')}
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
Return JSON with these exact keys:
{
  "bear_points": ["4 bear arguments in Traditional Chinese"],
  "bull_points": ["3 bull arguments in Traditional Chinese"],
  "table_rows": [{"indicator":"indicator name","bull":true/false,"neutral":true/false,"bear":true/false}],
  "guidance": "trading guidance in Traditional Chinese, 2-3 sentences"
}'''
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
  <h3 style="color:#e74c3c; margin:0 0 12px 0;">🐻 空頭論點</h3>
  <ol style="color:#ecf0f1; margin:0; padding-left:20px; line-height:1.7;">
    {bear_li}
  </ol>
</div>
<div style="background:#1c2128; border:1px solid #2ecc71; border-radius:8px; padding:16px; margin-bottom:16px;">
  <h3 style="color:#2ecc71; margin:0 0 12px 0;">🐂 多頭論點</h3>
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

# Save
out_path = REPO / f'{DATE}.html'
with open(out_path, 'w') as f:
    f.write(html)
print(f"  ✅ Saved: {DATE}.html")

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

# ── Report complete — git push is handled by the GitHub Actions workflow ──────
print(f"\n{'='*60}")
print(f"🌐 Report ready: {DATE}.html")
print(f"🌐 https://matt-manus.github.io/swing-trader-daily/{DATE}.html")
print(f"{'='*60}")
print("\n=== Done ===")
