#!/usr/bin/env python3
import json
import os
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

# Read 2026-03-20 template to copy CSS and structure
with open('/home/ubuntu/swing-trader-daily/2026-03-20.html') as f:
    template_lines = f.readlines()

# Extract CSS
css_start = template_lines.index('<style>\n')
css_end = template_lines.index('</style>\n')
css = "".join(template_lines[css_start:css_end+1])

# Build HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Market Summary — March 24, 2026 | {hk_time} / {et_time}</title>
{css}
</head>
<body>
<div class="container">

  <!-- ===== TODAY'S VERDICT ===== -->
  <div class="verdict-box">
    <div class="verdict-title">📊 Market Summary — Mar 24, 2026 | Generated {hk_time} / {et_time}</div>
    <div class="verdict-grid">
      <div class="verdict-item">
        <div class="verdict-label">Market Regime 市場環境</div>
        <div class="verdict-value" style="color:#f85149">⚠ BEARISH (Level 8–9 / 9)</div>
      </div>
      <div class="verdict-item">
        <div class="verdict-label">Fear &amp; Greed Index</div>
        <div class="verdict-value" style="color:#f85149">14 — EXTREME FEAR 😱</div>
      </div>
      <div class="verdict-item">
        <div class="verdict-label">VIX 恐慌指數</div>
        <div class="verdict-value" style="color:#f85149">{market_data['macro']['VIX']['price']} — ELEVATED ⚠ ({market_data['macro']['VIX']['chg_1d']}%)</div>
      </div>
      <div class="verdict-item">
        <div class="verdict-label">SPY vs Key MAs</div>
        <div class="verdict-value" style="color:#f85149">BELOW 10MA, 20MA, 50MA, 200MA</div>
      </div>
      <div class="verdict-action">
        <div style="color:#8b949e; font-size:12px; margin-bottom:4px">📋 ACTION GUIDANCE 交易指引</div>
        <div style="color:#e6edf3; font-size:14px"><strong>No new longs.</strong> VIX remains elevated at {market_data['macro']['VIX']['price']}. SPY ({market_data['indices']['SPY']['price']}, {market_data['indices']['SPY']['chg_1d']}%) closed below all major moving averages. Energy (XLE) remains the sole structural leader with RSI at 80.8. T2108 remains washed out but breadth thrust was negative today (281 down 4%+ vs 215 up 4%+). Wait for VIX &lt;20 before adding exposure.</div>
      </div>
    </div>
  </div>

  <!-- ===== KEY LEVELS ===== -->
  <div class="section">
    <div class="section-title">🔑 關鍵水平 Key Levels to Watch</div>
    <table>
      <tr><th>Level</th><th>Value</th><th>Significance</th><th>Bias</th></tr>
      <tr><td>SPX 200MA</td><td class="red">BREACHED</td><td>SPY remains below 200MA, continuing bearish trend.</td><td><span class="badge badge-bear">BREACHED ⚠</span></td></tr>
      <tr><td>VIX 20</td><td class="gray">Current: {market_data['macro']['VIX']['price']}</td><td>Bearish → Defensive threshold. Must close below for 3+ days</td><td><span class="badge badge-warn">REGIME TRIGGER</span></td></tr>
      <tr><td>T2108</td><td class="red">Oversold</td><td>Extreme Oversold — potential bounce zone but not signal to buy</td><td><span class="badge badge-bear">OVERSOLD</span></td></tr>
    </table>
  </div>

  <!-- HEADER -->
  <div class="header">
    <h1>📊 Market Summary — March 24, 2026 | {hk_time} / {et_time}</h1>
    <div class="subtitle">每日市場總結 | Steps 1–6 | Sources: Yahoo Finance · feargreedmeter.com · Finviz · StockCharts · MarketInOut · Stockbee · forex.tradingcharts.com</div>
    <div class="subtitle" style="margin-top:4px; color:#3fb950">✅ All data as of Mar 24, 2026 | 4:00 PM ET / Mar 25, 2026 4:00 AM HKT (Market Close)</div>
  </div>

  <!-- STEP 1: MACRO -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 1</span> 宏觀環境 Macro Environment</div>
    <table>
      <tr><th>Indicator</th><th>Value (Mar 24 Close)</th><th>Signal</th><th>Notes</th></tr>
      <tr><td>SPY</td><td class="red">${market_data['indices']['SPY']['price']}</td><td><span class="badge badge-bear">DOWNTREND</span></td><td>{market_data['indices']['SPY']['chg_1d']}% — Below all major MAs</td></tr>
      <tr><td>VIX (Fear Index)</td><td class="yellow">{market_data['macro']['VIX']['price']}</td><td><span class="badge badge-warn">ELEVATED</span></td><td>{market_data['macro']['VIX']['chg_1d']}% — remains above 20 danger zone</td></tr>
      <tr><td>CNN Fear &amp; Greed</td><td class="red">14</td><td><span class="badge badge-bear">EXTREME FEAR</span></td><td>Down from previous readings. Source: <a href="https://feargreedmeter.com" style="color:#58a6ff">feargreedmeter.com</a></td></tr>
    </table>
  </div>

  <!-- STEP 1B: MARKET INTELLIGENCE NEWS -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 1B</span> 市場情報 Market Intelligence News <span class="live-badge">✅ Mar 24 Headlines</span></div>
    <table>
      <tr><th>Impact</th><th>Tickers / Sector</th><th>Headline</th><th>Why It Matters</th></tr>
