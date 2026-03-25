"""
Complete HTML builder for 2026-03-24.html
Strategy: Start from 2026-03-23.html and do exact string replacements.
All replacements are based on the actual template structure.
"""
import json
import re

# ===== Load all data =====
with open('/home/ubuntu/eod_data/mar24_data.json') as f:
    d = json.load(f)

idx = d['indices']
mac = d['macro']

with open('/home/ubuntu/eod_data/mar24_news.json') as f:
    news_raw = json.load(f)
    if isinstance(news_raw, dict) and 'filtered_news' in news_raw:
        news_list = news_raw['filtered_news']
    else:
        news_list = news_raw if isinstance(news_raw, list) else []

with open('/home/ubuntu/eod_data/industry_leaders_with_sectors.json') as f:
    industry = json.load(f)

with open('/home/ubuntu/eod_data/sector_rsi.json') as f:
    sectors = json.load(f)
    # Sort by RSI descending
    sectors.sort(key=lambda x: x['rsi'], reverse=True)

with open('/home/ubuntu/eod_data/breadth_values.json') as f:
    breadth = json.load(f)

with open('/home/ubuntu/eod_data/t2108_values.json') as f:
    t2108 = json.load(f)

# CDN URLs for today's images
CDN = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"
IMGS = {
    'spxa20r':   CDN + "UchRzbLnXZOVLOSM.png",
    'spxa50r':   CDN + "YqYbgMkyHTAGMyOI.png",
    'spxa200r':  CDN + "OorOwtUUTFeAnXGC.png",
    'ndxa20r':   CDN + "XgbOeCnQgvgjZLQq.png",
    'ndxa50r':   CDN + "FUQmBjmrmqhvGXWj.png",
    'ndxa200r':  CDN + "EeMHzWdZygXoXVnk.png",
    'nya20r':    CDN + "LqnzwjnmCuLSIiIJ.png",
    'nya50r':    CDN + "WoTOuricVLNOZrjA.png",
    'nya200r':   CDN + "SXjAwlrLhQpDobVl.png",
    'stockbee':  CDN + "atToNJzyXaRJbfPN.png",
    'fullstack': CDN + "AKeZtENLuEgCqWgq.png",
}

# ===== Helper functions =====
def color_class(val):
    return "green" if val >= 0 else "red"

def badge_vs_ma(price, ma):
    pct = (price - ma) / ma * 100
    if pct >= 0:
        return f'<span class="badge badge-bull">ABOVE +{pct:.2f}%</span>'
    else:
        return f'<span class="badge badge-bear">BELOW {pct:.2f}%</span>'

def signal_badge(price, ma20, ma50, ma200):
    above = sum([price > ma20, price > ma50, price > ma200])
    if above == 3:
        return '<span class="badge badge-bull">ABOVE ALL MAs</span>'
    elif above == 0:
        return '<span class="badge badge-bear">BELOW ALL MAs</span>'
    else:
        return '<span class="badge badge-warn">MIXED MAs</span>'

