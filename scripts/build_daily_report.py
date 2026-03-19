#!/usr/bin/env python3
"""
Mar 19 EOD Report Builder v3
- Uses Mar 18 HTML as exact template
- Updates data values only
- Applies all confirmed changes:
  1. Step 2: Screenshot only (no data table), correct URL .co/market-model
  2. Step 4A: Remove SPY daily chart
  3. Step 4B: Add RSI 14, rank by RSI descending
  4. Step 4C: Use StockCharts screenshots ($SPXA20R, $SPXA50R, $SPXA200R)
  5. Step 5B: Use actual Finviz industry data (top/bottom 5)
  6. Step 6A: Use actual MarketInOut A/D screenshot (no login needed)
  7. Step 6B: Use actual Stockbee data (T2108=22, up4%=109, dn4%=476, 5d=0.57, 10d=0.73)
  8. Remove Step 7 UFO
  9. Remove Report Comparison Notes
"""

# ============================================================
# ALL CONFIRMED DATA (Mar 18, 2026 EOD Close)
# ============================================================

CDN_BASE = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"

# Screenshot CDN URLs (uploaded Mar 19)
FULLSTACK_IMG   = CDN_BASE + "LOlTwYvTooSklMVy.png"   # fullstack_full_v2.png
SPXA20R_IMG     = CDN_BASE + "gWLTengyKPRvytUI.png"   # spxa20r_chart.png
SPXA50R_IMG     = CDN_BASE + "clfVeocRWUYqLQim.png"   # spxa50r_chart.png
SPXA200R_IMG    = CDN_BASE + "dKEcGkLkwvAFwfqc.png"   # spxa200r_chart.png
MARKETINOUT_IMG = CDN_BASE + "ChzHhoHIMzuRUQiH.png"   # marketinout_ad_full.png
STOCKBEE_IMG    = CDN_BASE + "djnhRAuFBQrMyjoK.png"   # stockbee_t2108_mar19.png

# Indices (Mar 18 EOD close)
INDICES = [
    # (name, price, chg_pct, vs20, vs50, vs200, trend_badge, trend_class)
    ("SPY (S&P 500)",   661.43, -1.40, -2.58, -3.49, +0.57, "BELOW 20/50, ABOVE 200", "badge-warn"),
    ("^GSPC (S&P 500)", 6624.38, -1.37, -2.65, -3.58, +0.12, "BELOW 20/50, ABOVE 200", "badge-warn"),
    ("^NDX (Nasdaq 100)", 24423.0, -1.70, -1.70, -2.95, +0.38, "BELOW 20/50, ABOVE 200", "badge-warn"),
    ("^RUT (Russell 2000)", 2478.64, -1.64, -4.12, -5.47, +2.21, "WEAK — BELOW 20/50", "badge-bear"),
    ("^DJI (Dow Jones)", 46225.15, -1.63, -3.98, -5.43, -0.65, "WEAK — BELOW 20/50 & 200", "badge-bear"),
]

# Sector ETFs with RSI14 — sorted by RSI descending
SECTORS = [
    # (etf, sector, price, chg_pct, vs20, vs50, vs200, rsi14, signal_text, signal_class)
    ("XLE",  "Energy",              58.43, -0.14, +3.62, +10.98, +27.77, 74.2, "BULL — ABOVE ALL MAs", "badge-bull"),
    ("XLU",  "Utilities",           46.73, -0.85, -0.38, +4.21,  +8.55,  43.0, "BELOW 20MA, ABOVE 50/200", "badge-neutral"),
    ("XLK",  "Technology",         137.96, -1.13, -1.03, -2.85,  +0.39,  39.4, "BELOW 20/50MA", "badge-warn"),
    ("XLC",  "Comm. Services",     113.66, -1.48, -2.49, -2.55,  +0.83,  35.5, "BELOW 20/50MA", "badge-warn"),
    ("^GSPC","S&P 500 (Benchmark)",6624.38,-1.37, -2.65, -3.58,  +0.12,  None, "BENCHMARK", "badge-info"),  # placeholder, will use SPY
    ("XLRE", "Real Estate",         42.02, -1.64, -2.57, -0.45,  +1.92,  31.5, "BELOW 20MA, ABOVE 50/200", "badge-neutral"),
    ("XLY",  "Consumer Discret.",  110.57, -2.31, -3.64, -6.51,  -4.48,  29.4, "BELOW ALL MAs", "badge-bear"),
    ("^RUT", "Russell 2000",      2478.64, -1.64, -4.12, -5.47,  +2.21,  29.6, "WEAK", "badge-bear"),  # placeholder
    ("XLI",  "Industrials",        165.18, -0.79, -4.11, -2.42,  +6.29,  28.1, "BELOW 20/50MA", "badge-warn"),
    ("SPY",  "S&P 500 (Benchmark)",661.43, -1.40, -2.58, -3.49,  +0.57,  27.6, "BENCHMARK", "badge-info"),
    ("XLV",  "Health Care",        147.14, -1.67, -4.85, -5.58,  +1.86,  26.2, "BELOW 20/50MA", "badge-warn"),
    ("XLF",  "Financials",          48.97, -1.19, -3.37, -6.79,  -6.88,  26.6, "BELOW ALL MAs", "badge-bear"),
    ("XLB",  "Materials",           48.48, -2.10, -5.44, -4.19,  +5.74,  13.8, "BELOW 20/50MA", "badge-warn"),
    ("XLP",  "Consumer Staples",    82.64, -2.43, -4.72, -2.74,  +2.94,  21.7, "BELOW 20/50MA", "badge-warn"),
]

