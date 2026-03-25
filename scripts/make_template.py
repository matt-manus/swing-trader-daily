"""
Convert 2026-03-23.html into TEMPLATE.html
Every daily-changing value is replaced with a {{PLACEHOLDER}}
Structure, CSS, layout: untouched.
"""

with open('/home/ubuntu/swing-trader-daily/2026-03-23.html', 'r') as f:
    t = f.read()

# ── TITLE & DATE ──────────────────────────────────────────────────────────────
t = t.replace('Market Summary — Mon Mar 23, 2026', 'Market Summary — {{REPORT_DAY_FULL}}')
t = t.replace('Market Summary — Mon, Mar 23, 2026', 'Market Summary — {{REPORT_DAY_FULL}}')
t = t.replace('Mon Mar 23, 2026', '{{REPORT_DAY_FULL}}')
t = t.replace('Mon, Mar 23, 2026', '{{REPORT_DAY_FULL}}')
t = t.replace('19:45 HKT (07:45 ET)', '{{REPORT_TIME_HKT}} HKT ({{REPORT_TIME_ET}} ET)')
t = t.replace('✅ LIVE — Mar 23', '✅ LIVE — {{REPORT_DATE_SHORT}}')
t = t.replace('Mar 23 Headlines', '{{REPORT_DATE_SHORT}} Headlines')
t = t.replace('Mar 23 EOD', '{{REPORT_DATE_SHORT}} EOD')
t = t.replace('Value (Mar 23)', 'Value ({{REPORT_DATE_SHORT}})')
t = t.replace('Data as of Mar 23, 2026 close', 'Data as of {{REPORT_DATE_SHORT}}, 2026 close')
t = t.replace('Finviz — Mar 23', 'Finviz — {{REPORT_DATE_SHORT}}')
t = t.replace('Finviz — Mar 24', 'Finviz — {{REPORT_DATE_SHORT}}')

# ── KEY LEVELS ────────────────────────────────────────────────────────────────
t = t.replace('<td>$656.85</td><td><span class="badge badge-bear">BELOW — SPY @ $655.38 (-0.22%)</span></td></tr>',
              '<td>${{SPY_MA200}}</td><td><span class="badge badge-bear">BELOW — SPY @ ${{SPY_PRICE}} ({{SPY_VS_200MA}}%)</span></td></tr>')
t = t.replace('<td>$681.42</td><td><span class="badge badge-bear">BELOW — SPY @ $655.38 (-3.82%)</span></td>',
              '<td>${{SPY_MA50}}</td><td><span class="badge badge-bear">BELOW — SPY @ ${{SPY_PRICE}} ({{SPY_VS_50MA}}%)</span></td>')
t = t.replace('<td>$672.66</td><td><span class="badge badge-bear">BELOW — SPY @ $655.38 (-2.57%)</span></td></tr>',
              '<td>${{SPY_MA20}}</td><td><span class="badge badge-bear">BELOW — SPY @ ${{SPY_PRICE}} ({{SPY_VS_20MA}}%)</span></td></tr>')
t = t.replace('<td>26.15</td><td><span class="badge badge-warn">ELEVATED — Above 20 (Caution)</span></td></tr>',
              '<td>{{VIX}}</td><td><span class="badge badge-warn">ELEVATED — Above 20 (Caution)</span></td></tr>')
t = t.replace('<td>T2108 (% above 40MA)</td><td>~18–20%</td><td><span class="badge badge-bear">OVERSOLD — Below 20%</span></td></tr>',
              '<td>T2108 (% above 40MA)</td><td>{{T2108}}%</td><td><span class="badge badge-bear">OVERSOLD — Below 20%</span></td></tr>')
t = t.replace('<td>$SPXA20R</td><td>40.00%</td><td><span class="badge badge-warn">RECOVERING — Up from 12.60%</span></td></tr>',
              '<td>$SPXA20R</td><td>{{SPXA20R}}%</td><td><span class="badge badge-bear">BEARISH</span></td></tr>')