"""

for item in news_data.get('filtered_news', []):
    impact_class = "badge-bear" if item.get('impact') == 'HIGH' else "badge-warn"
    html += f"""
      <tr>
        <td><span class="badge {impact_class}">{item.get('impact', 'MEDIUM')}</span></td>
        <td class="yellow">{item.get('tickers', '')}</td>
        <td>{item.get('headline', '')}</td>
        <td>{item.get('why_it_matters', '')}</td>
      </tr>
"""

html += """
    </table>
  </div>

  <!-- STEP 2: FULLSTACK INVESTOR -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 2</span> Fullstack Investor Market Model</div>
    <img src="images/fullstack_combined.png" class="screenshot-img" alt="Fullstack Investor Model">
    <div class="note">Requires member login to view.</div>
  </div>

  <!-- STEP 3: SENTIMENT SCORECARD -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 3</span> Sentiment Scorecard</div>
    <div class="scorecard">
      <div class="score-item">
        <div class="score-label">NAAIM Exposure</div>
        <div class="score-value" style="color:#58a6ff">60.24</div>
      </div>
      <div class="score-item">
        <div class="score-label">Fear & Greed</div>
        <div class="score-value" style="color:#f85149">14</div>
      </div>
    </div>
    <img src="images/fear_greed.png" class="chart-img" alt="Fear & Greed Index">
  </div>

  <!-- STEP 4: BREADTH -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 4</span> Market Breadth</div>
    <div class="two-col">
      <div class="chart-card">
        <div class="chart-card-title">S&P 500 > 20MA ($SPXA20R)</div>
        <div style="font-size:24px; font-weight:bold; color:#f85149; text-align:center; margin-bottom:8px">19.80%</div>
        <img src="images/spxa20r.png" alt="SPXA20R">
      </div>
      <div class="chart-card">
        <div class="chart-card-title">S&P 500 > 50MA ($SPXA50R)</div>
        <div style="font-size:24px; font-weight:bold; color:#f85149; text-align:center; margin-bottom:8px">25.80%</div>
        <img src="images/spxa50r.png" alt="SPXA50R">
      </div>
      <div class="chart-card">
        <div class="chart-card-title">S&P 500 > 200MA ($SPXA200R)</div>
        <div style="font-size:24px; font-weight:bold; color:#d29922; text-align:center; margin-bottom:8px">49.20%</div>
        <img src="images/spxa200r.png" alt="SPXA200R">
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Nasdaq 100 > 20MA ($NDXA20R)</div>
        <div style="font-size:24px; font-weight:bold; color:#f85149; text-align:center; margin-bottom:8px">17.00%</div>
        <img src="images/ndxa20r.png" alt="NDXA20R">
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Nasdaq 100 > 50MA ($NDXA50R)</div>
        <div style="font-size:24px; font-weight:bold; color:#f85149; text-align:center; margin-bottom:8px">22.00%</div>
        <img src="images/ndxa50r.png" alt="NDXA50R">
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Nasdaq 100 > 200MA ($NDXA200R)</div>
        <div style="font-size:24px; font-weight:bold; color:#d29922; text-align:center; margin-bottom:8px">43.00%</div>
        <img src="images/ndxa200r.png" alt="NDXA200R">
      </div>
    </div>
  </div>

  <!-- STEP 4C: SECTOR RSI -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 4C</span> Sector ETF RSI</div>
    <table>
      <tr><th>Sector (Ticker)</th><th>Close</th><th>1D %</th><th>14-Day RSI</th></tr>
