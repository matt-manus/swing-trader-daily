# Daily EOD Market Summary — Master Workflow Reference

> **IMPORTANT FOR AI AGENT:** Read this file at the start of every new task before doing anything else.
> Do not rely on memory. Do not estimate. Do not change sources without user confirmation.
> Accuracy over speed — always.

---

## Overview

This repo generates a daily EOD (End of Day) market summary report published to GitHub Pages at:
**https://matt-manus.github.io/swing-trader-daily/**

The report is built using `scripts/build_daily_report.py`, which takes the previous day's HTML as a template and updates only the data values. The structure and format must remain identical each day.

---

## When to Run

- Run after US market close (4:00 PM ET = ~4:00 AM HKT next day)
- Target publish time: **7:00 AM HKT**
- User will initiate the task by opening a conversation and saying "開始" or "make the report"

---

## Step-by-Step Workflow

### Before Starting
1. Read this file (`WORKFLOW.md`) completely
2. Read the most recent archive HTML (e.g. `2026-03-19.html`) to confirm current structure
3. List out all sections and sources as a checklist — show to user for confirmation before proceeding
4. Only then start collecting data

### Data Collection Order
1. Yahoo Finance (automated via yfinance)
2. Fear & Greed Index (feargreedmeter.com)
3. Fullstack Investor screenshot
4. StockCharts breadth screenshots
5. MarketInOut A/D ratio screenshot
6. Stockbee data + screenshot
7. Finviz sector and industry data

### Building the Report
1. Copy the most recent archive HTML as the base template
2. Update data values only — do NOT change structure, CSS, or layout
3. Verify all sections present before pushing
4. Push to GitHub Pages

---

## Data Sources — Complete Reference

| Section | Source | URL | Method |
|---------|--------|-----|--------|
| Step 1 — Prices, MAs, RSI | Yahoo Finance | yfinance library | Automated |
| Step 1 — Fear & Greed | feargreedmeter.com | https://feargreedmeter.com | Scrape/screenshot |
| Step 1 — Economic Calendar | forex.tradingcharts.com | https://forex.tradingcharts.com/economic_calendar/ | Manual check |
| Step 2 — Fullstack Investor | fullstackinvestor.co | **https://fullstackinvestor.co/market-model** | Screenshot ONLY — no data extraction, no interpretation |
| Step 3 — T2108 value | Stockbee | https://stockbee.blogspot.com/p/mm.html | Read actual value — no login needed |
| Step 4A — Index vs MAs | Yahoo Finance | yfinance library | Automated |
| Step 4B — Sector ETF RSI | Yahoo Finance | yfinance library | Automated — sorted by RSI 14, not 1D% |
| Step 4C — % Above MAs | **StockCharts** | https://stockcharts.com/h-sc/ui?s=$SPXA20R | Screenshot — use $SPXA20R, $SPXA50R, $SPXA200R |
| Step 5A — Sector Performance | Finviz | https://finviz.com/groups.ashx?g=sector&o=-change | Data + screenshot |
| Step 5B — Industry Performance | Finviz | https://finviz.com/groups.ashx?g=industry&o=-change | Data table — top 5 and bottom 5 |
| Step 6A — A/D Ratio | MarketInOut | **https://www.marketinout.com/chart/market.php?breadth=advance-decline-ratio** | Screenshot — no login needed, shows all indices |
| Step 6B — Stockbee breadth | Stockbee | **https://stockbee.blogspot.com/p/mm.html** | Screenshot — must include T2108 column — no login needed |

---

## User Requirements (Do Not Change Without Confirmation)