# ── STEP 1A: MACRO TABLE ──────────────────────────────────────────────────────
# SPY
t = t.replace(
    '<td><strong>SPY (S&amp;P 500)</strong></td>\n      <td><strong>$655.38</strong></td>\n      <td class="green"><strong>+1.05%</strong></td>\n      <td class="red">-2.57%</td>\n      <td class="red">-3.82%</td>\n      <td class="red">-0.22%</td>\n      <td class="red"><strong>37.2</strong></td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td><strong>SPY (S&amp;P 500)</strong></td>\n      <td><strong>${{SPY_PRICE}}</strong></td>\n      <td class="{{SPY_CHG_COLOR}}"><strong>{{SPY_CHG}}%</strong></td>\n      <td class="{{SPY_20_COLOR}}">{{SPY_VS_20MA}}%</td>\n      <td class="{{SPY_50_COLOR}}">{{SPY_VS_50MA}}%</td>\n      <td class="{{SPY_200_COLOR}}">{{SPY_VS_200MA}}%</td>\n      <td class="{{SPY_RSI_COLOR}}"><strong>{{SPY_RSI}}</strong></td>\n      <td><span class="badge {{SPY_BADGE}}">{{SPY_SIGNAL}}</span></td>'
)
# QQQ
t = t.replace(
    '<td>QQQ (Nasdaq 100)</td>\n      <td>$588.00</td>\n      <td class="green">+1.02%</td>\n      <td class="red">-2.37%</td>\n      <td class="red">-3.65%</td>\n      <td class="red">-0.73%</td>\n      <td class="red">40.2</td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td>QQQ (Nasdaq 100)</td>\n      <td>${{QQQ_PRICE}}</td>\n      <td class="{{QQQ_CHG_COLOR}}">{{QQQ_CHG}}%</td>\n      <td class="{{QQQ_20_COLOR}}">{{QQQ_VS_20MA}}%</td>\n      <td class="{{QQQ_50_COLOR}}">{{QQQ_VS_50MA}}%</td>\n      <td class="{{QQQ_200_COLOR}}">{{QQQ_VS_200MA}}%</td>\n      <td class="{{QQQ_RSI_COLOR}}">{{QQQ_RSI}}</td>\n      <td><span class="badge {{QQQ_BADGE}}">{{QQQ_SIGNAL}}</span></td>'
)
# IWM
t = t.replace(
    '<td>IWM (Russell 2000)</td>\n      <td>$247.45</td>\n      <td class="green">+2.16%</td>\n      <td class="red">-2.52%</td>\n      <td class="red">-4.56%</td>\n      <td class="green">+3.00%</td>\n      <td class="yellow">42.0</td>\n      <td><span class="badge badge-warn">BELOW 20/50MA</span></td>',
    '<td>IWM (Russell 2000)</td>\n      <td>${{IWM_PRICE}}</td>\n      <td class="{{IWM_CHG_COLOR}}">{{IWM_CHG}}%</td>\n      <td class="{{IWM_20_COLOR}}">{{IWM_VS_20MA}}%</td>\n      <td class="{{IWM_50_COLOR}}">{{IWM_VS_50MA}}%</td>\n      <td class="{{IWM_200_COLOR}}">{{IWM_VS_200MA}}%</td>\n      <td class="{{IWM_RSI_COLOR}}">{{IWM_RSI}}</td>\n      <td><span class="badge {{IWM_BADGE}}">{{IWM_SIGNAL}}</span></td>'
)
# DIA
t = t.replace(
    '<td>DIA (Dow Jones)</td>\n      <td>$462.08</td>\n      <td class="green">+1.38%</td>\n      <td class="red">-3.01%</td>\n      <td class="red">-5.08%</td>\n      <td class="red">-0.80%</td>\n      <td class="red">34.6</td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td>DIA (Dow Jones)</td>\n      <td>${{DIA_PRICE}}</td>\n      <td class="{{DIA_CHG_COLOR}}">{{DIA_CHG}}%</td>\n      <td class="{{DIA_20_COLOR}}">{{DIA_VS_20MA}}%</td>\n      <td class="{{DIA_50_COLOR}}">{{DIA_VS_50MA}}%</td>\n      <td class="{{DIA_200_COLOR}}">{{DIA_VS_200MA}}%</td>\n      <td class="{{DIA_RSI_COLOR}}">{{DIA_RSI}}</td>\n      <td><span class="badge {{DIA_BADGE}}">{{DIA_SIGNAL}}</span></td>'
)
# VIX
t = t.replace(
    '<td><strong>VIX</strong></td>\n      <td><strong>26.15</strong></td>\n      <td class="green">-2.35%</td>\n      <td colspan="3">—</td>\n      <td class="yellow">56.8</td>\n      <td><span class="badge badge-warn">ELEVATED (>20)</span></td>',
    '<td><strong>VIX</strong></td>\n      <td><strong>{{VIX}}</strong></td>\n      <td class="{{VIX_CHG_COLOR}}">{{VIX_CHG}}%</td>\n      <td colspan="3">—</td>\n      <td class="yellow">—</td>\n      <td><span class="badge badge-warn">ELEVATED (>20)</span></td>'
)
# GLD
t = t.replace(
    '<td>GLD (Gold)</td>\n      <td>$404.04</td>\n      <td class="red">-2.26%</td>\n      <td class="red">-12.55%</td>\n      <td class="red">-11.38%</td>\n      <td class="green">+7.86%</td>\n      <td class="red">27.4</td>\n      <td><span class="badge badge-warn">PULLBACK — Above 200MA</span></td>',
    '<td>GLD (Gold)</td>\n      <td>${{GLD_PRICE}}</td>\n      <td class="{{GLD_CHG_COLOR}}">{{GLD_CHG}}%</td>\n      <td class="{{GLD_20_COLOR}}">{{GLD_VS_20MA}}%</td>\n      <td class="{{GLD_50_COLOR}}">{{GLD_VS_50MA}}%</td>\n      <td class="{{GLD_200_COLOR}}">{{GLD_VS_200MA}}%</td>\n      <td class="{{GLD_RSI_COLOR}}">{{GLD_RSI}}</td>\n      <td><span class="badge {{GLD_BADGE}}">{{GLD_SIGNAL}}</span></td>'
)
# USO
t = t.replace(
    '<td>USO (Oil)</td>\n      <td>$110.56</td>\n      <td class="red">-8.95%</td>\n      <td class="green">+7.47%</td>\n      <td class="green">+27.57%</td>\n      <td class="green">+44.71%</td>\n      <td class="yellow">59.5</td>\n      <td><span class="badge badge-bull">ABOVE ALL MAs</span></td>',
    '<td>USO (Oil)</td>\n      <td>${{USO_PRICE}}</td>\n      <td class="{{USO_CHG_COLOR}}">{{USO_CHG}}%</td>\n      <td class="{{USO_20_COLOR}}">{{USO_VS_20MA}}%</td>\n      <td class="{{USO_50_COLOR}}">{{USO_VS_50MA}}%</td>\n      <td class="{{USO_200_COLOR}}">{{USO_VS_200MA}}%</td>\n      <td class="{{USO_RSI_COLOR}}">{{USO_RSI}}</td>\n      <td><span class="badge {{USO_BADGE}}">{{USO_SIGNAL}}</span></td>'
)
# TLT
t = t.replace(
    '<td>TLT (20Y Treasury)</td>\n      <td>$86.39</td>\n      <td class="green">+0.65%</td>\n      <td class="red">-2.09%</td>\n      <td class="red">-1.67%</td>\n      <td class="red">-0.42%</td>\n      <td class="red">40.2</td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td>TLT (20Y Treasury)</td>\n      <td>${{TLT_PRICE}}</td>\n      <td class="{{TLT_CHG_COLOR}}">{{TLT_CHG}}%</td>\n      <td class="{{TLT_20_COLOR}}">{{TLT_VS_20MA}}%</td>\n      <td class="{{TLT_50_COLOR}}">{{TLT_VS_50MA}}%</td>\n      <td class="{{TLT_200_COLOR}}">{{TLT_VS_200MA}}%</td>\n      <td class="{{TLT_RSI_COLOR}}">{{TLT_RSI}}</td>\n      <td><span class="badge {{TLT_BADGE}}">{{TLT_SIGNAL}}</span></td>'
)
# TNX
t = t.replace(
    '<td>10Y Yield (^TNX)</td>\n      <td>4.33%</td>\n      <td class="red">-1.30%</td>\n      <td class="green">+4.09%</td>\n      <td class="green">+3.84%</td>\n      <td class="green">+3.34%</td>\n      <td class="yellow">63.5</td>\n      <td><span class="badge badge-warn">ABOVE ALL MAs — Elevated</span></td>',
    '<td>10Y Yield (^TNX)</td>\n      <td>{{TNX_PRICE}}%</td>\n      <td class="{{TNX_CHG_COLOR}}">{{TNX_CHG}}%</td>\n      <td class="{{TNX_20_COLOR}}">{{TNX_VS_20MA}}%</td>\n      <td class="{{TNX_50_COLOR}}">{{TNX_VS_50MA}}%</td>\n      <td class="{{TNX_200_COLOR}}">{{TNX_VS_200MA}}%</td>\n      <td class="{{TNX_RSI_COLOR}}">{{TNX_RSI}}</td>\n      <td><span class="badge {{TNX_BADGE}}">{{TNX_SIGNAL}}</span></td>'
)
# DXY
t = t.replace(
    '<td>DXY (US Dollar)</td>\n      <td>99.15</td>\n      <td class="red">-0.50%</td>\n      <td class="green">+0.14%</td>\n      <td class="green">+0.93%</td>\n      <td class="green">+0.76%</td>\n      <td class="yellow">52.6</td>\n      <td><span class="badge badge-neutral">NEUTRAL</span></td>',
    '<td>DXY (US Dollar)</td>\n      <td>{{DXY_PRICE}}</td>\n      <td class="{{DXY_CHG_COLOR}}">{{DXY_CHG}}%</td>\n      <td class="{{DXY_20_COLOR}}">{{DXY_VS_20MA}}%</td>\n      <td class="{{DXY_50_COLOR}}">{{DXY_VS_50MA}}%</td>\n      <td class="{{DXY_200_COLOR}}">{{DXY_VS_200MA}}%</td>\n      <td class="{{DXY_RSI_COLOR}}">{{DXY_RSI}}</td>\n      <td><span class="badge {{DXY_BADGE}}">{{DXY_SIGNAL}}</span></td>'
)
# Macro summary note
t = t.replace(
    '<div class="note">📌 宏觀總結: 市場今日出現技術性反彈 — SPY +1.05%，IWM +2.16%（小型股相對強勢）。VIX 微降至 26.15，仍在危險區間。黃金 GLD 大跌 -2.26%（可能是獲利回吐），石油 USO 大跌 -8.95%（伊朗戰爭緊張局勢緩和）。10Y 收益率 4.33% 仍高企。SPY 仍在 200MA ($656.85) 以下，反彈尚未確認趨勢轉向。</div>',
    '<div class="note">📌 宏觀總結: {{MACRO_SUMMARY}}</div>'
)