# Use only the 11 sector ETFs + SPY for the table, sorted by RSI
SECTOR_TABLE = [
    # (etf, sector, price, chg_pct, vs20, vs50, vs200, rsi14, signal_text, signal_class)
    ("XLE",  "Energy",              58.43, -0.14, +3.62, +10.98, +27.77, 74.2, "BULL — ABOVE ALL MAs", "badge-bull"),
    ("XLU",  "Utilities",           46.73, -0.85, -0.38, +4.21,  +8.55,  43.0, "BELOW 20MA, ABOVE 50/200", "badge-neutral"),
    ("XLK",  "Technology",         137.96, -1.13, -1.03, -2.85,  +0.39,  39.4, "BELOW 20/50MA", "badge-warn"),
    ("XLC",  "Comm. Services",     113.66, -1.48, -2.49, -2.55,  +0.83,  35.5, "BELOW 20/50MA", "badge-warn"),
    ("XLRE", "Real Estate",         42.02, -1.64, -2.57, -0.45,  +1.92,  31.5, "BELOW 20MA, ABOVE 50/200", "badge-neutral"),
    ("XLY",  "Consumer Discret.",  110.57, -2.31, -3.64, -6.51,  -4.48,  29.4, "BELOW ALL MAs", "badge-bear"),
    ("XLI",  "Industrials",        165.18, -0.79, -4.11, -2.42,  +6.29,  28.1, "BELOW 20/50MA", "badge-warn"),
    ("XLV",  "Health Care",        147.14, -1.67, -4.85, -5.58,  +1.86,  26.2, "BELOW 20/50MA", "badge-warn"),
    ("XLF",  "Financials",          48.97, -1.19, -3.37, -6.79,  -6.88,  26.6, "BELOW ALL MAs", "badge-bear"),
    ("XLP",  "Consumer Staples",    82.64, -2.43, -4.72, -2.74,  +2.94,  21.7, "BELOW 20/50MA", "badge-warn"),
    ("XLB",  "Materials",           48.48, -2.10, -5.44, -4.19,  +5.74,  13.8, "BELOW 20/50MA", "badge-warn"),
]
# SPY benchmark row (ranked inline by RSI=27.6, between XLV=26.2 and XLI=28.1)
SPY_ROW = ("SPY ★", "S&P 500 (Benchmark)", 661.43, -1.40, -2.58, -3.49, +0.57, 27.6, "BENCHMARK", "badge-info")

# Insert SPY at correct RSI position (between XLI=28.1 and XLV=26.2)
def build_sector_rows_with_spy():
    rows = list(SECTOR_TABLE)
    # Insert SPY between XLI (RSI 28.1) and XLV (RSI 26.2)
    # XLI is at index 6, XLV at index 7 — insert SPY between them
    rows.insert(7, SPY_ROW)
    return rows

def fmt_pct(v, bold=False):
    cls = "green" if v >= 0 else "red"
    sign = "+" if v >= 0 else ""
    val = f"{sign}{v:.2f}%"
    if bold:
        return f'<td class="{cls}"><strong>{val}</strong></td>'
    return f'<td class="{cls}">{val}</td>'

def fmt_vs(v):
    cls = "green" if v >= 0 else "red"
    sign = "+" if v >= 0 else ""
    return f'<td class="{cls}">{sign}{v:.2f}%</td>'

# ============================================================
# BUILD HTML
# ============================================================

