#!/usr/bin/env python3
"""
daily_report.py — Swing Trader Daily Market Summary
====================================================
Single script that generates the complete daily report.

Usage:
    python3 daily_report.py [YYYY-MM-DD]
    If no date given, uses today (HKT).

What it does:
    Step 1   - yfinance macro data (SPY/QQQ/IWM/DIA/VIX/GLD/USO/TLT/TNX/DXY)
    Step 1B  - Finviz news + OpenAI filter
    Step 2   - Fullstack Investor screenshot (Playwright)
    Step 3   - Fear & Greed (CNN API) + NAAIM (Excel download)
    Step 4B  - Sector ETF RSI (Wilder SMMA, sorted high→low)
    Step 4C  - 9x StockCharts breadth screenshots (Playwright, 1600px wide)
    Step 5A  - Finviz sector performance screenshot (sorted by 1D change)
    Step 5B  - Finviz industry leaders screenshot (sorted by 1D change)
    Step 6A  - MarketInOut A/D Ratio screenshot (Playwright)
    Step 6B  - Stockbee T2108 from Google Sheets CSV + screenshot (Playwright)
    Step 7   - Bull vs Bear commentary (OpenAI, Traditional Chinese)
    Final    - Fill TEMPLATE.html, upload CDN, push GitHub
"""

import os, sys, json, re, time, subprocess, io, csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO = Path('/home/ubuntu/swing-trader-daily')
EOD  = Path('/home/ubuntu/eod_data')
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
    from datetime import date as date_cls
    REPORT_DATE = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
else:
    REPORT_DATE = now_hkt.date()

DATE        = REPORT_DATE.strftime('%Y-%m-%d')
DATE_DISP   = REPORT_DATE.strftime('%a %b %-d, %Y')   # Mon Mar 24, 2026
DATE_SHORT  = REPORT_DATE.strftime('%b %-d, %Y')       # Mar 24, 2026
DATE_MMDD   = REPORT_DATE.strftime('%b %-d')           # Mar 24
REPORT_TIME = f"{now_hkt.strftime('%H:%M')} HKT ({now_et.strftime('%H:%M')} ET)"

print(f"=== Daily Report: {DATE} ===")
print(f"    Time: {REPORT_TIME}")

# ── Placeholder dict ───────────────────────────────────────────────────────────
P = {
    'REPORT_DATE':         DATE,
    'REPORT_DATE_DISPLAY': DATE_DISP,
    'REPORT_DATE_SHORT':   DATE_SHORT,
    'REPORT_DATE_MMDD':    DATE_MMDD,
    'REPORT_TIME':         REPORT_TIME,
    'SCREENSHOT_DATE':     DATE_SHORT,
}

# ── Helper: run Playwright script ──────────────────────────────────────────────
def run_playwright(script_content, timeout=120):
    """Write script to /tmp and run it, return (success, stdout, stderr)"""
    path = '/tmp/pw_script.py'
    with open(path, 'w') as f:
        f.write(script_content)
    r = subprocess.run(['python3', path], capture_output=True, text=True, timeout=timeout)
    return r.returncode == 0, r.stdout, r.stderr

# ── Helper: upload to CDN ──────────────────────────────────────────────────────
def upload_cdn(filepath):
    """Upload file to CDN, return public URL or None"""
    if not Path(filepath).exists():
        print(f"  ⚠️  File not found: {filepath}")
        return None
    r = subprocess.run(['manus-upload-file', str(filepath)], capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        for line in r.stdout.strip().split('\n'):
            if 'https://' in line:
                url = line.strip().split()[-1]
                print(f"  ✅ CDN: {Path(filepath).name} → ...{url[-35:]}")
                return url
    print(f"  ⚠️  CDN upload failed: {r.stderr[-100:]}")
    return None

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

def badge_ma(price, ma20, ma50, ma200):
    if price < ma20 and price < ma50 and price < ma200:
        return 'badge-bear', 'BELOW ALL MAs'
    if price > ma20 and price > ma50 and price > ma200:
        return 'badge-bull', 'ABOVE ALL MAs'
    if price < ma20 and price < ma50:
        return 'badge-warn', 'BELOW 20/50MA'
    if price < ma200:
        return 'badge-bear', 'BELOW 200MA'
    return 'badge-warn', 'MIXED'

MACRO_TICKERS = {
    'SPY': 'SPY', 'QQQ': 'QQQ', 'IWM': 'IWM', 'DIA': 'DIA',
    'VIX': '^VIX', 'GLD': 'GLD', 'USO': 'USO', 'TLT': 'TLT',
    'TNX': '^TNX', 'DXY': 'DX-Y.NYB',
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
        print(f"  ⚠️  {key}: {e}")

def fill_ticker_placeholders(key):
    d = macro.get(key)
    if not d:
        return
    bc, sig = badge_ma(d['price'], d['ma20'], d['ma50'], d['ma200'])
    P[f'{key}_PRICE']     = f"{d['price']:.2f}"
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

for key in ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'USO', 'TLT', 'TNX', 'DXY']:
    fill_ticker_placeholders(key)

if 'VIX' in macro:
    d = macro['VIX']
    P['VIX']           = f"{d['price']:.2f}"
    P['VIX_CHG']       = fmt(d['chg'])
    P['VIX_CHG_COLOR'] = color(-d['chg'])  # VIX up = bearish = red

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1B: NEWS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 1B] Finviz news + OpenAI filter...")

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