# ── STEP 1B: NEWS ─────────────────────────────────────────────────────────────
import re
t = re.sub(
    r'(<!-- STEP 1B.*?-->\n<div class="section">.*?<div class="section-title">.*?</div>\n)(.*?)(</div>\n<!-- STEP 2)',
    r'\1{{NEWS_ITEMS}}\3',
    t,
    flags=re.DOTALL
)

# ── STEP 2: FULLSTACK ─────────────────────────────────────────────────────────
t = t.replace(
    '<div class="note">⚠️ Fullstack Market Model page requires member login. Screenshot not available for this session. Please check <a href="https://fullstacktrading.com/market-model/" style="color:#58a6ff" target="_blank">fullstacktrading.com/market-model/</a> directly for the current model reading. Based on prior data (Mar 20), model was BULLISH (high exposure recommended).</div>',
    '<img src="{{FULLSTACK_IMG}}" alt="Fullstack Market Model {{REPORT_DATE_SHORT}}" style="max-width:100%;border-radius:8px;margin-top:8px;">'
)

# ── STEP 3: SENTIMENT ─────────────────────────────────────────────────────────
t = t.replace('<td><strong class="red">16 — EXTREME FEAR</strong></td>', '<td><strong class="red">{{FEAR_GREED}} — {{FEAR_GREED_LABEL}}</strong></td>')
t = t.replace('<td><strong class="red">19.44</strong> (as of Mar 18)</td>', '<td><strong class="red">{{NAAIM}}</strong> (as of {{NAAIM_DATE}})</td>')
t = t.replace('<td>26.15 (-2.35%)</td>', '<td>{{VIX}} ({{VIX_CHG}}%)</td>')
t = t.replace('<td>~18–20% (Stockbee MM)</td>', '<td>{{T2108}}% (Stockbee MM)</td>')
t = t.replace(
    '<div class="note">📌 情緒總結: Fear &amp; Greed 16 (Extreme Fear) 維持歷史低位。NAAIM 19.44 顯示機構投資者已大幅減倉至接近空倉水平。VIX 26.15 雖較昨日有所回落，但仍高於 20 的警戒線。整體情緒極度悲觀，歷史上此水平往往預示中期底部，但需等待技術確認。</div>',
    '<div class="note">📌 情緒總結: {{SENTIMENT_SUMMARY}}</div>'
)

