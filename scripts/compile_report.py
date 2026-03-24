#!/usr/bin/env python3
"""Compile the daily HTML report from collected data"""
import json
import os
import shutil
from datetime import datetime
import pytz

# Setup dates and times
hk_tz = pytz.timezone('Asia/Hong_Kong')
et_tz = pytz.timezone('US/Eastern')
now = datetime.now(pytz.utc)
hk_time = now.astimezone(hk_tz).strftime('%Y-%m-%d %H:%M:%S HKT')
et_time = now.astimezone(et_tz).strftime('%Y-%m-%d %H:%M:%S ET')

# Load data
with open('/home/ubuntu/eod_data/mar24_data.json') as f:
    market_data = json.load(f)
with open('/home/ubuntu/eod_data/mar24_news.json') as f:
    news_data = json.load(f)
with open('/home/ubuntu/eod_data/sector_rsi.json') as f:
    sector_rsi = json.load(f)
with open('/home/ubuntu/eod_data/industry_leaders.json') as f:
    industry_leaders = json.load(f)

# Copy images to repo
os.makedirs('/home/ubuntu/swing-trader-daily/images', exist_ok=True)
images_to_copy = [
    'fear_greed_mar24.png',
    'spxa20r.png', 'spxa50r.png', 'spxa200r.png',
    'ndxa20r.png', 'ndxa50r.png', 'ndxa200r.png',
    'stockbee_mm_mar24.png'
]
for img in images_to_copy:
    src = f'/home/ubuntu/eod_data/{img}'
    if os.path.exists(src):
        dst = f'/home/ubuntu/swing-trader-daily/images/{img.replace("_mar24", "")}'
        shutil.copy(src, dst)

# Read template
with open('/home/ubuntu/swing-trader-daily/2026-03-23.html') as f:
    template = f.read()

# Build News HTML
news_html = ""
for item in news_data.get('filtered_news', []):
    news_html += f"<li><strong>{item.get('impact', '')}</strong> | {item.get('tickers', '')}: {item.get('headline', '')} - {item.get('why_it_matters', '')}</li>\n"

# Build Sector RSI HTML
sector_html = ""
for item in sorted(sector_rsi, key=lambda x: x['rsi'] if x['rsi'] is not None else 0, reverse=True):
    if item['rsi'] is None: continue
    color = "green" if item['rsi'] > 70 else "red" if item['rsi'] < 30 else "black"
    sector_html += f"<tr><td>{item['sector']} ({item['ticker']})</td><td>{item['close']}</td><td>{item['pct_1d']}%</td><td style='color:{color}; font-weight:bold;'>{item['rsi']}</td></tr>\n"

# Build Industry Leaders HTML
leaders_html = ""
for item in industry_leaders[:10]:
    leaders_html += f"<li>{item['name']}: {item['change_1d']}</li>\n"

# Replace values in template
html = template
html = html.replace('2026-03-23', '2026-03-24')
html = html.replace('Market Summary 2026-03-23 06:15:00 HKT / 2026-03-22 18:15:00 ET', f'Market Summary {hk_time} / {et_time}')

# Update SPY/VIX
spy = market_data['SPY']
vix = market_data['VIX']
html = html.replace('<strong>SPY:</strong> $655.42 (-0.36%)', f"<strong>SPY:</strong> ${spy['close']} ({spy['pct_change']}%)")
html = html.replace('<strong>VIX:</strong> 26.15 (+1.40%)', f"<strong>VIX:</strong> ${vix['close']} ({vix['pct_change']}%)")

# Update News
import re
html = re.sub(r'<ul id="news-list">.*?</ul>', f'<ul id="news-list">\n{news_html}</ul>', html, flags=re.DOTALL)

# Update Fear & Greed and NAAIM
html = html.replace('Fear & Greed Index: 16 (Extreme Fear)', 'Fear & Greed Index: 14 (Extreme Fear)')
html = html.replace('NAAIM Exposure Index: 60.24', 'NAAIM Exposure Index: 60.24') # Same value

# Update Breadth values
html = html.replace('<li>S&P 500 above 20MA: 20.20%</li>', '<li>S&P 500 above 20MA: 19.80%</li>')
html = html.replace('<li>S&P 500 above 50MA: 26.60%</li>', '<li>S&P 500 above 50MA: 25.80%</li>')
html = html.replace('<li>S&P 500 above 200MA: 50.00%</li>', '<li>S&P 500 above 200MA: 49.20%</li>')
html = html.replace('<li>Nasdaq 100 above 20MA: 18.00%</li>', '<li>Nasdaq 100 above 20MA: 17.00%</li>')
html = html.replace('<li>Nasdaq 100 above 50MA: 23.00%</li>', '<li>Nasdaq 100 above 50MA: 22.00%</li>')
html = html.replace('<li>Nasdaq 100 above 200MA: 44.00%</li>', '<li>Nasdaq 100 above 200MA: 43.00%</li>')

# Update Sector RSI table
html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n{sector_html}</tbody>', html, flags=re.DOTALL)

# Update Industry Leaders
html = re.sub(r'<ul id="industry-leaders">.*?</ul>', f'<ul id="industry-leaders">\n{leaders_html}</ul>', html, flags=re.DOTALL)

# Update T2108
html = html.replace('<li>Stocks Up 4%+: 235</li>', '<li>Stocks Up 4%+: 215</li>')
html = html.replace('<li>Stocks Down 4%+: 85</li>', '<li>Stocks Down 4%+: 281</li>')

# Bull/Bear Commentary
bull_case = """
<ul>
    <li>Energy sector (XLE) showing extreme relative strength with RSI at 80.8, providing a pocket of leadership.</li>
    <li>Fear & Greed Index is at 14 (Extreme Fear), which often acts as a contrarian indicator for short-term bounces.</li>
    <li>Market breadth is extremely washed out (Nasdaq 100 > 20MA at just 17%), setting up potential mean reversion.</li>
</ul>
"""
bear_case = """
<ul>
    <li>SPY remains below all key moving averages (10, 20, 50, 200) with a declining trend.</li>
    <li>VIX remains elevated at 26.95, indicating ongoing market stress and implied volatility.</li>
    <li>Breadth thrust indicator flipped negative again with 281 stocks down 4%+ vs only 215 up 4%+.</li>
    <li>Defensive/commodity sectors (Energy, Materials) are leading while Tech/Growth lags, a classic risk-off rotation.</li>
</ul>
"""
html = re.sub(r'<div id="bull-case">.*?</div>', f'<div id="bull-case">\n{bull_case}</div>', html, flags=re.DOTALL)
html = re.sub(r'<div id="bear-case">.*?</div>', f'<div id="bear-case">\n{bear_case}</div>', html, flags=re.DOTALL)

# Save the new file
with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w') as f:
    f.write(html)

print("Report generated: 2026-03-24.html")