NEWS_TICKERS = ['SPY','QQQ','IWM','DIA','XLE','XLK','XLF','XLV','XLB',
                'NVDA','AAPL','MSFT','META','AMZN','TSLA','GOOGL',
                'GLD','TLT','USO','UUP']

req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
all_headlines = []

for ticker in NEWS_TICKERS:
    try:
        resp = requests.get(f'https://finviz.com/quote.ashx?t={ticker}',
                            headers=req_headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        news_table = soup.find(id='news-table')
        if not news_table:
            continue
        current_date = None
        for row in news_table.find_all('tr'):
            td_date = row.find('td', {'align': 'right'})
            td_news = row.find('td', {'align': 'left'})
            if not td_news:
                continue
            if td_date:
                dt = td_date.text.strip()
                if len(dt) > 8:
                    current_date = dt.split()[0]
            if current_date and ('Today' in current_date or
                                  REPORT_DATE.strftime('%b-%d-%y').lstrip('0').replace('-0','-') in current_date):
                link = td_news.find('a')
                if link:
                    all_headlines.append({'ticker': ticker, 'headline': link.text.strip()})
        time.sleep(0.2)
    except Exception as e:
        pass

print(f"  Collected {len(all_headlines)} headlines")

filtered_news_html = ''
if all_headlines:
    try:
        client = OpenAI()
        headlines_text = '\n'.join([f"[{h['ticker']}] {h['headline']}" for h in all_headlines[:80]])
        resp = client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=[{'role': 'user', 'content': f"""Today is {DATE}. SPY {macro.get('SPY',{}).get('chg',0):+.2f}%, VIX={macro.get('VIX',{}).get('price','?'):.1f}.
Select 5-7 most market-moving headlines. Return JSON array:
[{{"impact":"HIGH|MEDIUM","ticker":"...","headline":"...","reason":"one sentence"}}]

Headlines:
{headlines_text}"""}],
            temperature=0.3
        )
        raw = resp.choices[0].message.content.strip()
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        if m:
            items = json.loads(m.group())
            rows = []
            for item in items:
                impact = item.get('impact', 'MEDIUM')
                color_map = {'HIGH': '#e74c3c', 'MEDIUM': '#f39c12'}
                badge_map = {'HIGH': 'badge-bear', 'MEDIUM': 'badge-warn'}
                c = color_map.get(impact, '#3498db')
                b = badge_map.get(impact, 'badge-neutral')
                rows.append(f'''  <div style="border-left:3px solid {c}; padding:8px 12px; margin-bottom:8px; background:#161b22; border-radius:0 6px 6px 0;">
    <span class="badge {b}" style="font-size:10px;">{impact}</span>
    <span style="color:#8b949e; font-size:11px; margin-left:6px;">[{item.get('ticker','')}]</span>
    <strong style="color:#e6edf3; font-size:13px; margin-left:4px;">{item.get('headline','')}</strong>
    <div style="color:#8b949e; font-size:12px; margin-top:4px;">📌 {item.get('reason','')}</div>
  </div>''')
            filtered_news_html = '\n'.join(rows)
            print(f"  AI filtered to {len(items)} stories")
    except Exception as e:
        print(f"  ⚠️  OpenAI news: {e}")

