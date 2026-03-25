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

for key in ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'USO', 'TLT', 'TNX', 'DXY']:
    fill_ticker_placeholders(key)

if 'VIX' in macro:
    d = macro['VIX']
    P['VIX']           = f"{d['price']:.2f}"
    P['VIX_CHG']       = fmt(d['chg'])
    P['VIX_CHG_COLOR'] = color(-d['chg'])  # VIX up = bearish

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
                                  REPORT_DATE.strftime('%b-%d-%y') in current_date):
                link = td_news.find('a')
                if link:
                    all_headlines.append({'ticker': ticker, 'headline': link.text.strip()})
        time.sleep(0.2)
    except Exception:
        pass

print(f"  Collected {len(all_headlines)} headlines")

filtered_news_html = ''
if all_headlines:
    try:
        client = OpenAI()
        headlines_text = '\n'.join([f"[{h['ticker']}] {h['headline']}" for h in all_headlines[:80]])
        spy_chg = macro.get('SPY', {}).get('chg', 0)
        vix_val = macro.get('VIX', {}).get('price', 0)
        resp = client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=[{'role': 'user', 'content': f"""Today is {DATE}. SPY {spy_chg:+.2f}%, VIX={vix_val:.1f}.
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
        print(f"  WARNING OpenAI news: {e}")

if not filtered_news_html:
    filtered_news_html = '<div style="color:#8b949e; padding:12px;">⚠️ News data unavailable.</div>'

P['NEWS_ITEMS'] = filtered_news_html

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: FULLSTACK INVESTOR SCREENSHOT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 2] Fullstack Investor screenshot...")

fullstack_path = IMG_DIR / 'fullstack.png'

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
        await page.screenshot(path='/tmp/fs_top.png')
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='/tmp/fs_bot.png')
        await browser.close()

asyncio.run(main())

top = Image.open('/tmp/fs_top.png')
bot = Image.open('/tmp/fs_bot.png')
combined = Image.new('RGB', (top.width, top.height + bot.height))
combined.paste(top, (0, 0))
combined.paste(bot, (0, top.height))
combined.save('{fullstack_path}')
print('done')
""", timeout=60)

if fullstack_path.exists():
    P['IMG_FULLSTACK'] = img_path('fullstack.png')
    print("  ✅ Fullstack screenshot done")
else:
    P['IMG_FULLSTACK'] = ''
    print(f"  WARNING Fullstack failed: {err[-150:]}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: FEAR & GREED + NAAIM
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 3] Fear & Greed + NAAIM...")

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

# Breadth values shown in screenshots; set display to N/A
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
# STEP 5A/5B: FINVIZ SECTOR + INDUSTRY SCREENSHOTS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 5A/5B] Finviz screenshots...")

sectors_path   = str(IMG_DIR / '5A_sectors.png')
industry_path  = str(IMG_DIR / '5B_industry.png')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright
from PIL import Image

UA = '{UA}'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # 5A: Sectors sorted by 1D change
        page = await browser.new_page(
            viewport={{'width': 1600, 'height': 900}},
            extra_http_headers={{'User-Agent': UA}})
        try:
            await page.goto('https://finviz.com/groups.ashx?g=sector&o=-change&v=140',
                            wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)
            await page.screenshot(path='/tmp/5A_raw.png')
            img = Image.open('/tmp/5A_raw.png')
            w, h = img.size
            img.crop((0, 110, w, min(h, 420))).save('{sectors_path}')
            print('done:5A')
        except Exception as e:
            print(f'fail:5A:{{e}}')
        await page.close()

        # 5B: Industries sorted by 1D change
        page = await browser.new_page(
            viewport={{'width': 1600, 'height': 1400}},
            extra_http_headers={{'User-Agent': UA}})
        try:
            await page.goto('https://finviz.com/groups.ashx?g=industry&o=-change&v=140',
                            wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)
            await page.screenshot(path='/tmp/5B_raw.png')
            img = Image.open('/tmp/5B_raw.png')
            w, h = img.size
            img.crop((0, 110, w, min(h, 900))).save('{industry_path}')
            print('done:5B')
        except Exception as e:
            print(f'fail:5B:{{e}}')
        await page.close()

        await browser.close()

asyncio.run(main())
""", timeout=90)

print(out)

if (IMG_DIR / '5A_sectors.png').exists():
    P['IMG_5A_SECTORS'] = img_path('5A_sectors.png')
else:
    P['IMG_5A_SECTORS'] = ''
    print("  WARNING 5A screenshot failed")

if (IMG_DIR / '5B_industry.png').exists():
    P['IMG_5B_INDUSTRY'] = img_path('5B_industry.png')
else:
    P['IMG_5B_INDUSTRY'] = ''
    print("  WARNING 5B screenshot failed")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6A: MARKETINOUT A/D RATIO SCREENSHOT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Step 6A] MarketInOut A/D Ratio screenshot...")

marketinout_path = str(IMG_DIR / 'marketinout.png')

ok, out, err = run_playwright(f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{'width': 1400, 'height': 800}})
        try:
            await page.goto('https://www.marketinout.com/advance_decline.php',
                            wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            await page.screenshot(path='{marketinout_path}')
            print('done')
        except Exception as e:
            print(f'fail:{{e}}')
        await browser.close()

asyncio.run(main())
""", timeout=60)

if (IMG_DIR / 'marketinout.png').exists():
    P['IMG_MARKETINOUT'] = img_path('marketinout.png')
    print("  ✅ MarketInOut done")
else:
    P['IMG_MARKETINOUT'] = ''
    print(f"  WARNING MarketInOut failed: {err[-100:]}")

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

# ── Git push ───────────────────────────────────────────────────────────────────
print("\n[Git] Committing and pushing...")
os.chdir(REPO)
subprocess.run(['git', 'config', 'user.email', 'github-actions@github.com'], check=True)
subprocess.run(['git', 'config', 'user.name', 'GitHub Actions'], check=True)
subprocess.run(['git', 'add', f'{DATE}.html', 'MARKET_HISTORY.md',
                f'images/{DATE}/'], check=True)
r = subprocess.run(['git', 'commit', '-m', f'Daily report {DATE}: {REGIME}'],
                   capture_output=True, text=True)
print(r.stdout.strip())
# Pull with rebase to avoid conflicts, then push
subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'],
               capture_output=True, text=True)
r = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
if r.returncode == 0:
    print(f"  ✅ Pushed to GitHub")
    print(f"\n{'='*60}")
    print(f"🌐 https://matt-manus.github.io/swing-trader-daily/{DATE}.html")
    print(f"{'='*60}")
else:
    print(f"  WARNING Push failed: {r.stderr[-200:]}")

print("\n=== Done ===")