1. **Accuracy over speed** — If unsure, check. If don't remember, re-read the file. Never estimate.
2. **Step 2 Fullstack** — Screenshot ONLY. No data extraction. No interpretation. Full page (stitch top + bottom). URL: fullstackinvestor.co (NOT .com)
3. **Step 4A** — No SPY daily chart
4. **Step 4B** — Must include RSI 14 column. Must be sorted by RSI descending (not 1D%)
5. **Step 4C** — Use StockCharts screenshots ($SPXA20R, $SPXA50R, $SPXA200R). No TradingView. No estimates.
6. **Step 6A** — MarketInOut A/D ratio screenshot showing all indices. No login needed.
7. **Step 6B** — Stockbee screenshot must include T2108. No login needed. URL: stockbee.blogspot.com/p/mm.html
8. **Step 7 UFO Watchlist** — REMOVED. Do not include.
9. **Report Comparison Notes** — REMOVED. Do not include.
10. **No estimated values** — No `~` approximations for any data values. All values must be exact and cited.
11. **All data must cite source** — Every section must have a source link/label.
12. **Show checklist before starting** — Before collecting any data, list all sections and sources for user confirmation.

---

## Report Sections (in order)

1. **Header** — Date, title, generated timestamp
2. **Verdict Box** — Overall market verdict (Bullish/Neutral/Defensive/Bearish + level)
3. **Key Levels** — SPX 20/50/200MA (exact values from yfinance), VIX levels, T2108
4. **Step 1: Macro Environment** — Indices (SPY, QQQ, IWM, DIA), VIX, Gold (GLD), Oil (USO), 10Y Yield (^TNX), USD (UUP), Fear & Greed
5. **Step 2: Fullstack Investor** — Screenshot only, link to fullstackinvestor.co/market-model
6. **Step 3: Market Sentiment** — VIX scorecard, Fear & Greed, T2108 scorecard, sentiment summary note
7. **Step 4: Technical Analysis**
   - 4A: Index vs Moving Averages (SPY, QQQ, IWM, DIA vs 20/50/200MA)
   - 4B: Sector ETF Rotation (all 11 sectors + SPY, with RSI 14, sorted by RSI)
   - 4C: % of Stocks Above MAs (StockCharts $SPXA20R, $SPXA50R, $SPXA200R screenshots)
8. **Step 5: Sector & Industry Strength**
   - 5A: Sector Performance (Finviz heatmap screenshot + data table)
   - 5B: Industry Leaders & Laggards (Finviz — top 5 and bottom 5 by 1D%)
9. **Step 6: Market Breadth**
   - 6A: Advance/Decline Ratio (MarketInOut screenshot — all indices)
   - 6B: Stockbee Market Monitor (screenshot including T2108, up/down 4%+, 5d/10d ratios)
10. **Regime Box** — Final market environment determination with action guidance
11. **Economic Calendar** — Next 3 trading days key events
12. **Watchlist Follow-Up** — Previous day's watchlist stocks performance

---

## File Structure

```
swing-trader-daily/
├── index.html              # Current day's report (always latest)
├── 2026-03-18.html         # Mar 18 archive
├── 2026-03-19.html         # Mar 19 archive
├── WORKFLOW.md             # This file — master reference
└── scripts/
    ├── build_daily_report.py   # Main report builder
    ├── fetch_data.py           # Yahoo Finance data fetcher
    └── update_template.py      # Template updater
```

---

## CDN Image Upload

All screenshots are uploaded to Manus CDN using:
```bash
manus-upload-file /path/to/image.png
```
Returns a URL like: `https://static.manus.im/file/manuscdn.com/XXXXXXXX.png`

---

## GitHub Pages

- Repo: `matt-manus/swing-trader-daily`
- Branch: `main`
- Live URL: https://matt-manus.github.io/swing-trader-daily/
- Push command: `git add . && git commit -m "message" && git push origin main`

---

## Common Mistakes to Avoid

| Mistake | Correct Action |
|---------|---------------|
| Using fullstackinvestor.com | Use fullstackinvestor.co/market-model |
| Using stockbee.biz | Use stockbee.blogspot.com/p/mm.html |
| Saying Stockbee needs login | It does NOT need login |
| Saying MarketInOut A/D needs login | It does NOT need login |
| Using TradingView for Step 4C | Use StockCharts ($SPXA20R, $SPXA50R, $SPXA200R) |
| Estimating values with ~ | Always get exact values from source |
| Rewriting the builder from scratch | Always use previous day's HTML as template |
| Including Step 7 UFO | Step 7 is REMOVED |
| Including Report Comparison Notes | REMOVED |
| Sorting Step 4B by 1D% | Sort by RSI 14 descending |