if not filtered_news_html:
    filtered_news_html = '<div style="color:#8b949e; padding:12px;">⚠️ News data unavailable.</div>'

P['NEWS_ITEMS'] = filtered_news_html

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: FULLSTACK INVESTOR SCREENSHOT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 2] Fullstack Investor screenshot...")

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright
from PIL import Image

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{'width': 1400, 'height': 900}})
        await page.goto('https://fullstackinvestor.co/market-model',
                        wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path='/home/ubuntu/eod_data/{DATE}_fullstack_top.png')
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='/home/ubuntu/eod_data/{DATE}_fullstack_bot.png')
        await browser.close()

asyncio.run(main())

top = Image.open('/home/ubuntu/eod_data/{DATE}_fullstack_top.png')
bot = Image.open('/home/ubuntu/eod_data/{DATE}_fullstack_bot.png')
combined = Image.new('RGB', (top.width, top.height + bot.height))
combined.paste(top, (0, 0))
combined.paste(bot, (0, top.height))
combined.save('/home/ubuntu/eod_data/{DATE}_fullstack.png')
print('done')
""", timeout=60)

if ok and (EOD / f'{DATE}_fullstack.png').exists():
    url = upload_cdn(EOD / f'{DATE}_fullstack.png')
    P['IMG_FULLSTACK'] = url or 'MISSING'
    print("  ✅ Fullstack screenshot done")
else:
    P['IMG_FULLSTACK'] = 'MISSING'
    print(f"  ⚠️  Fullstack failed: {err[-200:]}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: FEAR & GREED + NAAIM
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 3] Fear & Greed + NAAIM...")

# Fear & Greed via CNN API
try:
    r = requests.get('https://production.dataviz.cnn.io/index/fearandgreed/graphdata',
                     headers=req_headers, timeout=10)
    fg = r.json()['fear_and_greed']
    fg_score = int(float(fg['score']))
    fg_rating = fg.get('rating', 'N/A').replace('_', ' ').title()
    P['FEAR_GREED']        = str(fg_score)
    P['FEAR_GREED_RATING'] = fg_rating
    print(f"  Fear & Greed: {fg_score} ({fg_rating})")
except Exception as e:
    print(f"  ⚠️  Fear & Greed: {e}")
    P['FEAR_GREED']        = 'N/A'
    P['FEAR_GREED_RATING'] = 'N/A'

# NAAIM — download Excel, read row 2 (most recent, newest-first)
try:
    import openpyxl
    naaim_url = 'https://naaim.org/wp-content/uploads/2026/03/NAAIM-Exposure-Index.xlsx'
    r = requests.get(naaim_url, headers=req_headers, timeout=15)
    wb = openpyxl.load_workbook(io.BytesIO(r.content))
    ws = wb.active
    row2 = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))[0]
    naaim_val  = round(float(row2[3] if row2[3] is not None else row2[1]), 2)
    naaim_date = row2[0]
    naaim_date_str = naaim_date.strftime('%b %-d, %Y') if hasattr(naaim_date, 'strftime') else str(naaim_date)
    P['NAAIM']      = str(naaim_val)
    P['NAAIM_DATE'] = naaim_date_str
    print(f"  NAAIM: {naaim_val} ({naaim_date_str})")
except Exception as e:
    print(f"  ⚠️  NAAIM: {e}")
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

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright

CHARTS = {json.dumps(BREADTH)}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, symbol in CHARTS:
            page = await browser.new_page(viewport={{'width': 1600, 'height': 700}})
            url = f'https://stockcharts.com/h-sc/ui?s={{symbol}}&p=D&yr=1&mn=0&dy=0'
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f'/home/ubuntu/eod_data/{DATE}_{{name}}.png')
                print(f'done:{{name}}')
            except Exception as e:
                print(f'fail:{{name}}:{{e}}')
            await page.close()
        await browser.close()

asyncio.run(main())
""", timeout=150)

print(out)

# Upload each breadth chart
for name, _ in BREADTH:
    path = EOD / f'{DATE}_{name}.png'
    if path.exists():
        url = upload_cdn(path)
        P[f'IMG_{name}'] = url or 'MISSING'
    else:
        P[f'IMG_{name}'] = 'MISSING'
        print(f"  ⚠️  Missing: {name}")