html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EOD Market Summary — March 19, 2026 (for Mar 20 Review)</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1117; color: #e6edf3; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6; }
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  .header { background: linear-gradient(135deg, #161b22, #21262d); border: 1px solid #30363d; border-radius: 12px; padding: 24px 30px; margin-bottom: 20px; }
  .header h1 { font-size: 22px; color: #58a6ff; margin-bottom: 6px; }
  .header .subtitle { color: #8b949e; font-size: 13px; }
  .verdict-box { background: #1c1c2e; border: 2px solid #da3633; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; }
  .verdict-title { font-size: 16px; font-weight: bold; color: #f85149; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
  .verdict-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .verdict-item { background: #21262d; border-radius: 8px; padding: 12px 16px; }
  .verdict-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  .verdict-value { font-size: 15px; font-weight: bold; }
  .verdict-action { background: #21262d; border-radius: 8px; padding: 12px 16px; grid-column: 1 / -1; border-left: 3px solid #da3633; }
  .section { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px 24px; margin-bottom: 18px; }
  .section-title { font-size: 15px; font-weight: bold; color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
  .step-badge { background: #1f6feb; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
  .stale-badge { background: #3d2a0a; color: #e3b341; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
  .live-badge { background: #1a4731; color: #3fb950; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { background: #21262d; color: #8b949e; padding: 8px 12px; text-align: left; font-weight: 600; border-bottom: 1px solid #30363d; }
  td { padding: 7px 12px; border-bottom: 1px solid #21262d; }
  tr:hover td { background: #1c2128; }
  .green { color: #3fb950; font-weight: 600; }
  .red { color: #f85149; font-weight: 600; }
  .yellow { color: #d29922; font-weight: 600; }
  .blue { color: #58a6ff; }
  .gray { color: #8b949e; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
  .badge-bull { background: #1a4731; color: #3fb950; }
  .badge-bear { background: #3d1c1c; color: #f85149; }
  .badge-neutral { background: #2d2a1e; color: #d29922; }
  .badge-warn { background: #3d2a0a; color: #e3b341; }
  .badge-info { background: #1f3a5f; color: #58a6ff; }
  .badge-stale { background: #2d2a1e; color: #d29922; font-size: 10px; }
  .chart-img { width: 100%; border-radius: 8px; margin-top: 12px; }
  .screenshot-img { width: 100%; border-radius: 8px; border: 1px solid #30363d; margin-top: 12px; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 14px; }
  .chart-card { background: #21262d; border-radius: 8px; padding: 12px; }
  .chart-card-title { font-size: 12px; color: #c9d1d9; text-align: center; margin-bottom: 8px; font-weight: bold; letter-spacing: 0.3px; }
  .chart-card img { width: 100%; border-radius: 6px; }
  .scorecard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 8px; }
  .score-item { background: #21262d; border-radius: 8px; padding: 12px; text-align: center; }
  .score-label { font-size: 11px; color: #8b949e; margin-bottom: 4px; }
  .score-value { font-size: 18px; font-weight: bold; }
  .regime-box { background: #3d1c1c; border: 1px solid #da3633; border-radius: 8px; padding: 16px; margin-top: 8px; }
  .regime-title { font-size: 16px; font-weight: bold; color: #f85149; margin-bottom: 8px; }
  .note { background: #1c2128; border-left: 3px solid #58a6ff; padding: 10px 14px; border-radius: 0 6px 6px 0; margin-top: 10px; font-size: 13px; color: #8b949e; }
  .flag { background: #2d2a1e; border-left: 3px solid #d29922; padding: 10px 14px; border-radius: 0 6px 6px 0; margin-top: 10px; font-size: 13px; color: #d29922; }
  .unavailable { background: #1c1c1c; border: 1px dashed #555; border-radius: 8px; padding: 16px; text-align: center; color: #555; margin-top: 10px; }
  .unavailable a { color: #58a6ff; }
  .t2108-bar { position: relative; background: #21262d; height: 20px; border-radius: 6px; overflow: hidden; margin-top: 6px; }
  .t2108-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #f85149, #d29922); }
  .t2108-label { position: absolute; right: 8px; top: 2px; font-size: 11px; color: white; font-weight: bold; }
  h3.sub { color: #8b949e; font-size: 13px; margin: 16px 0 10px; text-transform: uppercase; letter-spacing: 0.5px; }
  .divider { border: none; border-top: 1px dashed #30363d; margin: 18px 0; }
  .source-label { font-size: 11px; color: #555; margin-top: 6px; text-align: right; }
  .cal-high { color: #f85149; font-weight: bold; }
  .cal-med { color: #d29922; }
  .cal-low { color: #8b949e; }
  .watchlist-placeholder { background: #1c2128; border: 1px dashed #30363d; border-radius: 8px; padding: 20px; text-align: center; color: #555; font-size: 13px; margin-top: 8px; }
  .spy-row { background: #1a2332 !important; border-left: 3px solid #58a6ff; }
  @media (max-width: 768px) {
    .two-col { grid-template-columns: 1fr; }
    .three-col { grid-template-columns: 1fr; }
    .scorecard { grid-template-columns: repeat(2, 1fr); }
    .verdict-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">

  <!-- ===== TODAY'S VERDICT ===== -->
  <div class="verdict-box">
    <div class="verdict-title">🎯 市場判決 Market Verdict — Mar 19, 2026 Close (for Mar 20 Review)</div>
    <div class="verdict-grid">
      <div class="verdict-item">
        <div class="verdict-label">Market Regime 市場環境</div>
        <div class="verdict-value" style="color:#f85149">⚠ BEARISH (Level 8–9 / 9)</div>
      </div>
      <div class="verdict-item">
        <div class="verdict-label">Fear &amp; Greed Index</div>
        <div class="verdict-value" style="color:#f85149">18 — EXTREME FEAR 😱</div>
      </div>
      <div class="verdict-item">
        <div class="verdict-label">VIX 恐慌指數</div>
        <div class="verdict-value" style="color:#f85149">25.09 — DANGER ZONE ⚠ (+12.16%)</div>
      </div>
      <div class="verdict-item">
        <div class="verdict-label">SPY vs Key MAs</div>
        <div class="verdict-value" style="color:#f85149">BELOW 20MA &amp; 50MA</div>
      </div>
      <div class="verdict-action">
        <div style="color:#8b949e; font-size:12px; margin-bottom:4px">📋 ACTION GUIDANCE 交易指引</div>
        <div style="color:#e6edf3; font-size:14px"><strong>No new longs.</strong> VIX broke above 25 — full bearish regime. Market sold off sharply (-1.40%) with all 11 sectors red. Only XLE (Energy) has structural strength (RSI 74.2). T2108 fell to 22% — deep oversold. Wait for VIX &lt;20 + T2108 &gt;40% before adding any exposure.</div>
        <div style="color:#8b949e; font-size:12px; margin-top:4px">不開新多倉。VIX 突破 25，進入全面熊市環境。T2108 跌至 22%，屬深度超賣。等待 VIX 回落至 20 以下及 T2108 突破 40% 才考慮加倉。</div>
      </div>
    </div>
  </div>

  <!-- ===== KEY LEVELS ===== -->
  <div class="section">
    <div class="section-title">🔑 關鍵水平 Key Levels to Watch</div>
    <table>
      <tr><th>Level</th><th>Value</th><th>Significance</th><th>Bias</th></tr>
      <tr><td>SPX 200MA</td><td class="yellow">$6,615.70</td><td>Must hold — structural support. Breach = full Bearish regime confirmation</td><td><span class="badge badge-warn">CRITICAL SUPPORT</span></td></tr>
      <tr><td>SPX 50MA</td><td class="red">$6,872.82</td><td>Reclaim needed for regime upgrade to Neutral/Defensive</td><td><span class="badge badge-bear">RESISTANCE</span></td></tr>
      <tr><td>SPX 20MA</td><td class="red">$6,803.49</td><td>First resistance above current price ($6,624)</td><td><span class="badge badge-bear">RESISTANCE</span></td></tr>
      <tr><td>VIX 20</td><td class="gray">Current: 25.09</td><td>Bearish → Defensive threshold. Must close below for 3+ days</td><td><span class="badge badge-warn">REGIME TRIGGER</span></td></tr>
      <tr><td>VIX 25</td><td class="red">BREACHED — 25.09</td><td>Above 25 = full Bearish regime confirmed</td><td><span class="badge badge-bear">BREACHED ⚠</span></td></tr>
      <tr><td>T2108</td><td class="red">22% (Oversold)</td><td>Below 20% = Extreme Oversold — potential bounce zone but not signal to buy</td><td><span class="badge badge-bear">OVERSOLD</span></td></tr>
      <tr><td>DJI 200MA</td><td class="red">BREACHED — $46,225 vs $46,529</td><td>Dow Jones now below 200MA — structural deterioration</td><td><span class="badge badge-bear">BREACHED ⚠</span></td></tr>
    </table>
  </div>

  <!-- HEADER -->
  <div class="header">
    <h1>📊 EOD Market Summary — March 19, 2026 Close</h1>
    <div class="subtitle">每日市場總結 | Steps 1–6 | Sources: Yahoo Finance · feargreedmeter.com · Finviz · StockCharts · MarketInOut · Stockbee · forex.tradingcharts.com</div>
    <div class="subtitle" style="margin-top:4px; color:#3fb950">✅ All data live — Mar 18, 2026 EOD close</div>
  </div>

  <!-- STEP 1: MACRO -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 1</span> 宏觀環境 Macro Environment</div>
    <table>
      <tr><th>Indicator</th><th>Value (Mar 18 Close)</th><th>Signal</th><th>Notes</th></tr>
      <tr><td>VIX (Fear Index)</td><td class="red">25.09</td><td><span class="badge badge-bear">DANGER ZONE</span></td><td>+12.16% — broke above 25; full bearish regime confirmed</td></tr>
      <tr><td>CNN Fear &amp; Greed</td><td class="red">18</td><td><span class="badge badge-bear">EXTREME FEAR</span></td><td>Down 2pts from yesterday (20). Source: <a href="https://feargreedmeter.com" style="color:#58a6ff">feargreedmeter.com</a></td></tr>
      <tr><td>Gold (GLD)</td><td class="yellow">$444.74</td><td><span class="badge badge-warn">PULLBACK</span></td><td>-3.16% — pulled back from highs; risk-off partially unwinding</td></tr>
      <tr><td>Oil (USO)</td><td class="yellow">$121.67</td><td><span class="badge badge-warn">ELEVATED</span></td><td>+2.38% — energy demand remains strong; stagflation risk</td></tr>
      <tr><td>10Y Treasury (^TNX)</td><td class="red">4.26%</td><td><span class="badge badge-warn">RISING</span></td><td>+1.43% — yields rising; stagflation narrative strengthening</td></tr>
      <tr><td>USD (UUP proxy)</td><td class="yellow">$27.85</td><td><span class="badge badge-warn">STRENGTHENING</span></td><td>+0.61% — USD strength = headwind for equities</td></tr>
      <tr><td>TLT (20Y Bond ETF)</td><td class="gray">$86.96</td><td><span class="badge badge-neutral">FLAT</span></td><td>-0.56% — bonds not rallying despite equity selloff (stagflation)</td></tr>
    </table>
    <div class="note">📌 宏觀總結: VIX 突破 25 進入危險區，Fear &amp; Greed 跌至 18 (極度恐懼)。黃金 (GLD) 回落 -3.16%，油價 (USO) 繼續上升 +2.38%。10 年期國債收益率升至 4.26%，債券未有因股市下跌而上升，顯示滯脹 (Stagflation) 環境持續。</div>
    <div class="flag">⚠ 關鍵觀察: 下個主席 (Fed Chair 繼任人選) 的討論繼續主導市場敘事，比短期 FOMC 決議更重要。市場正在重新定價長期利率路徑。</div>
  </div>

  <!-- STEP 2: FULLSTACK (SCREENSHOT ONLY) -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 2</span> Fullstack Investor Market Model <span class="live-badge">✅ LIVE — Mar 19</span></div>
    <img src="''' + FULLSTACK_IMG + '''" class="screenshot-img" alt="Fullstack Investor Market Model — Full Page (Mar 19)">
    <div class="source-label">Source: <a href="https://fullstackinvestor.co/market-model" style="color:#58a6ff">fullstackinvestor.co/market-model</a> | Screenshot taken Mar 19, 2026</div>
  </div>

  <!-- STEP 3: SENTIMENT -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 3</span> 市場情緒 Market Sentiment</div>
    <div class="scorecard">
      <div class="score-item">
        <div class="score-label">VIX</div>
        <div class="score-value red">25.09</div>
        <div class="gray" style="font-size:11px">+12.16% today</div>
      </div>
      <div class="score-item">
        <div class="score-label">Fear &amp; Greed</div>
        <div class="score-value red">18</div>
        <div class="gray" style="font-size:11px">Extreme Fear</div>
      </div>
      <div class="score-item">
        <div class="score-label">T2108</div>
        <div class="score-value red">22%</div>
        <div class="gray" style="font-size:11px">✅ Live (Stockbee)</div>
      </div>
      <div class="score-item">
        <div class="score-label">SPY vs 52w High</div>
        <div class="score-value red">-8.5%</div>
        <div class="gray" style="font-size:11px">Off highs</div>
      </div>
    </div>
    <div class="note">📌 情緒總結: VIX 25.09 突破危險區 (>25)，Fear &amp; Greed 跌至 18 (極度恐懼)。T2108 從昨日 ~26% 進一步下跌至 22%，接近極度超賣區間 (<20%)。情緒面全面偏空，但極度超賣水平有時預示短期技術性反彈。</div>
  </div>

  <!-- STEP 4: TECHNICAL -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 4</span> 技術面 &amp; 市場廣度 Technical &amp; Breadth</div>

    <h3 class="sub">4A. Major Index vs Moving Averages (Mar 18 EOD — Yahoo Finance)</h3>
    <table>
      <tr><th>Index</th><th>Price</th><th>1D %</th><th>vs 20MA</th><th>vs 50MA</th><th>vs 200MA</th><th>Trend</th></tr>
'''

for name, price, chg, vs20, vs50, vs200, trend, tcls in INDICES:
    chg_cls = "green" if chg >= 0 else "red"
    chg_sign = "+" if chg >= 0 else ""
    vs20_cls = "green" if vs20 >= 0 else "red"
    vs50_cls = "green" if vs50 >= 0 else "red"
    vs200_cls = "green" if vs200 >= 0 else "red"
    vs20_sign = "+" if vs20 >= 0 else ""
    vs50_sign = "+" if vs50 >= 0 else ""
    vs200_sign = "+" if vs200 >= 0 else ""
    price_fmt = f"${price:,.2f}" if price > 1000 else f"${price:.2f}"
    html += f'''      <tr><td>{name}</td><td>{price_fmt}</td><td class="{chg_cls}">{chg_sign}{chg:.2f}%</td><td class="{vs20_cls}">{vs20_sign}{vs20:.2f}%</td><td class="{vs50_cls}">{vs50_sign}{vs50:.2f}%</td><td class="{vs200_cls}">{vs200_sign}{vs200:.2f}%</td><td><span class="badge {tcls}">{trend}</span></td></tr>\n'''

html += '''    </table>
    <div class="source-label">Source: <a href="https://finance.yahoo.com" style="color:#58a6ff">Yahoo Finance</a> | Data as of Mar 18, 2026 close</div>
    <div class="note">📌 注意: Dow Jones (^DJI) 已跌破 200MA (-0.65%)，係今日新增的技術面惡化信號。SPY 仍在 200MA 之上 (+0.57%)，但距離支撐位收窄。</div>

    <h3 class="sub">4B. Sector ETF Performance — Sorted by RSI 14 (SPY Ranked Inline) <span class="live-badge">✅ LIVE</span></h3>
    <p style="color:#8b949e; font-size:12px; margin-bottom:8px">
      Source: <a href="https://finance.yahoo.com" style="color:#58a6ff">Yahoo Finance</a> (Mar 18 EOD close) | Sorted by RSI 14 descending | SPY ★ ranked inline as benchmark
    </p>
    <table>
      <tr>
        <th>ETF</th><th>Sector</th><th>Price</th><th>1D %</th>
        <th>vs 20MA</th><th>vs 50MA</th><th>vs 200MA</th><th>RSI 14</th><th>Signal</th>
      </tr>
'''

sector_rows = build_sector_rows_with_spy()
for row in sector_rows:
    etf, sector, price, chg, vs20, vs50, vs200, rsi, sig_text, sig_cls = row
    is_spy = etf == "SPY ★"
    row_style = ' class="spy-row"' if is_spy else ''
    chg_cls = "green" if chg >= 0 else "red"
    chg_sign = "+" if chg >= 0 else ""
    vs20_cls = "green" if vs20 >= 0 else "red"
    vs50_cls = "green" if vs50 >= 0 else "red"
    vs200_cls = "green" if vs200 >= 0 else "red"
    vs20_sign = "+" if vs20 >= 0 else ""
    vs50_sign = "+" if vs50 >= 0 else ""
    vs200_sign = "+" if vs200 >= 0 else ""
    price_fmt = f"${price:,.2f}" if price > 1000 else f"${price:.2f}"
    rsi_fmt = f"{rsi:.1f}" if rsi else "—"
    rsi_cls = "green" if rsi and rsi >= 50 else ("red" if rsi and rsi < 30 else "yellow")
    if is_spy:
        html += f'''      <tr{row_style}><td><strong>{etf}</strong></td><td><strong>{sector}</strong></td><td><strong>{price_fmt}</strong></td><td class="{chg_cls}"><strong>{chg_sign}{chg:.2f}%</strong></td><td class="{vs20_cls}">{vs20_sign}{vs20:.2f}%</td><td class="{vs50_cls}">{vs50_sign}{vs50:.2f}%</td><td class="{vs200_cls}">{vs200_sign}{vs200:.2f}%</td><td class="{rsi_cls}"><strong>{rsi_fmt}</strong></td><td><span class="badge {sig_cls}">{sig_text}</span></td></tr>\n'''
    else:
        html += f'''      <tr><td>{etf}</td><td>{sector}</td><td>{price_fmt}</td><td class="{chg_cls}">{chg_sign}{chg:.2f}%</td><td class="{vs20_cls}">{vs20_sign}{vs20:.2f}%</td><td class="{vs50_cls}">{vs50_sign}{vs50:.2f}%</td><td class="{vs200_cls}">{vs200_sign}{vs200:.2f}%</td><td class="{rsi_cls}">{rsi_fmt}</td><td><span class="badge {sig_cls}">{sig_text}</span></td></tr>\n'''

html += '''    </table>
    <div class="note">📌 板塊 ETF 總結 (RSI 排序): XLE (Energy) RSI 74.2 唯一強勢板塊，且在所有移動平均線之上。XLB (Materials) RSI 13.8 最超賣。SPY RSI 27.6 排在 XLI (28.1) 之後、XLV (26.2) 之前。所有板塊 RSI 均低於 50，顯示整體市場偏弱。</div>

    <h3 class="sub">4C. % of Stocks Above Moving Averages <span class="live-badge">✅ LIVE — StockCharts</span></h3>
    <table>
      <tr><th>Index</th><th>Ticker</th><th>MA</th><th>Value (Mar 18)</th><th>Signal</th><th>Source</th></tr>
      <tr><td rowspan="3"><strong>S&amp;P 500</strong></td><td>$SPXA20R</td><td>20MA</td><td class="red">19.20%</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td><td>StockCharts</td></tr>
      <tr><td>$SPXA50R</td><td>50MA</td><td class="red">29.80%</td><td><span class="badge badge-bear">BEARISH</span></td><td>StockCharts</td></tr>
      <tr><td>$SPXA200R</td><td>200MA</td><td class="yellow">48.60%</td><td><span class="badge badge-warn">WARNING</span></td><td>StockCharts</td></tr>
    </table>
    <div class="source-label">Source: <a href="https://stockcharts.com" style="color:#58a6ff">StockCharts.com</a> | Data as of Mar 18, 2026 close</div>
    <div class="three-col">
      <div class="chart-card">
        <div class="chart-card-title">S&amp;P 500 — % Above 20MA ($SPXA20R) = 19.20%</div>
        <img src="''' + SPXA20R_IMG + '''" alt="$SPXA20R Chart">
        <div class="source-label">StockCharts.com</div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">S&amp;P 500 — % Above 50MA ($SPXA50R) = 29.80%</div>
        <img src="''' + SPXA50R_IMG + '''" alt="$SPXA50R Chart">
        <div class="source-label">StockCharts.com</div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">S&amp;P 500 — % Above 200MA ($SPXA200R) = 48.60%</div>
        <img src="''' + SPXA200R_IMG + '''" alt="$SPXA200R Chart">
        <div class="source-label">StockCharts.com</div>
      </div>
    </div>
    <div class="note">📌 廣度總結: S&P 500 中只有 19.20% 的股票在 20MA 之上 — 極度超賣水平。29.80% 在 50MA 之上，48.60% 在 200MA 之上。當 $SPXA20R 跌至 20% 以下，通常預示短期技術性反彈，但唔係買入信號。</div>
  </div>

  <!-- STEP 5: SECTOR & INDUSTRY -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 5</span> 板塊 &amp; 行業強度 Sector &amp; Industry Strength</div>

    <h3 class="sub">5A. Sector Performance (Finviz — Mar 18 EOD) <span class="live-badge">✅ LIVE</span></h3>
    <table>
      <tr><th>Sector</th><th>1D</th><th>1W</th><th>1M</th><th>YTD</th><th>Trend</th></tr>
      <tr><td><strong>Energy</strong></td><td class="red">-0.14%</td><td class="green">+3.07%</td><td class="green">+10.71%</td><td class="green">+30.07%</td><td><span class="badge badge-bull">LEADING</span></td></tr>
      <tr><td>Utilities</td><td class="red">-0.85%</td><td class="green">+0.88%</td><td class="red">-0.59%</td><td class="green">+8.72%</td><td><span class="badge badge-bull">DEFENSIVE</span></td></tr>
      <tr><td>Industrials</td><td class="red">-0.79%</td><td class="red">-2.05%</td><td class="red">-5.59%</td><td class="green">+7.69%</td><td><span class="badge badge-neutral">MIXED</span></td></tr>
      <tr><td>Technology</td><td class="red">-1.13%</td><td class="red">-1.63%</td><td class="red">-1.31%</td><td class="red">-3.85%</td><td><span class="badge badge-warn">WEAK YTD</span></td></tr>
      <tr><td>Communication Services</td><td class="red">-1.48%</td><td class="red">-1.23%</td><td class="green">+1.21%</td><td class="red">-3.08%</td><td><span class="badge badge-neutral">MIXED</span></td></tr>
      <tr><td>Real Estate</td><td class="red">-1.64%</td><td class="red">-0.52%</td><td class="red">-3.66%</td><td class="green">+3.82%</td><td><span class="badge badge-neutral">MIXED</span></td></tr>
      <tr><td>Financial</td><td class="red">-1.19%</td><td class="red">-1.27%</td><td class="red">-6.96%</td><td class="red">-8.50%</td><td><span class="badge badge-bear">WEAK</span></td></tr>
      <tr><td>Health Care</td><td class="red">-1.67%</td><td class="red">-3.28%</td><td class="red">-6.84%</td><td class="red">-4.61%</td><td><span class="badge badge-bear">LAGGING</span></td></tr>
      <tr><td>Consumer Cyclical</td><td class="red">-2.31%</td><td class="red">-1.78%</td><td class="red">-4.34%</td><td class="red">-7.62%</td><td><span class="badge badge-bear">WEAK</span></td></tr>
      <tr><td>Consumer Defensive</td><td class="red">-2.43%</td><td class="red">-1.47%</td><td class="red">-5.77%</td><td class="green">+6.98%</td><td><span class="badge badge-neutral">MIXED</span></td></tr>
      <tr><td>Basic Materials</td><td class="red">-2.10%</td><td class="red">-5.58%</td><td class="red">-7.55%</td><td class="green">+8.80%</td><td><span class="badge badge-bear">WEAK</span></td></tr>
    </table>
    <div class="source-label">Source: <a href="https://finviz.com/groups.ashx?g=sector&o=-change" style="color:#58a6ff">Finviz.com/groups</a> | Data as of Mar 18, 2026</div>

    <h3 class="sub">5B. Industry Leaders &amp; Laggards (Finviz — Mar 18) <span class="live-badge">✅ LIVE</span></h3>
    <div class="two-col">
      <div>
        <p style="color:#3fb950; font-size:12px; font-weight:bold; margin-bottom:6px">▲ Top Industries (1D%)</p>
        <table>
          <tr><th>Industry</th><th>1D</th></tr>
          <tr><td>Utilities - Independent Power Producers</td><td class="green">+2.70%</td></tr>
          <tr><td>Thermal Coal</td><td class="green">+1.47%</td></tr>
          <tr><td>Coking Coal</td><td class="green">+1.32%</td></tr>
          <tr><td>Marine Shipping</td><td class="green">+1.13%</td></tr>
          <tr><td>Oil &amp; Gas Refining &amp; Marketing</td><td class="green">+1.11%</td></tr>
        </table>
      </div>
      <div>
        <p style="color:#f85149; font-size:12px; font-weight:bold; margin-bottom:6px">▼ Bottom Industries (1D%)</p>
        <table>
          <tr><th>Industry</th><th>1D</th></tr>
          <tr><td>Copper</td><td class="red">-5.41%</td></tr>
          <tr><td>Gold</td><td class="red">-5.97%</td></tr>
          <tr><td>Other Precious Metals &amp; Mining</td><td class="red">-6.16%</td></tr>
          <tr><td>Silver</td><td class="red">-6.95%</td></tr>
          <tr><td>Auto &amp; Truck Dealerships</td><td class="red">-3.91%</td></tr>
        </table>
      </div>
    </div>
    <div class="source-label">Source: <a href="https://finviz.com/groups.ashx?g=industry&o=-change&v=140" style="color:#58a6ff">Finviz.com/groups (Industry)</a> | Data as of Mar 18, 2026</div>
    <div class="note">📌 行業總結: 能源相關行業 (Thermal Coal, Coking Coal, Oil &amp; Gas) 繼續領漲。貴金屬 (Silver -6.95%, Gold -5.97%, Copper -5.41%) 全面崩跌，顯示風險資產拋售擴大至商品市場。</div>
  </div>

  <!-- STEP 6: BREADTH -->
  <div class="section">
    <div class="section-title"><span class="step-badge">STEP 6</span> 市場廣度 Market Breadth</div>

    <h3 class="sub">6A. Advance / Decline Ratio <span class="live-badge">✅ LIVE — MarketInOut</span></h3>
    <table>
      <tr><th>Index</th><th>A/D Ratio (Mar 18)</th><th>MA(10)</th><th>Signal</th></tr>
      <tr><td>S&amp;P 500</td><td class="red">0.1919</td><td class="gray">0.9259</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td></tr>
      <tr><td>Dow Jones</td><td class="red">0.0714</td><td class="gray">1.08</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td></tr>
      <tr><td>NYSE Composite</td><td class="red">0.2253</td><td class="gray">0.8319</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td></tr>
      <tr><td>Nasdaq Composite</td><td class="red">0.2726</td><td class="gray">0.7879</td><td><span class="badge badge-bear">EXTREME BEARISH</span></td></tr>
    </table>
    <img src="''' + MARKETINOUT_IMG + '''" class="screenshot-img" alt="MarketInOut A/D Ratio — All Indices (Mar 18)">
    <div class="source-label">Source: <a href="https://www.marketinout.com/chart/market.php?breadth=advance-decline-ratio" style="color:#58a6ff">MarketInOut.com</a> | Screenshot taken Mar 19, 2026</div>

    <h3 class="sub">6B. Stockbee Market Monitor (T2108 &amp; 4% Movers) <span class="live-badge">✅ LIVE</span></h3>
    <table>
      <tr><th>Metric</th><th>Value (Mar 18)</th><th>Signal</th></tr>
      <tr><td>Stocks up 4%+ today</td><td class="yellow">109</td><td><span class="badge badge-warn">LOW</span></td></tr>
      <tr><td>Stocks down 4%+ today</td><td class="red">476</td><td><span class="badge badge-bear">HIGH — BROAD SELLING</span></td></tr>
      <tr><td>5-day ratio</td><td class="red">0.57</td><td><span class="badge badge-bear">BEARISH (&lt;1.0)</span></td></tr>
      <tr><td>10-day ratio</td><td class="red">0.73</td><td><span class="badge badge-bear">BEARISH (&lt;1.0)</span></td></tr>
      <tr><td><strong>T2108 (% above 40MA)</strong></td><td class="red"><strong>22%</strong></td><td><span class="badge badge-bear">OVERSOLD ZONE</span></td></tr>
    </table>
    <div style="margin-top:12px">
      <div style="color:#8b949e; font-size:12px; margin-bottom:4px">T2108 Gauge: 22% (Oversold &lt;40% | Extreme Oversold &lt;20%) — ✅ Live Mar 18 data from Stockbee</div>
      <div class="t2108-bar">
        <div class="t2108-fill" style="width:22%"></div>
        <div class="t2108-label">22%</div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:10px; color:#555; margin-top:2px">
        <span>0%</span><span>20% (Extreme OS)</span><span>40% (OS)</span><span>60% (Neutral)</span><span>80% (OB)</span><span>100%</span>
      </div>
    </div>
    <img src="''' + STOCKBEE_IMG + '''" class="screenshot-img" alt="Stockbee Market Monitor — T2108 and 4% Movers (Mar 18)">
    <div class="source-label">Source: <a href="https://stockbee.blogspot.com/p/mm.html" style="color:#58a6ff">stockbee.blogspot.com/p/mm.html</a> | Screenshot taken Mar 19, 2026</div>
    <div class="note">📌 廣度總結: T2108 22% 屬超賣區間，接近極度超賣 (&lt;20%)。今日下跌 4%+ 的股票有 476 隻，遠多於上漲 4%+ 的 109 隻 (比率 0.23)。5日及10日比率均低於 0.8，廣度結構嚴重偏弱，顯示廣泛性拋售。</div>
  </div>

  <!-- REGIME -->
  <div class="section">
    <div class="section-title">🎯 市場環境判定 Regime Determination</div>
    <div class="regime-box">
      <div class="regime-title">⚠ REGIME: BEARISH (Level 8–9 of 9)</div>
      <table>
        <tr><th>Factor</th><th>Reading</th><th>Source</th><th>Status</th></tr>
        <tr><td>VIX</td><td><span class="badge badge-bear">25.09 (DANGER ZONE &gt;25)</span></td><td>Yahoo Finance</td><td>✅ Live</td></tr>
        <tr><td>SPX vs Key MAs</td><td><span class="badge badge-warn">Below 20MA &amp; 50MA</span></td><td>Yahoo Finance</td><td>✅ Live</td></tr>
        <tr><td>DJI vs 200MA</td><td><span class="badge badge-bear">BREACHED — Below 200MA</span></td><td>Yahoo Finance</td><td>✅ Live</td></tr>
        <tr><td>Fear &amp; Greed</td><td><span class="badge badge-bear">18 — Extreme Fear</span></td><td>feargreedmeter.com</td><td>✅ Live</td></tr>
        <tr><td>Sector Leadership</td><td><span class="badge badge-warn">Energy only (RSI 74.2)</span></td><td>Yahoo Finance / Finviz</td><td>✅ Live</td></tr>
        <tr><td>Fullstack Exposure</td><td><span class="badge badge-bull">BULLISH (see screenshot)</span></td><td>fullstackinvestor.co</td><td>✅ Live</td></tr>
        <tr><td>T2108</td><td><span class="badge badge-bear">22% (Oversold)</span></td><td>stockbee.blogspot.com</td><td>✅ Live</td></tr>
        <tr><td>$SPXA20R</td><td><span class="badge badge-bear">19.20% (Extreme Bearish)</span></td><td>StockCharts.com</td><td>✅ Live</td></tr>
        <tr><td>A/D Ratio (S&amp;P 500)</td><td><span class="badge badge-bear">0.1919 (Extreme Bearish)</span></td><td>MarketInOut.com</td><td>✅ Live</td></tr>
      </table>
    </div>
    <div class="note" style="margin-top:12px">
      📌 <strong>交易建議 Trading Guidance:</strong> 市場環境為全面偏空型 (Bearish Level 8–9)。VIX 突破 25，T2108 跌至 22%，$SPXA20R 跌至 19.20%，A/D ratio 極度偏空。建議：(1) 不開任何新多倉；(2) 能源板塊 (XLE, RSI 74.2) 是唯一結構性強勢板塊；(3) 等待 VIX 回落至 20 以下、T2108 突破 40% 及 $SPXA20R 回升至 30% 以上才考慮加倉；(4) 注意 Fullstack Exposure 顯示 Bullish — 與其他指標有分歧，需要觀察是否持續。
    </div>
  </div>

  <!-- ECONOMIC CALENDAR -->
  <div class="section">
    <div class="section-title">📅 經濟日曆 Economic Calendar (Mar 19–21, 2026 — US Focus)</div>
    <table>
      <tr><th>Date</th><th>Time (ET)</th><th>Event</th><th>Previous</th><th>Consensus</th><th>Impact</th></tr>
      <tr>
        <td rowspan="4"><strong>Thu Mar 19</strong><br><span style="color:#3fb950;font-size:11px">TODAY</span></td>
        <td>08:30 AM</td><td><strong>Initial Jobless Claims (MAR 14)</strong></td><td>213K</td><td>215K</td><td><span class="cal-high">●</span> High</td>
      </tr>
      <tr><td>08:30 AM</td><td>Philly Fed Manufacturing Index (MAR)</td><td>16.3</td><td>15</td><td><span class="cal-med">●</span> Med</td></tr>
      <tr><td>08:30 AM</td><td>Philly Fed Prices Paid (MAR)</td><td>38.9</td><td>—</td><td><span class="cal-med">●</span> Med</td></tr>
      <tr><td>10:30 AM</td><td>EIA Natural Gas Inventory (MAR 13)</td><td>1,848B</td><td>—</td><td><span class="cal-low">●</span> Low</td></tr>
      <tr>
        <td><strong>Fri Mar 20</strong></td>
        <td>01:00 PM</td><td>Baker Hughes Rig Count (MAR 20)</td><td>553</td><td>—</td><td><span class="cal-low">●</span> Low</td>
      </tr>
      <tr>
        <td rowspan="3"><strong>Mon Mar 23</strong></td>
        <td>10:00 AM</td><td>Construction Spending - Total (JAN)</td><td>+0.3%</td><td>—</td><td><span class="cal-low">●</span> Low</td>
      </tr>
      <tr><td>10:00 AM</td><td>Construction Spending - Residential (JAN)</td><td>+1.5%</td><td>—</td><td><span class="cal-low">●</span> Low</td></tr>
      <tr><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
      <tr>
        <td rowspan="3"><strong>Tue Mar 24</strong></td>
        <td>08:30 AM</td><td><strong>Retail Sales MoM (JAN)</strong></td><td>0.0%</td><td>—</td><td><span class="cal-high">●</span> High</td>
      </tr>
      <tr><td>09:45 AM</td><td>PMI Manufacturing Flash (MAR)</td><td>51.6</td><td>—</td><td><span class="cal-med">●</span> Med</td></tr>
      <tr><td>09:45 AM</td><td>PMI Services Flash (MAR)</td><td>51.7%</td><td>—</td><td><span class="cal-med">●</span> Med</td></tr>
    </table>
    <div class="source-label">Source: <a href="https://forex.tradingcharts.com/economic_calendar/2026-03-19.html?code=USD" style="color:#58a6ff">forex.tradingcharts.com</a></div>
    <div class="flag">⚠ 今日重點 (Mar 19): Initial Jobless Claims (8:30 AM ET) + Philly Fed (8:30 AM ET)。鑑於昨日市場大跌，市場對今日 Philly Fed Prices Paid 特別敏感。若繼續偏高，滯脹憂慮將加劇。</div>
  </div>

  <!-- WATCHLIST FOLLOW-UP -->
  <div class="section">
    <div class="section-title">📋 前日觀察名單追蹤 Watchlist Follow-Up</div>
    <div class="watchlist-placeholder">
      📭 No watchlist entries from previous session.<br>
      <span style="font-size:12px">Once you start using ticker proposals, yesterday's watchlist performance will appear here.</span>
    </div>
  </div>

  <div style="text-align:center; color:#444; font-size:12px; padding: 20px 0;">
    Data Sources: <a href="https://finance.yahoo.com" style="color:#555">Yahoo Finance</a> · 
    <a href="https://feargreedmeter.com" style="color:#555">feargreedmeter.com</a> · 
    <a href="https://finviz.com" style="color:#555">Finviz.com</a> · 
    <a href="https://stockcharts.com" style="color:#555">StockCharts.com</a> · 
    <a href="https://www.marketinout.com" style="color:#555">MarketInOut.com</a> · 
    <a href="https://stockbee.blogspot.com/p/mm.html" style="color:#555">Stockbee.blogspot.com</a> · 
    <a href="https://fullstackinvestor.co/market-model" style="color:#555">FullstackInvestor.co</a> · 
    <a href="https://forex.tradingcharts.com" style="color:#555">forex.tradingcharts.com</a><br>
    Generated: March 19, 2026 ~8:30 AM HKT | For educational purposes only — not financial advice
  </div>

</div>
</body>
</html>'''

with open('/home/ubuntu/eod_data/mar19_report_v3.html', 'w') as f:
    f.write(html)

print(f"Generated: {len(html):,} chars, {len(html.encode()):,} bytes")
print("Saved to: /home/ubuntu/eod_data/mar19_report_v3.html")
