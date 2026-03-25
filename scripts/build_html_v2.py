import re
import json
from datetime import datetime

# Read the template
with open('/home/ubuntu/swing-trader-daily/2026-03-23.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Read data
with open('/home/ubuntu/eod_data/mar24_data.json', 'r') as f:
    macro_data = json.load(f)

with open('/home/ubuntu/eod_data/mar24_news.json', 'r') as f:
    news_data = json.load(f)
    if isinstance(news_data, dict) and 'filtered_news' in news_data:
        news_list = news_data['filtered_news']
    else:
        news_list = news_data

with open('/home/ubuntu/eod_data/industry_leaders_with_sectors.json', 'r') as f:
    industry_data = json.load(f)

with open('/home/ubuntu/eod_data/sector_rsi.json', 'r') as f:
    sector_rsi = json.load(f)

with open('/home/ubuntu/eod_data/breadth_values.json', 'r') as f:
    breadth = json.load(f)

with open('/home/ubuntu/eod_data/t2108_values.json', 'r') as f:
    t2108 = json.load(f)

# --- REPLACEMENTS ---

# 1. Title and Date
html = html.replace("Market Summary: March 23, 2026", "Market Summary: March 24, 2026")
html = html.replace("Data as of: 2026-03-23", "Data as of: 2026-03-24")

# 2. Step 1 Macro Data
# SPY
html = re.sub(r'(\$SPY\s+)\$655\.38\s+\(\-1\.66\%\)', f'\\g<1>${macro_data["indices"]["SPY"]["price"]:.2f} ({macro_data["indices"]["SPY"]["chg_1d"]:+.2f}%)', html)
# QQQ
html = re.sub(r'(\$QQQ\s+)\$587\.99\s+\(\-1\.78\%\)', f'\\g<1>${macro_data["indices"]["QQQ"]["price"]:.2f} ({macro_data["indices"]["QQQ"]["chg_1d"]:+.2f}%)', html)
# IWM
html = re.sub(r'(\$IWM\s+)\$247\.45\s+\(\-0\.53\%\)', f'\\g<1>${macro_data["indices"]["IWM"]["price"]:.2f} ({macro_data["indices"]["IWM"]["chg_1d"]:+.2f}%)', html)
# DIA
html = re.sub(r'(\$DIA\s+)\$461\.96\s+\(\-1\.09\%\)', f'\\g<1>${macro_data["indices"]["DIA"]["price"]:.2f} ({macro_data["indices"]["DIA"]["chg_1d"]:+.2f}%)', html)
# VIX
html = re.sub(r'(\$VIX\s+)26\.15\s+\(\+5\.74\%\)', f'\\g<1>{macro_data["macro"]["VIX"]["price"]:.2f} ({macro_data["macro"]["VIX"]["chg_1d"]:+.2f}%)', html)
# GLD
html = re.sub(r'(\$GLD\s+)\$273\.56\s+\(\+0\.13\%\)', f'\\g<1>${macro_data["macro"]["GLD"]["price"]:.2f} ({macro_data["macro"]["GLD"]["chg_1d"]:+.2f}%)', html)
# USO
html = re.sub(r'(\$USO\s+)\$75\.21\s+\(\+0\.64\%\)', f'\\g<1>${macro_data["macro"]["USO"]["price"]:.2f} ({macro_data["macro"]["USO"]["chg_1d"]:+.2f}%)', html)
# TNX
html = re.sub(r'(\$TNX\s+)4\.61\%\s+\(\-0\.01\%\)', f'\\g<1>{macro_data["macro"]["TNX"]["price"]:.2f}% ({macro_data["macro"]["TNX"]["chg_1d"]:+.2f}%)', html)
# DXY
html = re.sub(r'(\$DXY\s+)106\.85\s+\(\+0\.15\%\)', f'\\g<1>{macro_data["macro"]["DXY"]["price"]:.2f} ({macro_data["macro"]["DXY"]["chg_1d"]:+.2f}%)', html)

# 3. Step 1B News
news_html = ""
for n in news_list:
    ticker = n.get('ticker', '')
    title = n.get('title', '')
    url = n.get('url', '#')
    news_html += f'<li><strong>{ticker}</strong>: <a href="{url}" target="_blank">{title}</a></li>\n'
html = re.sub(r'<ul id="news-list">.*?</ul>', f'<ul id="news-list">\n{news_html}</ul>', html, flags=re.DOTALL)

# 4. Step 2 Fullstack
html = html.replace('https://manus-data.s3.amazonaws.com/fullstack_20260323.png', 'images/fullstack_v2.png')

# 5. Step 3 Sentiment Scorecard
html = html.replace('<div class="value">26.15</div>', f'<div class="value">{macro_data["macro"]["VIX"]["price"]:.2f}</div>') # VIX
html = html.replace('<div class="value">16</div>', '<div class="value">17</div>') # Fear & Greed
html = html.replace('<div class="value">235 / 85</div>', f'<div class="value">{t2108["up_4pct"]} / {t2108["down_4pct"]}</div>') # T2108

# 6. Step 4A Index vs MAs
def get_ma_class(price, ma):
    return "above-ma" if price > ma else "below-ma"

for sym in ['SPY', 'QQQ', 'IWM', 'DIA']:
    p = macro_data["indices"][sym]["price"]
    m20 = macro_data["indices"][sym]["ma20"]
    m50 = macro_data["indices"][sym]["ma50"]
    m200 = macro_data["indices"][sym]["ma200"]
    
    # Need to replace the whole row for each index
    row_pattern = r'<tr>\s*<td>\s*<strong>' + sym + r'</strong>\s*</td>.*?</tr>'
    new_row = f'''<tr>
                            <td><strong>{sym}</strong></td>
                            <td class="{get_ma_class(p, m20)}">{m20:.2f}</td>
                            <td class="{get_ma_class(p, m50)}">{m50:.2f}</td>
                            <td class="{get_ma_class(p, m200)}">{m200:.2f}</td>
                        </tr>'''
    html = re.sub(row_pattern, new_row, html, flags=re.DOTALL)

# 7. Step 4B Sector RSI
sector_html = ""
for s in sector_rsi:
    sym = s['ticker']
    name = s['sector']
    rsi = s['rsi']
    chg = s['pct_1d']
    rsi_class = "bullish" if rsi > 50 else "bearish"
    if rsi > 70: rsi_class = "extreme-bullish"
    if rsi < 30: rsi_class = "extreme-bearish"
    
    sector_html += f'''<tr>
                            <td><strong>{sym}</strong> ({name})</td>
                            <td>{chg:+.2f}%</td>
                            <td class="{rsi_class}"><strong>{rsi:.1f}</strong></td>
                        </tr>\n'''

html = re.sub(r'<tbody id="sector-rsi-body">.*?</tbody>', f'<tbody id="sector-rsi-body">\n{sector_html}</tbody>', html, flags=re.DOTALL)

# 8. Step 4C Breadth Screenshots
html = html.replace('https://manus-data.s3.amazonaws.com/spxa20r_20260323.png', 'images/spxa20r_v2.png')
html = html.replace('https://manus-data.s3.amazonaws.com/spxa50r_20260323.png', 'images/spxa50r_v2.png')
html = html.replace('https://manus-data.s3.amazonaws.com/spxa200r_20260323.png', 'images/spxa200r_v2.png')

html = html.replace('https://manus-data.s3.amazonaws.com/ndxa20r_20260323.png', 'images/ndxa20r_v2.png')
html = html.replace('https://manus-data.s3.amazonaws.com/ndxa50r_20260323.png', 'images/ndxa50r_v2.png')
html = html.replace('https://manus-data.s3.amazonaws.com/ndxa200r_20260323.png', 'images/ndxa200r_v2.png')

html = html.replace('https://manus-data.s3.amazonaws.com/nya20r_20260323.png', 'images/nya20r_v2.png')
html = html.replace('https://manus-data.s3.amazonaws.com/nya50r_20260323.png', 'images/nya50r_v2.png')
html = html.replace('https://manus-data.s3.amazonaws.com/nya200r_20260323.png', 'images/nya200r_v2.png')

# 9. Step 5 Industry Leaders
ind_html = ""
for i, item in enumerate(industry_data, 1):
    ind_html += f'''<tr>
                            <td>{i}</td>
                            <td>{item["name"]}</td>
                            <td>{item["sector"]}</td>
                            <td class="bullish">{item["change_1d"]}</td>
                        </tr>\n'''
html = re.sub(r'<tbody id="industry-leaders-body">.*?</tbody>', f'<tbody id="industry-leaders-body">\n{ind_html}</tbody>', html, flags=re.DOTALL)

# 10. Step 6 Stockbee
html = html.replace('https://manus-data.s3.amazonaws.com/stockbee_20260323.png', 'images/stockbee_mm_v2.png')

# 11. Step 7 Bull vs Bear (Rewrite commentary for Mar 24)
bull_bear = """
                    <div class="bull-bear-grid">
                        <div class="bear-case">
                            <h4>空頭論點 (Bear Case)</h4>
                            <ul>
                                <li><strong>市寬持續惡化：</strong> S&P 500、Nasdaq 100 和 NYSE 的 20MA、50MA、200MA 市寬指標全面處於極低水平（如 NDX 20MA 僅剩 17%），顯示內部結構極度疲弱。</li>
                                <li><strong>T2108 負向推力：</strong> Stockbee T2108 顯示今日有 281 隻股票下跌超過 4%，而僅 215 隻上漲超過 4%，在昨日短暫反彈後再次出現負向廣度推力。</li>
                                <li><strong>VIX 居高不下：</strong> VIX 升至 26.95，市場恐慌情緒（Fear & Greed = 17）極端，四大指數均跌破所有關鍵均線（20/50/200MA）。</li>
                            </ul>
                        </div>
                        <div class="bull-case">
                            <h4>多頭論點 (Bull Case)</h4>
                            <ul>
                                <li><strong>極度超賣可能引發反彈：</strong> 許多廣度指標已經跌至歷史極端超賣區域（如 Fear & Greed 17，NDX 20MA 17%），隨時可能出現技術性空頭回補反彈。</li>
                                <li><strong>能源與原物料展現相對強勢：</strong> XLE (RSI 81.8) 和 XLB (RSI 40.9) 逆勢上漲，Coking Coal、Chemicals 等傳統防禦性/通脹受惠板塊成為資金避風港。</li>
                            </ul>
                        </div>
                    </div>
                    <div class="conclusion">
                        <h4>總結與行動建議 (Action Guidance)</h4>
                        <p>市場目前處於典型的<strong>防禦性輪動（Defensive Rotation）</strong>，資金從科技股（XLK RSI 43.1）撤出，轉入能源（XLE）和原物料板塊。整體市場結構（Market Regime）維持在 <strong>Level 8-9 的強烈空頭狀態</strong>。在 VIX 回落至 20 以下，且四大指數重新站上 20MA 之前，<strong>嚴禁建立任何新的多頭部位（No New Longs）</strong>。目前最佳策略是保持高現金比例，耐心等待市寬出現真正的「多頭推力（Breadth Thrust）」。</p>
                    </div>
"""
html = re.sub(r'<div class="bull-bear-grid">.*?</div>\s*</div>', bull_bear + '\n                </div>', html, flags=re.DOTALL)

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully generated 2026-03-24.html using 2026-03-23.html as template.")