# Breadth values — these are read from the screenshots visually.
# Set to N/A; they will be visible in the screenshots.
for name, _ in BREADTH:
    P[name] = 'N/A'

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
        print(f"  ⚠️  {ticker}: {e}")

sector_rows.sort(key=lambda x: x['rsi'], reverse=True)
print(f"  Top sector: {sector_rows[0]['ticker']} RSI={sector_rows[0]['rsi']}")

def sector_row_html(i, s):
    chg_cls = 'green' if s['chg'] >= 0 else 'red'
    chg_str = f"{s['chg']:+.2f}%"
    rsi = s['rsi']
    rsi_badge = 'badge-warn' if rsi >= 70 else ('badge-bear' if rsi <= 30 else 'badge-neutral')
    signal = 'OVERBOUGHT' if rsi >= 70 else ('OVERSOLD' if rsi <= 30 else 'NEUTRAL')
    sig_cls = rsi_badge

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
            f'<td><span class="badge {sig_cls}">{signal}</span></td>'
            f'</tr>\n')

SECTOR_ROWS_HTML = ''
for i, s in enumerate(sector_rows, 1):
    SECTOR_ROWS_HTML += sector_row_html(i, s)

P['SECTOR_ROWS'] = SECTOR_ROWS_HTML

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5A/5B: FINVIZ SECTOR + INDUSTRY SCREENSHOTS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 5A/5B] Finviz screenshots...")

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright
from PIL import Image

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 5A: Sectors sorted by 1D change
        page = await browser.new_page(
            viewport={{'width': 1600, 'height': 900}},
            extra_http_headers={{'User-Agent': UA}})
        await page.goto('https://finviz.com/groups.ashx?g=sector&o=-change&v=140',
                        wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/home/ubuntu/eod_data/{DATE}_5A_raw.png')
        await page.close()
        
        # 5B: Industries sorted by 1D change
        page = await browser.new_page(
            viewport={{'width': 1600, 'height': 1400}},
            extra_http_headers={{'User-Agent': UA}})
        await page.goto('https://finviz.com/groups.ashx?g=industry&o=-change&v=140',
                        wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/home/ubuntu/eod_data/{DATE}_5B_raw.png')
        await page.close()
        
        await browser.close()

asyncio.run(main())

# Crop to table area
for suffix, top_crop, bot_crop in [('5A', 110, 420), ('5B', 110, 900)]:
    try:
        img = Image.open(f'/home/ubuntu/eod_data/{DATE}_{{suffix}}_raw.png')
        w, h = img.size
        cropped = img.crop((0, top_crop, w, min(h, bot_crop)))
        cropped.save(f'/home/ubuntu/eod_data/{DATE}_{{suffix}}.png')
        print(f'done:{{suffix}}')
    except Exception as e:
        print(f'fail:{{suffix}}:{{e}}')
""", timeout=90)

print(out)
for suffix, key in [('5A', 'IMG_5A_SECTORS'), ('5B', 'IMG_5B_INDUSTRY')]:
    path = EOD / f'{DATE}_{suffix}.png'
    if path.exists():
        url = upload_cdn(path)
        P[key] = url or 'MISSING'
    else:
        P[key] = 'MISSING'
        print(f"  ⚠️  Missing: {suffix}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6A: MARKETINOUT A/D RATIO SCREENSHOT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6A] MarketInOut A/D Ratio screenshot...")

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{'width': 1400, 'height': 800}})
        await page.goto('https://www.marketinout.com/advance_decline.php',
                        wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path='/home/ubuntu/eod_data/{DATE}_marketinout.png')
        await browser.close()
        print('done')

asyncio.run(main())
""", timeout=60)

path = EOD / f'{DATE}_marketinout.png'
if path.exists():
    url = upload_cdn(path)
    P['IMG_MARKETINOUT'] = url or 'MISSING'
    print("  ✅ MarketInOut done")
else:
    P['IMG_MARKETINOUT'] = 'MISSING'
    print(f"  ⚠️  MarketInOut failed: {err[-150:]}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6B: STOCKBEE T2108 (Google Sheets CSV + screenshot)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6B] Stockbee T2108...")

STOCKBEE_CSV = 'https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=csv'
STOCKBEE_HTML = 'https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=html&widget=true'

t2108_val = up4_val = dn4_val = r5d_val = r10d_val = None

try:
    r = requests.get(STOCKBEE_CSV, timeout=15)
    rows = list(csv.reader(io.StringIO(r.text)))
    
    # Find header row
    header_idx = 0
    for i, row in enumerate(rows[:5]):
        if any('t2108' in str(c).lower() or 'date' in str(c).lower() for c in row):
            header_idx = i
            break
    
    hdr = rows[header_idx]
    data = rows[header_idx + 1]
    
    def find_col(keywords):
        for i, h in enumerate(hdr):
            if all(k in str(h).lower() for k in keywords):
                return i
        return None
    
    t2108_col = find_col(['t2108']) or find_col(['t21'])
    up4_col   = next((i for i, h in enumerate(hdr) if 'up' in str(h).lower() and '4' in str(h)), None)
    dn4_col   = next((i for i, h in enumerate(hdr) if 'down' in str(h).lower() and '4' in str(h)), None)
    r5d_col   = next((i for i, h in enumerate(hdr) if '5' in str(h) and 'ratio' in str(h).lower()), None)
    r10d_col  = next((i for i, h in enumerate(hdr) if '10' in str(h) and 'ratio' in str(h).lower()), None)
    
    if t2108_col is not None:
        t2108_val = round(float(data[t2108_col]), 2)
    if up4_col is not None:
        up4_val = int(float(data[up4_col]))
    if dn4_col is not None:
        dn4_val = int(float(data[dn4_col]))
    if r5d_col is not None:
        r5d_val = round(float(data[r5d_col]), 2)
    if r10d_col is not None:
        r10d_val = round(float(data[r10d_col]), 2)
    
    print(f"  T2108: {t2108_val}% | Up4%+: {up4_val} | Down4%+: {dn4_val}")
    print(f"  5D ratio: {r5d_val} | 10D ratio: {r10d_val}")

except Exception as e:
    print(f"  ⚠️  Stockbee CSV: {e}")

P['T2108']     = str(t2108_val) if t2108_val is not None else 'N/A'
P['UP4PCT']    = str(up4_val)   if up4_val   is not None else 'N/A'
P['DOWN4PCT']  = str(dn4_val)   if dn4_val   is not None else 'N/A'
P['RATIO_5D']  = str(r5d_val)   if r5d_val   is not None else 'N/A'
P['RATIO_10D'] = str(r10d_val)  if r10d_val  is not None else 'N/A'

# Screenshot the Google Sheets (wide viewport to show T2108 column)
ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{'width': 1800, 'height': 600}})
        await page.goto('{STOCKBEE_HTML}', wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        # Scroll right to show T2108 column
        await page.evaluate('''
            var c = document.querySelector(".waffle-container") || document.querySelector("iframe");
            if (c) c.scrollLeft = 400;
        ''')
        await page.wait_for_timeout(500)
        await page.screenshot(path='/home/ubuntu/eod_data/{DATE}_t2108_sheet.png')
        await browser.close()
        print('done')

asyncio.run(main())
""", timeout=60)

path = EOD / f'{DATE}_t2108_sheet.png'
if path.exists():
    url = upload_cdn(path)
    P['IMG_T2108_SHEET'] = url or 'MISSING'
    print("  ✅ T2108 screenshot done")
else:
    P['IMG_T2108_SHEET'] = 'MISSING'
    print(f"  ⚠️  T2108 screenshot failed")

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
if isinstance(P.get('FEAR_GREED'), str) and P['FEAR_GREED'].isdigit():
    if int(P['FEAR_GREED']) < 25: regime_score += 1

REGIME = 'BEARISH' if regime_score >= 6 else ('BEARISH-TO-NEUTRAL' if regime_score >= 4 else ('NEUTRAL' if regime_score >= 2 else 'BULLISH'))
P['REGIME'] = REGIME

context = f"""
Date: {DATE_DISP}
SPY: ${spy_d.get('price','?'):.2f} ({spy_d.get('chg',0):+.2f}%) | vs 20MA: {spy_d.get('vs20',0):+.2f}% | vs 50MA: {spy_d.get('vs50',0):+.2f}% | vs 200MA: {spy_d.get('vs200',0):+.2f}%
VIX: {vix_d.get('price','?'):.2f} ({vix_d.get('chg',0):+.2f}%)
Fear & Greed: {P.get('FEAR_GREED','N/A')} ({P.get('FEAR_GREED_RATING','N/A')})
NAAIM: {P.get('NAAIM','N/A')} ({P.get('NAAIM_DATE','N/A')})
T2108: {P.get('T2108','N/A')}%
Up 4%+: {P.get('UP4PCT','N/A')} | Down 4%+: {P.get('DOWN4PCT','N/A')}
5D ratio: {P.get('RATIO_5D','N/A')} | 10D ratio: {P.get('RATIO_10D','N/A')}
Top sector by RSI: {sector_rows[0]['ticker']} ({sector_rows[0]['sector']}) RSI={sector_rows[0]['rsi']}
Regime: {REGIME}
"""

try:
    client = OpenAI()
    resp = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[{
            'role': 'system',
            'content': '''You are a professional swing trader analyst. Generate a bull vs bear analysis in Traditional Chinese (繁體中文).
Return JSON:
{
  "bear_points": ["4 bear arguments"],
  "bull_points": ["3 bull arguments"],
  "table_rows": [{"indicator":"...", "bull":true/false/null, "neutral":true/false/null, "bear":true/false/null}],
  "guidance": "trading guidance in Traditional Chinese"
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
    print(f"  ⚠️  OpenAI commentary: {e}")
    bear_pts = bull_pts = table_rows = []
    guidance = ''

bear_li = ''.join(f'<li style="margin-bottom:6px;">{p}</li>\n' for p in bear_pts)
bull_li = ''.join(f'<li style="margin-bottom:6px;">{p}</li>\n' for p in bull_pts)
table_body = ''
for row in table_rows:
    b = '✔' if row.get('bull')    else ''
    n = '✔' if row.get('neutral') else ''
    br = '✔' if row.get('bear')   else ''
    table_body += f'<tr style="border-bottom:1px solid #333;"><td style="padding:10px;">{row.get("indicator","")}</td><td style="text-align:center;color:#2ecc71;">{b}</td><td style="text-align:center;color:#f1c40f;">{n}</td><td style="text-align:center;color:#e74c3c;">{br}</td></tr>\n'

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
    print(f"  ⚠️  Unfilled placeholders: {set(remaining)}")
else:
    print("  ✅ All placeholders filled")

# Save
out_path = REPO / f'{DATE}.html'
with open(out_path, 'w') as f:
    f.write(html)
print(f"  ✅ Saved: {out_path}")

# ── Update MARKET_HISTORY.md ───────────────────────────────────────────────────
history_path = REPO / 'MARKET_HISTORY.md'
new_entry = (f"| [{DATE}](https://matt-manus.github.io/swing-trader-daily/{DATE}.html) "
             f"| {REGIME} "
             f"| ${spy_d.get('price','?'):.2f} ({spy_d.get('chg',0):+.2f}%) "
             f"| {vix_d.get('price','?'):.2f} "
             f"| {P.get('FEAR_GREED','N/A')} "
             f"| {P.get('NAAIM','N/A')} "
             f"| {P.get('T2108','N/A')}% |\n")

try:
    with open(history_path) as f:
        history = f.read()
    marker = '|---|---|---|---|---|---|---|\n'
    if marker in history:
        history = history.replace(marker, marker + new_entry, 1)
        with open(history_path, 'w') as f:
            f.write(history)
        print("  ✅ MARKET_HISTORY.md updated")
except Exception as e:
    print(f"  ⚠️  MARKET_HISTORY: {e}")

# ── Git push ───────────────────────────────────────────────────────────────────
print("\n[Git] Committing and pushing...")
os.chdir(REPO)
subprocess.run(['git', 'config', 'user.email', 'manus@manus.ai'], check=True)
subprocess.run(['git', 'config', 'user.name', 'Manus'], check=True)
subprocess.run(['git', 'add', f'{DATE}.html', 'MARKET_HISTORY.md'], check=True)
r = subprocess.run(['git', 'commit', '-m', f'Daily report {DATE}: {REGIME}'],
                   capture_output=True, text=True)
print(r.stdout.strip())
r = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
if r.returncode == 0:
    print(f"  ✅ Pushed to GitHub")
    print(f"\n{'='*60}")
    print(f"🌐 https://matt-manus.github.io/swing-trader-daily/{DATE}.html")
    print(f"{'='*60}")
else:
    print(f"  ⚠️  Push failed: {r.stderr}")

print("\n=== Done ===")