# ── STEP 3: SENTIMENT SCORECARD BADGES ───────────────────────────────────────
t = t.replace('<span class="badge badge-bear">EXTREME FEAR</span>', '<span class="badge {{FEAR_GREED_BADGE}}">{{FEAR_GREED_LABEL}}</span>')
t = t.replace('<span class="badge badge-bear">HEAVILY UNDERWEIGHT</span>', '<span class="badge {{NAAIM_BADGE}}">{{NAAIM_SIGNAL}}</span>')

# ── STEP 4A: INDEX VS MAs TABLE ───────────────────────────────────────────────
# SPY in 4A (different format from 1A - has MA price columns)
t = t.replace(
    '<td><strong>SPY (S&amp;P 500)</strong></td>\n      <td><strong>$655.38</strong></td>\n      <td class="green"><strong>+1.05%</strong></td>\n      <td>$672.66</td><td class="red">-2.57%</td>\n      <td>$681.42</td><td class="red">-3.82%</td>\n      <td>$656.85</td><td class="red">-0.22%</td>\n      <td class="red"><strong>37.2</strong></td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td><strong>SPY (S&amp;P 500)</strong></td>\n      <td><strong>${{SPY_PRICE}}</strong></td>\n      <td class="{{SPY_CHG_COLOR}}"><strong>{{SPY_CHG}}%</strong></td>\n      <td>${{SPY_MA20}}</td><td class="{{SPY_20_COLOR}}">{{SPY_VS_20MA}}%</td>\n      <td>${{SPY_MA50}}</td><td class="{{SPY_50_COLOR}}">{{SPY_VS_50MA}}%</td>\n      <td>${{SPY_MA200}}</td><td class="{{SPY_200_COLOR}}">{{SPY_VS_200MA}}%</td>\n      <td class="{{SPY_RSI_COLOR}}"><strong>{{SPY_RSI}}</strong></td>\n      <td><span class="badge {{SPY_BADGE}}">{{SPY_SIGNAL}}</span></td>'
)
# QQQ in 4A
t = t.replace(
    '<td>QQQ (Nasdaq 100)</td>\n      <td>$588.00</td>\n      <td class="green">+1.02%</td>\n      <td>$601.96</td><td class="red">-2.37%</td>\n      <td>$609.89</td><td class="red">-3.65%</td>\n      <td>$592.34</td><td class="red">-0.73%</td>\n      <td class="red">40.2</td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td>QQQ (Nasdaq 100)</td>\n      <td>${{QQQ_PRICE}}</td>\n      <td class="{{QQQ_CHG_COLOR}}">{{QQQ_CHG}}%</td>\n      <td>${{QQQ_MA20}}</td><td class="{{QQQ_20_COLOR}}">{{QQQ_VS_20MA}}%</td>\n      <td>${{QQQ_MA50}}</td><td class="{{QQQ_50_COLOR}}">{{QQQ_VS_50MA}}%</td>\n      <td>${{QQQ_MA200}}</td><td class="{{QQQ_200_COLOR}}">{{QQQ_VS_200MA}}%</td>\n      <td class="{{QQQ_RSI_COLOR}}">{{QQQ_RSI}}</td>\n      <td><span class="badge {{QQQ_BADGE}}">{{QQQ_SIGNAL}}</span></td>'
)
# IWM in 4A
t = t.replace(
    '<td>IWM (Russell 2000)</td>\n      <td>$247.45</td>\n      <td class="green">+2.16%</td>\n      <td>$253.85</td><td class="red">-2.52%</td>\n      <td>$259.28</td><td class="red">-4.56%</td>\n      <td>$240.23</td><td class="green">+3.00%</td>\n      <td class="yellow">42.0</td>\n      <td><span class="badge badge-warn">BELOW 20/50MA</span></td>',
    '<td>IWM (Russell 2000)</td>\n      <td>${{IWM_PRICE}}</td>\n      <td class="{{IWM_CHG_COLOR}}">{{IWM_CHG}}%</td>\n      <td>${{IWM_MA20}}</td><td class="{{IWM_20_COLOR}}">{{IWM_VS_20MA}}%</td>\n      <td>${{IWM_MA50}}</td><td class="{{IWM_50_COLOR}}">{{IWM_VS_50MA}}%</td>\n      <td>${{IWM_MA200}}</td><td class="{{IWM_200_COLOR}}">{{IWM_VS_200MA}}%</td>\n      <td class="{{IWM_RSI_COLOR}}">{{IWM_RSI}}</td>\n      <td><span class="badge {{IWM_BADGE}}">{{IWM_SIGNAL}}</span></td>'
)
# DIA in 4A
t = t.replace(
    '<td>DIA (DJI)</td>\n      <td>$462.08</td>\n      <td class="green">+1.38%</td>\n      <td>$476.40</td><td class="red">-3.01%</td>\n      <td>$486.82</td><td class="red">-5.08%</td>\n      <td>$465.82</td><td class="red">-0.80%</td>\n      <td class="red">34.6</td>\n      <td><span class="badge badge-bear">BELOW ALL MAs</span></td>',
    '<td>DIA (DJI)</td>\n      <td>${{DIA_PRICE}}</td>\n      <td class="{{DIA_CHG_COLOR}}">{{DIA_CHG}}%</td>\n      <td>${{DIA_MA20}}</td><td class="{{DIA_20_COLOR}}">{{DIA_VS_20MA}}%</td>\n      <td>${{DIA_MA50}}</td><td class="{{DIA_50_COLOR}}">{{DIA_VS_50MA}}%</td>\n      <td>${{DIA_MA200}}</td><td class="{{DIA_200_COLOR}}">{{DIA_VS_200MA}}%</td>\n      <td class="{{DIA_RSI_COLOR}}">{{DIA_RSI}}</td>\n      <td><span class="badge {{DIA_BADGE}}">{{DIA_SIGNAL}}</span></td>'
)
# 4A summary note
t = t.replace(
    '<div class="note">📌 4A 總結: SPY 仍在所有移動平均線以下。DIA 跌破 200MA。IWM 仍在 200MA 以上（小型股相對強勢）。QQQ 在所有 MA 以下。</div>',
    '<div class="note">📌 4A 總結: {{STEP4A_SUMMARY}}</div>'
)