"""

for item in sorted(sector_rsi, key=lambda x: x['rsi'] if x['rsi'] is not None else 0, reverse=True):
    if item['rsi'] is None: continue
    color_class = "green" if item['rsi'] > 70 else "red" if item['rsi'] < 30 else "gray"
    html += f"""
      <tr>
        <td>{item['sector']} ({item['ticker']})</td>
        <td>${item['close']}</td>
        <td>{item['pct_1d']}%</td>
        <td class="{color_class}">{item['rsi']}</td>
      </tr>
"""

html += """
    </table>
  </div>

  <!-- STEP 5: INDUSTRY LEADERS -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 5</span> Top 10 Industry Leaders (1-Day Performance)</div>
    <table>
      <tr><th>Rank</th><th>Industry Group</th><th>1-Day Change</th></tr>
"""

for item in industry_leaders[:10]:
    html += f"""
      <tr>
        <td>{item['rank']}</td>
        <td>{item['name']}</td>
        <td class="green">+{item['change_1d']}</td>
      </tr>
"""

html += """
    </table>
  </div>

  <!-- STEP 6: STOCKBEE T2108 -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 6</span> Stockbee T2108 & Breadth Thrust</div>
    <div class="scorecard">
      <div class="score-item">
        <div class="score-label">Stocks Up 4%+</div>
        <div class="score-value" style="color:#3fb950">215</div>
      </div>
      <div class="score-item">
        <div class="score-label">Stocks Down 4%+</div>
        <div class="score-value" style="color:#f85149">281</div>
      </div>
    </div>
    <div class="note">Negative breadth thrust today: more stocks down 4%+ than up 4%+.</div>
    <img src="images/stockbee_mm.png" class="screenshot-img" alt="Stockbee Market Monitor">
  </div>

  <!-- STEP 7: BULL VS BEAR -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 7</span> Bull vs Bear Commentary</div>
    <div class="two-col">
      <div class="regime-box" style="background:#1a4731; border-color:#3fb950">
        <div class="regime-title" style="color:#3fb950">🐂 THE BULL CASE</div>
        <ul style="margin-left:20px">
          <li>Energy sector (XLE) showing extreme relative strength with RSI at 80.8, providing a pocket of leadership.</li>
          <li>Fear & Greed Index is at 14 (Extreme Fear), which often acts as a contrarian indicator for short-term bounces.</li>
          <li>Market breadth is extremely washed out (Nasdaq 100 > 20MA at just 17%), setting up potential mean reversion.</li>
        </ul>
      </div>
      <div class="regime-box">
        <div class="regime-title">🐻 THE BEAR CASE</div>
        <ul style="margin-left:20px">
          <li>SPY remains below all key moving averages (10, 20, 50, 200) with a declining trend.</li>
          <li>VIX remains elevated at 26.95, indicating ongoing market stress and implied volatility.</li>
          <li>Breadth thrust indicator flipped negative again with 281 stocks down 4%+ vs only 215 up 4%+.</li>
          <li>Defensive/commodity sectors (Energy, Materials) are leading while Tech/Growth lags, a classic risk-off rotation.</li>
        </ul>
      </div>
    </div>
  </div>

</div>
</body>
</html>
"""

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w') as f:
    f.write(html)

print("Report successfully built: 2026-03-24.html")