# ===== Read template =====
with open('/home/ubuntu/swing-trader-daily/2026-03-23.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ===== 1. TITLE & DATE =====
html = html.replace(
    'Market Summary — Mon Mar 23, 2026',
    'Market Summary — Mon Mar 24, 2026'
)
html = html.replace(
    'Market Summary — Mon, Mar 23, 2026',
    'Market Summary — Mon, Mar 24, 2026'
)
html = html.replace(
    'Report generated: Mon Mar 23, 2026 · 19:45 HKT (07:45 ET)',
    'Report generated: Mon Mar 24, 2026 · 21:45 HKT (09:45 ET)'
)
html = html.replace('Mar 23, 2026', 'Mar 24, 2026')
html = html.replace('Mar 23 EOD', 'Mar 24 EOD')
html = html.replace('Mar 23 Headlines', 'Mar 24 Headlines')
html = html.replace('✅ LIVE — Mar 23', '✅ LIVE — Mar 24')
html = html.replace('Value (Mar 23)', 'Value (Mar 24)')
html = html.replace('Data as of Mar 23, 2026 close', 'Data as of Mar 24, 2026 close')

# ===== 2. KEY LEVELS TABLE =====
# SPY 200MA row
spy = idx['SPY']
html = html.replace(
    '<tr><td>SPY 200MA</td><td>$656.85</td><td><span class="badge badge-bear">BELOW — SPY @ $655.38 (-0.22%)</span></td></tr>',
    f'<tr><td>SPY 200MA</td><td>${spy["ma200"]:.2f}</td><td><span class="badge badge-bear">BELOW — SPY @ ${spy["price"]:.2f} ({spy["vs_200ma"]:+.2f}%)</span></td></tr>'
)
# SPY 50MA row
html = html.replace(
    '<tr><td>SPY 50MA</td><td>$681.42</td><td><span class="badge badge-bear">BELOW — SPY @ $655.38 (-3.82%)</span></td>',
    f'<tr><td>SPY 50MA</td><td>${spy["ma50"]:.2f}</td><td><span class="badge badge-bear">BELOW — SPY @ ${spy["price"]:.2f} ({spy["vs_50ma"]:+.2f}%)</span></td>'
)
# SPY 20MA row
html = html.replace(
    '<tr><td>SPY 20MA</td><td>$672.66</td><td><span class="badge badge-bear">BELOW — SPY @ $655.38 (-2.57%)</span></td></tr>',
    f'<tr><td>SPY 20MA</td><td>${spy["ma20"]:.2f}</td><td><span class="badge badge-bear">BELOW — SPY @ ${spy["price"]:.2f} ({spy["vs_20ma"]:+.2f}%)</span></td></tr>'
)
# VIX Level row
vix = mac['VIX']
html = html.replace(
    '<tr><td>VIX Level</td><td>26.15</td><td><span class="badge badge-warn">ELEVATED — Above 20 (Caution)</span></td></tr>',
    f'<tr><td>VIX Level</td><td>{vix["price"]:.2f}</td><td><span class="badge badge-warn">ELEVATED — Above 20 (Caution)</span></td></tr>'
)
# T2108 row
html = html.replace(
    '<tr><td>T2108 (% above 40MA)</td><td>~18–20%</td><td><span class="badge badge-bear">OVERSOLD — Below 20%</span></td></tr>',
    f'<tr><td>T2108 (Up 4%+ / Down 4%+)</td><td>{t2108["up_4pct"]} / {t2108["down_4pct"]}</td><td><span class="badge badge-bear">BEARISH BREADTH</span></td></tr>'
)
# SPXA20R row in key levels
html = html.replace(
    '<tr><td>$SPXA20R</td><td>40.00%</td><td><span class="badge badge-warn">RECOVERING — Up from 12.60%</span></td></tr>',
    f'<tr><td>$SPXA20R</td><td>{breadth["SP500"]["above_20ma"]:.2f}%</td><td><span class="badge badge-bear">BEARISH</span></td></tr>'
)

# ===== 3. STEP 1A MACRO TABLE =====
# SPY row
html = html.replace(
    '''<tr>
      <td><strong>SPY (S&P 500)</strong></td>
      <td><strong>$655.38</strong></td>
      <td class="green"><strong>+1.05%</strong></td>
      <td class="red">-2.57%</td>
      <td class="red">-3.82%</td>
      <td class="red">-0.22%</td>
      <td class="red"><strong>37.2</strong></td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td><strong>SPY (S&P 500)</strong></td>
      <td><strong>${spy["price"]:.2f}</strong></td>
      <td class="{color_class(spy["chg_1d"])}"><strong>{spy["chg_1d"]:+.2f}%</strong></td>
      <td class="red">{spy["vs_20ma"]:+.2f}%</td>
      <td class="red">{spy["vs_50ma"]:+.2f}%</td>
      <td class="red">{spy["vs_200ma"]:+.2f}%</td>
      <td class="red"><strong>{spy["rsi14"]:.1f}</strong></td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>'''
)

# QQQ row
qqq = idx['QQQ']
html = html.replace(
    '''<tr>
      <td>QQQ (Nasdaq 100)</td>
      <td>$588.00</td>
      <td class="green">+1.02%</td>
      <td class="red">-2.37%</td>
      <td class="red">-3.65%</td>
      <td class="red">-0.73%</td>
      <td class="red">40.2</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td>QQQ (Nasdaq 100)</td>
      <td>${qqq["price"]:.2f}</td>
      <td class="{color_class(qqq["chg_1d"])}">{qqq["chg_1d"]:+.2f}%</td>
      <td class="red">{qqq["vs_20ma"]:+.2f}%</td>
      <td class="red">{qqq["vs_50ma"]:+.2f}%</td>
      <td class="red">{qqq["vs_200ma"]:+.2f}%</td>
      <td class="red">{qqq["rsi14"]:.1f}</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>'''
)

# IWM row
iwm = idx['IWM']
html = html.replace(
    '''<tr>
      <td>IWM (Russell 2000)</td>
      <td>$247.45</td>
      <td class="green">+2.16%</td>
      <td class="red">-2.52%</td>
      <td class="red">-4.56%</td>
      <td class="green">+3.00%</td>
      <td class="yellow">42.0</td>
      <td><span class="badge badge-warn">BELOW 20/50MA</span></td>
    </tr>''',
    f'''<tr>
      <td>IWM (Russell 2000)</td>
      <td>${iwm["price"]:.2f}</td>
      <td class="{color_class(iwm["chg_1d"])}">{iwm["chg_1d"]:+.2f}%</td>
      <td class="red">{iwm["vs_20ma"]:+.2f}%</td>
      <td class="red">{iwm["vs_50ma"]:+.2f}%</td>
      <td class="{color_class(iwm["vs_200ma"])}">{iwm["vs_200ma"]:+.2f}%</td>
      <td class="yellow">{iwm["rsi14"]:.1f}</td>
      <td><span class="badge badge-warn">BELOW 20/50MA</span></td>
    </tr>'''
)

# DIA row
dia = idx['DIA']
html = html.replace(
    '''<tr>
      <td>DIA (Dow Jones)</td>
      <td>$462.08</td>
      <td class="green">+1.38%</td>
      <td class="red">-3.01%</td>
      <td class="red">-5.08%</td>
      <td class="red">-0.80%</td>
      <td class="red">34.6</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td>DIA (Dow Jones)</td>
      <td>${dia["price"]:.2f}</td>
      <td class="{color_class(dia["chg_1d"])}">{dia["chg_1d"]:+.2f}%</td>
      <td class="red">{dia["vs_20ma"]:+.2f}%</td>
      <td class="red">{dia["vs_50ma"]:+.2f}%</td>
      <td class="red">{dia["vs_200ma"]:+.2f}%</td>
      <td class="red">{dia["rsi14"]:.1f}</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>'''
)

# VIX row
html = html.replace(
    '''<tr>
      <td><strong>VIX</strong></td>
      <td><strong>26.15</strong></td>
      <td class="green">-2.35%</td>
      <td colspan="3">—</td>
      <td class="yellow">56.8</td>
      <td><span class="badge badge-warn">ELEVATED (>20)</span></td>
    </tr>''',
    f'''<tr>
      <td><strong>VIX</strong></td>
      <td><strong>{vix["price"]:.2f}</strong></td>
      <td class="{color_class(-vix["chg_1d"])}">{vix["chg_1d"]:+.2f}%</td>
      <td colspan="3">—</td>
      <td class="yellow">—</td>
      <td><span class="badge badge-warn">ELEVATED (>20)</span></td>
    </tr>'''
)

# GLD row
gld = mac['GLD']
html = html.replace(
    '''<tr>
      <td>GLD (Gold)</td>
      <td>$404.04</td>
      <td class="red">-2.26%</td>
      <td class="red">-12.55%</td>
      <td class="red">-11.38%</td>
      <td class="green">+7.86%</td>
      <td class="red">27.4</td>
      <td><span class="badge badge-warn">PULLBACK — Above 200MA</span></td>
    </tr>''',
    f'''<tr>
      <td>GLD (Gold)</td>
      <td>${gld["price"]:.2f}</td>
      <td class="{color_class(gld["chg_1d"])}">{gld["chg_1d"]:+.2f}%</td>
      <td class="{color_class(gld["vs_20ma"])}">{gld["vs_20ma"]:+.2f}%</td>
      <td class="{color_class(gld["vs_50ma"])}">{gld["vs_50ma"]:+.2f}%</td>
      <td class="{color_class(gld["vs_200ma"])}">{gld["vs_200ma"]:+.2f}%</td>
      <td class="red">{gld["rsi14"]:.1f}</td>
      <td><span class="badge badge-warn">PULLBACK</span></td>
    </tr>'''
)

# USO row
uso = mac['USO']
html = html.replace(
    '''<tr>
      <td>USO (Oil)</td>
      <td>$110.56</td>
      <td class="red">-8.95%</td>
      <td class="green">+7.47%</td>
      <td class="green">+27.57%</td>
      <td class="green">+44.71%</td>
      <td class="yellow">59.5</td>
      <td><span class="badge badge-bull">ABOVE ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td>USO (Oil)</td>
      <td>${uso["price"]:.2f}</td>
      <td class="{color_class(uso["chg_1d"])}">{uso["chg_1d"]:+.2f}%</td>
      <td class="{color_class(uso["vs_20ma"])}">{uso["vs_20ma"]:+.2f}%</td>
      <td class="{color_class(uso["vs_50ma"])}">{uso["vs_50ma"]:+.2f}%</td>
      <td class="{color_class(uso["vs_200ma"])}">{uso["vs_200ma"]:+.2f}%</td>
      <td class="yellow">{uso["rsi14"]:.1f}</td>
      <td><span class="badge badge-bull">ABOVE ALL MAs</span></td>
    </tr>'''
)

# TNX row
tnx = mac['TNX']
html = html.replace(
    '''<tr>
      <td>10Y Yield (^TNX)</td>
      <td>4.33%</td>
      <td class="red">-1.30%</td>
      <td class="green">+4.09%</td>
      <td class="green">+3.84%</td>
      <td class="green">+3.34%</td>
      <td class="yellow">63.5</td>
      <td><span class="badge badge-warn">ABOVE ALL MAs — Elevated</span></td>
    </tr>''',
    f'''<tr>
      <td>10Y Yield (^TNX)</td>
      <td>{tnx["price"]:.2f}%</td>
      <td class="{color_class(tnx["chg_1d"])}">{tnx["chg_1d"]:+.2f}%</td>
      <td class="{color_class(tnx["vs_20ma"])}">{tnx["vs_20ma"]:+.2f}%</td>
      <td class="{color_class(tnx["vs_50ma"])}">{tnx["vs_50ma"]:+.2f}%</td>
      <td class="{color_class(tnx["vs_200ma"])}">{tnx["vs_200ma"]:+.2f}%</td>
      <td class="yellow">{tnx["rsi14"]:.1f}</td>
      <td><span class="badge badge-warn">ABOVE ALL MAs — Elevated</span></td>
    </tr>'''
)

# DXY row
dxy = mac['DXY']
html = html.replace(
    '''<tr>
      <td>DXY (US Dollar)</td>
      <td>99.15</td>
      <td class="red">-0.50%</td>
      <td class="green">+0.14%</td>
      <td class="green">+0.93%</td>
      <td class="green">+0.76%</td>
      <td class="yellow">52.6</td>
      <td><span class="badge badge-neutral">NEUTRAL</span></td>
    </tr>''',
    f'''<tr>
      <td>DXY (US Dollar)</td>
      <td>{dxy["price"]:.2f}</td>
      <td class="{color_class(dxy["chg_1d"])}">{dxy["chg_1d"]:+.2f}%</td>
      <td class="{color_class(dxy["vs_20ma"])}">{dxy["vs_20ma"]:+.2f}%</td>
      <td class="{color_class(dxy["vs_50ma"])}">{dxy["vs_50ma"]:+.2f}%</td>
      <td class="{color_class(dxy["vs_200ma"])}">{dxy["vs_200ma"]:+.2f}%</td>
      <td class="yellow">{dxy["rsi14"]:.1f}</td>
      <td><span class="badge badge-neutral">NEUTRAL</span></td>
    </tr>'''
)

# ===== 4. STEP 1B NEWS =====
# Build news HTML
news_html = ""
for n in news_list:
    ticker = n.get('ticker', n.get('tickers', 'Market'))
    title = n.get('title', n.get('headline', ''))
    url = n.get('url', '#')
    impact = n.get('impact', 'medium').lower()
    why = n.get('why', n.get('reason', ''))
    impact_class = 'impact-high' if 'high' in impact else ('impact-low' if 'low' in impact else 'impact-medium')
    impact_icon = '⚡' if 'high' in impact else ('⬜' if 'low' in impact else '🔶')
    impact_label = 'HIGH IMPACT' if 'high' in impact else ('LOW IMPACT' if 'low' in impact else 'MEDIUM IMPACT')
    news_html += f'''  <div class="news-item {impact_class}">
    <div class="news-tickers">🏷 {ticker}</div>
    <div class="news-headline"><a href="{url}" target="_blank" style="color:#e6edf3;text-decoration:none;">{title}</a></div>
    <div class="news-why">{impact_icon} <strong>{impact_label}:</strong> {why}</div>
  </div>\n'''

# Replace the entire news section content
html = re.sub(
    r'(<!-- STEP 1B.*?-->\n<div class="section">.*?</div>\n<!-- STEP 2)',
    lambda m: re.sub(
        r'(<div class="news-item.*?</div>\n)+',
        news_html,
        m.group(0),
        flags=re.DOTALL
    ),
    html,
    flags=re.DOTALL
)

# ===== 5. STEP 2 FULLSTACK =====
html = html.replace(
    '⚠️ Fullstack Market Model page requires member login. Screenshot not available for this session. Please check <a href="https://fullstacktrading.com/market-model/" style="color:#58a6ff" target="_blank">fullstacktrading.com/market-model/</a> directly for the current model reading. Based on prior data (Mar 20), model was BULLISH (high exposure recommended).',
    f'<img src="{IMGS["fullstack"]}" alt="Fullstack Market Model Mar 24" style="max-width:100%;border-radius:8px;margin-top:8px;">'
)

# ===== 6. STEP 3 SENTIMENT =====
html = html.replace(
    '<td><strong class="red">16 — EXTREME FEAR</strong></td>',
    '<td><strong class="red">17 — EXTREME FEAR</strong></td>'
)
html = html.replace(
    '<td><strong class="red">19.44</strong> (as of Mar 18)</td>',
    '<td><strong class="red">60.24</strong> (as of Mar 18)</td>'
)
html = html.replace(
    '<td>26.15 (-2.35%)</td>',
    f'<td>{vix["price"]:.2f} ({vix["chg_1d"]:+.2f}%)</td>'
)
html = html.replace(
    '<td>~18–20% (Stockbee MM)</td>',
    f'<td>{t2108["up_4pct"]} up / {t2108["down_4pct"]} down (Stockbee MM)</td>'
)

# ===== 7. STEP 4A INDEX VS MAs TABLE =====
# SPY row in 4A
html = html.replace(
    '''<tr>
      <td><strong>SPY (S&P 500)</strong></td>
      <td><strong>$655.38</strong></td>
      <td class="green"><strong>+1.05%</strong></td>
      <td>$672.66</td><td class="red">-2.57%</td>
      <td>$681.42</td><td class="red">-3.82%</td>
      <td>$656.85</td><td class="red">-0.22%</td>
      <td class="red"><strong>37.2</strong></td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td><strong>SPY (S&P 500)</strong></td>
      <td><strong>${spy["price"]:.2f}</strong></td>
      <td class="{color_class(spy["chg_1d"])}"><strong>{spy["chg_1d"]:+.2f}%</strong></td>
      <td>${spy["ma20"]:.2f}</td><td class="red">{spy["vs_20ma"]:+.2f}%</td>
      <td>${spy["ma50"]:.2f}</td><td class="red">{spy["vs_50ma"]:+.2f}%</td>
      <td>${spy["ma200"]:.2f}</td><td class="red">{spy["vs_200ma"]:+.2f}%</td>
      <td class="red"><strong>{spy["rsi14"]:.1f}</strong></td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>'''
)

# QQQ row in 4A
html = html.replace(
    '''<tr>
      <td>QQQ (Nasdaq 100)</td>
      <td>$588.00</td>
      <td class="green">+1.02%</td>
      <td>$601.96</td><td class="red">-2.37%</td>
      <td>$609.89</td><td class="red">-3.65%</td>
      <td>$592.34</td><td class="red">-0.73%</td>
      <td class="red">40.2</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td>QQQ (Nasdaq 100)</td>
      <td>${qqq["price"]:.2f}</td>
      <td class="{color_class(qqq["chg_1d"])}">{qqq["chg_1d"]:+.2f}%</td>
      <td>${qqq["ma20"]:.2f}</td><td class="red">{qqq["vs_20ma"]:+.2f}%</td>
      <td>${qqq["ma50"]:.2f}</td><td class="red">{qqq["vs_50ma"]:+.2f}%</td>
      <td>${qqq["ma200"]:.2f}</td><td class="red">{qqq["vs_200ma"]:+.2f}%</td>
      <td class="red">{qqq["rsi14"]:.1f}</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>'''
)

# IWM row in 4A
html = html.replace(
    '''<tr>
      <td>IWM (Russell 2000)</td>
      <td>$247.45</td>
      <td class="green">+2.16%</td>
      <td>$253.85</td><td class="red">-2.52%</td>
      <td>$259.28</td><td class="red">-4.56%</td>
      <td>$240.23</td><td class="green">+3.00%</td>
      <td class="yellow">42.0</td>
      <td><span class="badge badge-warn">BELOW 20/50MA</span></td>
    </tr>''',
    f'''<tr>
      <td>IWM (Russell 2000)</td>
      <td>${iwm["price"]:.2f}</td>
      <td class="{color_class(iwm["chg_1d"])}">{iwm["chg_1d"]:+.2f}%</td>
      <td>${iwm["ma20"]:.2f}</td><td class="red">{iwm["vs_20ma"]:+.2f}%</td>
      <td>${iwm["ma50"]:.2f}</td><td class="red">{iwm["vs_50ma"]:+.2f}%</td>
      <td>${iwm["ma200"]:.2f}</td><td class="{color_class(iwm["vs_200ma"])}">{iwm["vs_200ma"]:+.2f}%</td>
      <td class="yellow">{iwm["rsi14"]:.1f}</td>
      <td><span class="badge badge-warn">BELOW 20/50MA</span></td>
    </tr>'''
)

# DIA row in 4A
html = html.replace(
    '''<tr>
      <td>DIA (DJI)</td>
      <td>$462.08</td>
      <td class="green">+1.38%</td>
      <td>$476.40</td><td class="red">-3.01%</td>
      <td>$486.82</td><td class="red">-5.08%</td>
      <td>$465.82</td><td class="red">-0.80%</td>
      <td class="red">34.6</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>''',
    f'''<tr>
      <td>DIA (DJI)</td>
      <td>${dia["price"]:.2f}</td>
      <td class="{color_class(dia["chg_1d"])}">{dia["chg_1d"]:+.2f}%</td>
      <td>${dia["ma20"]:.2f}</td><td class="red">{dia["vs_20ma"]:+.2f}%</td>
      <td>${dia["ma50"]:.2f}</td><td class="red">{dia["vs_50ma"]:+.2f}%</td>
      <td>${dia["ma200"]:.2f}</td><td class="red">{dia["vs_200ma"]:+.2f}%</td>
      <td class="red">{dia["rsi14"]:.1f}</td>
      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>
    </tr>'''
)

# ===== 8. STEP 4B SECTOR ETF TABLE =====
# Build new sector table rows (sorted by RSI desc)
sector_rows = ""
for s in sectors:
    sym = s['ticker']
    name = s['sector']
    price = s['close']
    chg = s['pct_1d']
    rsi = s['rsi']
    
    # We don't have vs MA data for sectors, use placeholder
    rsi_class = "green" if rsi > 50 else ("yellow" if rsi > 30 else "red")
    badge = "badge-bull" if rsi > 60 else ("badge-warn" if rsi > 40 else "badge-bear")
    badge_text = "STRONG" if rsi > 60 else ("NEUTRAL" if rsi > 40 else "WEAK")
    
    sector_rows += f'''    <tr>
      <td>{sym}</td><td>{name}</td><td>${price:.2f}</td>
      <td class="{color_class(chg)}">{chg:+.2f}%</td>
      <td>—</td>
      <td>—</td>
      <td>—</td>
      <td class="{rsi_class}"><strong>{rsi:.1f}</strong></td>
      <td><span class="badge {badge}">{badge_text}</span></td>
    </tr>\n'''

# Replace the entire sector table body
html = re.sub(
    r'(<tr><th>ETF</th>.*?</tr>\n)(.*?)(</table>\n  <div class="note">📌 板塊 ETF 總結)',
    lambda m: m.group(1) + sector_rows + m.group(3),
    html,
    flags=re.DOTALL
)

# ===== 9. STEP 4C BREADTH TABLE VALUES =====
sp = breadth['SP500']
nd = breadth['NDX100']
ny = breadth['NYSE']

html = html.replace(
    '<tr><td rowspan="3"><strong>S&amp;P 500</strong></td><td>$SPXA20R</td><td>20MA</td><td class="yellow">40.00%</td><td><span class="badge badge-warn">RECOVERING — Up from 12.60%</span></td><td>StockCharts</td></tr>',
    f'<tr><td rowspan="3"><strong>S&amp;P 500</strong></td><td>$SPXA20R</td><td>20MA</td><td class="red">{sp["above_20ma"]:.2f}%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td>$SPXA50R</td><td>50MA</td><td class="red">21.00%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>',
    f'<tr><td>$SPXA50R</td><td>50MA</td><td class="red">{sp["above_50ma"]:.2f}%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td>$SPXA200R</td><td>200MA</td><td class="yellow">49.00%</td><td><span class="badge badge-warn">WARNING — Near 50%</span></td><td>StockCharts</td></tr>',
    f'<tr><td>$SPXA200R</td><td>200MA</td><td class="yellow">{sp["above_200ma"]:.2f}%</td><td><span class="badge badge-warn">WARNING — Near 50%</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td rowspan="3"><strong>Nasdaq 100</strong></td><td>$NDXA20R</td><td>20MA</td><td class="yellow">27.00%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>',
    f'<tr><td rowspan="3"><strong>Nasdaq 100</strong></td><td>$NDXA20R</td><td>20MA</td><td class="red">{nd["above_20ma"]:.2f}%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td>$NDXA50R</td><td>50MA</td><td class="red">21.00%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>',
    f'<tr><td>$NDXA50R</td><td>50MA</td><td class="red">{nd["above_50ma"]:.2f}%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td>$NDXA200R</td><td>200MA</td><td class="yellow">43.00%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>',
    f'<tr><td>$NDXA200R</td><td>200MA</td><td class="yellow">{nd["above_200ma"]:.2f}%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td rowspan="3"><strong>NYSE</strong></td><td>$NYA20R</td><td>20MA</td><td class="red">23.31%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>',
    f'<tr><td rowspan="3"><strong>NYSE</strong></td><td>$NYA20R</td><td>20MA</td><td class="red">{ny["above_20ma"]:.2f}%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td>$NYA50R</td><td>50MA</td><td class="red">25.83%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>',
    f'<tr><td>$NYA50R</td><td>50MA</td><td class="red">{ny["above_50ma"]:.2f}%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>'
)
html = html.replace(
    '<tr><td>$NYA200R</td><td>200MA</td><td class="yellow">46.79%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>',
    f'<tr><td>$NYA200R</td><td>200MA</td><td class="yellow">{ny["above_200ma"]:.2f}%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>'
)

# ===== 10. STEP 4C CHART CARD TITLES & IMAGES =====
html = html.replace(
    'S&amp;P 500 — % Above 20MA ($SPXA20R) = 40.00%',
    f'S&amp;P 500 — % Above 20MA ($SPXA20R) = {sp["above_20ma"]:.2f}%'
)
html = html.replace(
    'S&amp;P 500 — % Above 50MA ($SPXA50R) = 21.00%',
    f'S&amp;P 500 — % Above 50MA ($SPXA50R) = {sp["above_50ma"]:.2f}%'
)
html = html.replace(
    'S&amp;P 500 — % Above 200MA ($SPXA200R) = 49.00%',
    f'S&amp;P 500 — % Above 200MA ($SPXA200R) = {sp["above_200ma"]:.2f}%'
)

# Replace all CDN URLs
OLD_CDN = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"
url_map = {
    "CTUzxaAqcpaevTvi.png": "UchRzbLnXZOVLOSM.png",
    "DQlweCCLSHauCyBn.png": "YqYbgMkyHTAGMyOI.png",
    "ivuLkuZeqNkFruSD.png": "OorOwtUUTFeAnXGC.png",
    "DqtUSvHOzZlOnbym.png": "XgbOeCnQgvgjZLQq.png",
    "FrnJGRHehDeBfSSu.png": "FUQmBjmrmqhvGXWj.png",
    "VzGlsCvOlYrYArzm.png": "EeMHzWdZygXoXVnk.png",
    "aLRUwqWnnOAkVUsE.png": "LqnzwjnmCuLSIiIJ.png",
    "dwSNMinuFLvRFcBl.png": "WoTOuricVLNOZrjA.png",
    "DWVaHZsujoNKTGFB.png": "SXjAwlrLhQpDobVl.png",
    "rhOaquSPLXjAmwcG.png": "atToNJzyXaRJbfPN.png",
    "brlBogwNeKchEFhK.png": "atToNJzyXaRJbfPN.png",
}
for old_f, new_f in url_map.items():
    html = html.replace(OLD_CDN + old_f, OLD_CDN + new_f)

# Also replace Fullstack note with image
html = html.replace(
    '<div class="note">⚠️ Fullstack Market Model page requires member login. Screenshot not available for this session. Please check <a href="https://fullstacktrading.com/market-model/" style="color:#58a6ff" target="_blank">fullstacktrading.com/market-model/</a> directly for the current model reading. Based on prior data (Mar 20), model was BULLISH (high exposure recommended).</div>',
    f'<img src="{IMGS["fullstack"]}" alt="Fullstack Market Model Mar 24" style="max-width:100%;border-radius:8px;margin-top:8px;">'
)

# ===== 11. STEP 5 INDUSTRY LEADERS =====
# Build new industry leaders table
ind_rows = ""
for i, item in enumerate(industry, 1):
    ind_rows += f'    <tr><td>{i}</td><td>{item["name"]}</td><td>{item["sector"]}</td><td class="green">+{item["change_1d"].replace("%","").replace("+","")}%</td></tr>\n'

# Find and replace the industry leaders table body
html = re.sub(
    r'(<tr><th>#</th><th>Industry</th>.*?</tr>\n)(.*?)(</table>\n.*?<!-- STEP 6)',
    lambda m: m.group(1) + ind_rows + m.group(3),
    html,
    flags=re.DOTALL
)

# ===== 12. STEP 6 STOCKBEE =====
# Update Stockbee values
html = html.replace(
    'Up 4%+: <strong>235</strong>',
    f'Up 4%+: <strong>{t2108["up_4pct"]}</strong>'
)
html = html.replace(
    'Down 4%+: <strong>85</strong>',
    f'Down 4%+: <strong>{t2108["down_4pct"]}</strong>'
)

# ===== SAVE =====
with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w', encoding='utf-8') as f:
    f.write(html)

# ===== VERIFY =====
print("=== VERIFICATION ===")
checks = [
    (f'{spy["price"]:.2f}', 'SPY price'),
    (f'{qqq["price"]:.2f}', 'QQQ price'),
    (f'{vix["price"]:.2f}', 'VIX'),
    ('17 — EXTREME FEAR', 'Fear & Greed'),
    ('60.24', 'NAAIM'),
    (f'{sp["above_20ma"]:.2f}%', 'SPXA20R value'),
    (f'{ny["above_20ma"]:.2f}%', 'NYA20R value'),
    ('UchRzbLnXZOVLOSM', 'SPXA20R CDN'),
    ('LqnzwjnmCuLSIiIJ', 'NYA20R CDN'),
    ('atToNJzyXaRJbfPN', 'Stockbee CDN'),
    ('AKeZtENLuEgCqWgq', 'Fullstack CDN'),
    ('Coking Coal', 'Industry #1'),
    ('Mar 24, 2026', 'Date updated'),
]

all_ok = True
for val, label in checks:
    found = val in html
    status = "✓" if found else "✗ MISSING"
    print(f"  {status} {label}: {val}")
    if not found:
        all_ok = False

if all_ok:
    print("\n✅ All checks passed!")
else:
    print("\n⚠️ Some checks failed.")