# ── STEP 4B: SECTOR ETF TABLE ─────────────────────────────────────────────────
t = re.sub(
    r'(<tr><th>ETF</th><th>Sector</th><th>Price</th><th>1D Chg</th><th>vs 20MA</th><th>vs 50MA</th><th>vs 200MA</th><th>RSI\(14\)</th><th>Signal</th></tr>\n)(.*?)(</table>\n  <div class="note">📌 板塊 ETF 總結)',
    r'\1{{SECTOR_ROWS}}\3',
    t,
    flags=re.DOTALL
)
t = t.replace(
    '<div class="note">📌 板塊 ETF 總結 (RSI 排序): XLE (Energy) RSI 68.4 唯一強勢板塊，且在所有移動平均線之上。XLV (Health Care) RSI 26.3 最超賣。XLP (Consumer Staples) RSI 28.8 極度超賣。SPY RSI 37.2。IWM (+2.16%) 今日表現最佳，顯示小型股有相對強勢。所有板塊 RSI 均低於 50，市場整體偏弱。</div>',
    '<div class="note">📌 板塊 ETF 總結 (RSI 排序): {{SECTOR_SUMMARY}}</div>'
)

# ── STEP 4C: BREADTH TABLE VALUES ────────────────────────────────────────────
t = t.replace(
    '<tr><td rowspan="3"><strong>S&amp;P 500</strong></td><td>$SPXA20R</td><td>20MA</td><td class="yellow">40.00%</td><td><span class="badge badge-warn">RECOVERING — Up from 12.60%</span></td><td>StockCharts</td></tr>',
    '<tr><td rowspan="3"><strong>S&amp;P 500</strong></td><td>$SPXA20R</td><td>20MA</td><td class="{{SPXA20R_COLOR}}">{{SPXA20R}}%</td><td><span class="badge {{SPXA20R_BADGE}}">{{SPXA20R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td>$SPXA50R</td><td>50MA</td><td class="red">21.00%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>',
    '<tr><td>$SPXA50R</td><td>50MA</td><td class="{{SPXA50R_COLOR}}">{{SPXA50R}}%</td><td><span class="badge {{SPXA50R_BADGE}}">{{SPXA50R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td>$SPXA200R</td><td>200MA</td><td class="yellow">49.00%</td><td><span class="badge badge-warn">WARNING — Near 50%</span></td><td>StockCharts</td></tr>',
    '<tr><td>$SPXA200R</td><td>200MA</td><td class="{{SPXA200R_COLOR}}">{{SPXA200R}}%</td><td><span class="badge {{SPXA200R_BADGE}}">{{SPXA200R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td rowspan="3"><strong>Nasdaq 100</strong></td><td>$NDXA20R</td><td>20MA</td><td class="yellow">27.00%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>',
    '<tr><td rowspan="3"><strong>Nasdaq 100</strong></td><td>$NDXA20R</td><td>20MA</td><td class="{{NDXA20R_COLOR}}">{{NDXA20R}}%</td><td><span class="badge {{NDXA20R_BADGE}}">{{NDXA20R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td>$NDXA50R</td><td>50MA</td><td class="red">21.00%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>',
    '<tr><td>$NDXA50R</td><td>50MA</td><td class="{{NDXA50R_COLOR}}">{{NDXA50R}}%</td><td><span class="badge {{NDXA50R_BADGE}}">{{NDXA50R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td>$NDXA200R</td><td>200MA</td><td class="yellow">43.00%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>',
    '<tr><td>$NDXA200R</td><td>200MA</td><td class="{{NDXA200R_COLOR}}">{{NDXA200R}}%</td><td><span class="badge {{NDXA200R_BADGE}}">{{NDXA200R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td rowspan="3"><strong>NYSE</strong></td><td>$NYA20R</td><td>20MA</td><td class="red">23.31%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>',
    '<tr><td rowspan="3"><strong>NYSE</strong></td><td>$NYA20R</td><td>20MA</td><td class="{{NYA20R_COLOR}}">{{NYA20R}}%</td><td><span class="badge {{NYA20R_BADGE}}">{{NYA20R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td>$NYA50R</td><td>50MA</td><td class="red">25.83%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>',
    '<tr><td>$NYA50R</td><td>50MA</td><td class="{{NYA50R_COLOR}}">{{NYA50R}}%</td><td><span class="badge {{NYA50R_BADGE}}">{{NYA50R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)
t = t.replace(
    '<tr><td>$NYA200R</td><td>200MA</td><td class="yellow">46.79%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>',
    '<tr><td>$NYA200R</td><td>200MA</td><td class="{{NYA200R_COLOR}}">{{NYA200R}}%</td><td><span class="badge {{NYA200R_BADGE}}">{{NYA200R_SIGNAL}}</span></td><td>StockCharts</td></tr>'
)

# ── STEP 4C: CHART CARD TITLES & IMAGES ──────────────────────────────────────
CDN_OLD = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"
t = t.replace('S&amp;P 500 — % Above 20MA ($SPXA20R) = 40.00%', 'S&amp;P 500 — % Above 20MA ($SPXA20R) = {{SPXA20R}}%')
t = t.replace('S&amp;P 500 — % Above 50MA ($SPXA50R) = 21.00%', 'S&amp;P 500 — % Above 50MA ($SPXA50R) = {{SPXA50R}}%')
t = t.replace('S&amp;P 500 — % Above 200MA ($SPXA200R) = 49.00%', 'S&amp;P 500 — % Above 200MA ($SPXA200R) = {{SPXA200R}}%')
t = t.replace('Nasdaq 100 — % Above 20MA ($NDXA20R) = 27.00%', 'Nasdaq 100 — % Above 20MA ($NDXA20R) = {{NDXA20R}}%')
t = t.replace('Nasdaq 100 — % Above 50MA ($NDXA50R) = 21.00%', 'Nasdaq 100 — % Above 50MA ($NDXA50R) = {{NDXA50R}}%')
t = t.replace('Nasdaq 100 — % Above 200MA ($NDXA200R) = 43.00%', 'Nasdaq 100 — % Above 200MA ($NDXA200R) = {{NDXA200R}}%')
t = t.replace('NYSE — % Above 20MA ($NYA20R) = 23.31%', 'NYSE — % Above 20MA ($NYA20R) = {{NYA20R}}%')
t = t.replace('NYSE — % Above 50MA ($NYA50R) = 25.83%', 'NYSE — % Above 50MA ($NYA50R) = {{NYA50R}}%')
t = t.replace('NYSE — % Above 200MA ($NYA200R) = 46.79%', 'NYSE — % Above 200MA ($NYA200R) = {{NYA200R}}%')

# Replace CDN image URLs
t = t.replace(CDN_OLD + 'CTUzxaAqcpaevTvi.png', '{{IMG_SPXA20R}}')
t = t.replace(CDN_OLD + 'DQlweCCLSHauCyBn.png', '{{IMG_SPXA50R}}')
t = t.replace(CDN_OLD + 'ivuLkuZeqNkFruSD.png', '{{IMG_SPXA200R}}')
t = t.replace(CDN_OLD + 'DqtUSvHOzZlOnbym.png', '{{IMG_NDXA20R}}')
t = t.replace(CDN_OLD + 'FrnJGRHehDeBfSSu.png', '{{IMG_NDXA50R}}')
t = t.replace(CDN_OLD + 'VzGlsCvOlYrYArzm.png', '{{IMG_NDXA200R}}')
t = t.replace(CDN_OLD + 'aLRUwqWnnOAkVUsE.png', '{{IMG_NYA20R}}')
t = t.replace(CDN_OLD + 'dwSNMinuFLvRFcBl.png', '{{IMG_NYA50R}}')
t = t.replace(CDN_OLD + 'DWVaHZsujoNKTGFB.png', '{{IMG_NYA200R}}')

# ── STEP 5A: SECTOR PERFORMANCE TABLE ────────────────────────────────────────
t = re.sub(
    r'(<tr><th>Rank</th><th>Sector</th><th>1D Chg</th><th>1W Chg</th><th>1M Chg</th><th>YTD Chg</th></tr>\n)(.*?)(</table>\n  <div class="source-label">Source: <a href="https://finviz.com/groups.ashx\?g=sector)',
    r'\1{{SECTOR5A_ROWS}}\3',
    t,
    flags=re.DOTALL
)

# ── STEP 5B: INDUSTRY LEADERS TABLE ──────────────────────────────────────────
t = re.sub(
    r'(<tr><th>Rank</th><th>Industry</th><th>Sector</th><th>1D Chg</th></tr>\n)(.*?)(</table>\n  <div class="source-label">Source: <a href="https://finviz.com/groups)',
    r'\1{{INDUSTRY_ROWS}}\3',
    t,
    flags=re.DOTALL
)

# ── STEP 6A: MARKETINOUT IMAGE ────────────────────────────────────────────────
t = t.replace(CDN_OLD + 'rhOaquSPLXjAmwcG.png', '{{IMG_MARKETINOUT}}')

# ── STEP 6B: STOCKBEE IMAGE & VALUES ─────────────────────────────────────────
t = t.replace(CDN_OLD + 'brlBogwNeKchEFhK.png', '{{IMG_STOCKBEE}}')
t = t.replace('Up 4%+: <strong>235</strong>', 'Up 4%+: <strong>{{STOCKBEE_UP4}}</strong>')
t = t.replace('Down 4%+: <strong>85</strong>', 'Down 4%+: <strong>{{STOCKBEE_DOWN4}}</strong>')
t = t.replace('<td>T2108 (% Above 40MA)</td>\n      <td>~18–20% (Stockbee MM)</td>', '<td>T2108 (% Above 40MA)</td>\n      <td>{{T2108}}% (Stockbee MM)</td>')

# ── STEP 7: BULL VS BEAR ──────────────────────────────────────────────────────
# Replace the entire bull/bear section content
t = re.sub(
    r'(<!-- STEP 7.*?-->\n<div class="section">.*?<div class="section-title">.*?</div>\n)(.*?)(</div>\n<!-- REGIME)',
    r'\1{{BULL_BEAR_CONTENT}}\3',
    t,
    flags=re.DOTALL
)

# ── REGIME BOX ────────────────────────────────────────────────────────────────
t = t.replace(
    '<div class="regime-title">⚠ REGIME: BEARISH-TO-NEUTRAL TRANSITION (Level 6–7 of 9)</div>',
    '<div class="regime-title">⚠ REGIME: {{REGIME_TITLE}}</div>'
)
t = t.replace(
    '<span class="badge badge-warn">26.15 (ELEVATED — still above 20)</span>',
    '<span class="badge badge-warn">{{VIX}} (ELEVATED — still above 20)</span>'
)
t = t.replace(
    '<span class="badge badge-bear">Below 20MA, 50MA &amp; 200MA (-0.22% vs 200MA)</span>',
    '<span class="badge badge-bear">Below 20MA, 50MA &amp; 200MA ({{SPY_VS_200MA}}% vs 200MA)</span>'
)
t = t.replace(
    '<span class="badge badge-bear">BREACHED — Below 200MA (-0.80%)</span>',
    '<span class="badge badge-bear">BREACHED — Below 200MA ({{DIA_VS_200MA}}%)</span>'
)
t = t.replace(
    '<span class="badge badge-bear">16 — Extreme Fear</span>',
    '<span class="badge badge-bear">{{FEAR_GREED}} — {{FEAR_GREED_LABEL}}</span>'
)
t = t.replace(
    '<span class="badge badge-warn">Energy (RSI 68.4) + Basic Materials leading</span>',
    '<span class="badge badge-warn">{{SECTOR_LEADER}}</span>'
)
t = t.replace(
    '<span class="badge badge-bear">~18–20% (Oversold)</span>',
    '<span class="badge badge-bear">{{T2108}}% (Oversold)</span>'
)
t = t.replace(
    '<span class="badge badge-warn">40.00% (Recovering from 12.60%)</span>',
    '<span class="badge badge-warn">{{SPXA20R}}%</span>'
)
t = t.replace(
    '<span class="badge badge-bear">19.44 — Near empty (Mar 18)</span>',
    '<span class="badge badge-bear">{{NAAIM}} — ({{NAAIM_DATE}})</span>'
)
t = t.replace(
    '<div class="note" style="margin-top:12px">\n    📌 <strong>交易建議 Trading Guidance:</strong> 市場環境從全面偏空型 (Bearish Level 8–9) 轉向過渡期 (Level 6–7)。今日反彈顯著，$SPXA20R 大幅回升至 40%，Stockbee 今日比率 2.81:1。然而，SPY 仍在 200MA ($656.85) 以下，VIX 26.15 仍高。\n    <br><br>\n    關鍵觀察點：(1) SPY 能否明日收復 200MA ($656.85)；(2) VIX 能否跌破 20；(3) $SPXA50R 能否突破 30%。\n    <br><br>\n    建議：(1) 不開大倉新多；(2) 能源板塊 (XLE, RSI 68.4) 和 Basic Materials 是最強板塊，可小倉參與；(3) 等待 VIX 回落至 20 以下、SPY 收復 200MA 才考慮加倉；(4) 今日反彈是事件驅動型（伊朗緊張局勢緩和），需觀察明日是否能延續。\n  </div>',
    '<div class="note" style="margin-top:12px">\n    📌 <strong>交易建議 Trading Guidance:</strong> {{TRADING_GUIDANCE}}\n  </div>'
)

# Save template
with open('/home/ubuntu/swing-trader-daily/TEMPLATE.html', 'w') as f:
    f.write(t)

# Verify: count remaining placeholders
import re
placeholders = re.findall(r'\{\{[A-Z0-9_]+\}\}', t)
unique = sorted(set(placeholders))
print(f"Template saved. {len(unique)} unique placeholders:")
for p in unique:
    print(f"  {p}")

# Verify no old data values remain
old_values = ['655.38', '26.15', '19.44', '40.00%', '23.31%', '46.79%', '247.45', '462.08', '588.00']
print("\nOld value check:")
for v in old_values:
    if v in t:
        print(f"  ✗ STILL PRESENT: {v}")
    else:
        print(f"  ✓ Replaced: {v}")
