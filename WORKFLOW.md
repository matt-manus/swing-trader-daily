# Daily EOD Market Summary — Master Workflow Reference

> **IMPORTANT FOR AI AGENT:** At the start of every new task, you MUST read ALL 4 core files in order before doing anything else.
> These files are located in BOTH the Manus project shared directory (`/home/ubuntu/projects/daily-market-summary-c59730ec/`) AND the GitHub repo (`swing-trader-daily` root):
>
> 1. `MASTER_INSTRUCTION.md` — Core principles and data sources
> 2. `WORKFLOW.md` — This file (daily workflow)
> 3. `Log.md` — Chronological session action log
> 4. `evolution.md` — Lessons learned and rule updates
>
> Do not rely on memory. Do not estimate. Do not change sources without user confirmation.
> Accuracy over speed — always.
>
> **End of session:** Update `Log.md` with actions taken. Update `evolution.md` with any new lessons learned.

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
1. Yahoo Finance (automated via yfinance) — includes BTC-USD
2. Fear & Greed Index (feargreedmeter.com)
3. **NAAIM Exposure Index** (naaim.org Excel download — automated)
4. Barchart.com — exact % above MA values ($S5TW/$S5FI/$S5TH, $NDTW/$NDFI/$NDTH, $MMTW/$MMFI/$MMTH)
5. StockCharts breadth screenshots (9 charts) + Step 6A AD Ratio from StockCharts Market Summary
6. Stockbee data + screenshot (Step 6B)
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
| Step 1 — Prices, MAs, RSI | Yahoo Finance | yfinance library | Automated — tickers: SPY, QQQ, IWM, DIA, VIX, GLD, USO, ^TNX, DX-Y.NYB, **BTC-USD** |
| Step 1 — BTC | **Yahoo Finance** | `BTC-USD` via yfinance | Include BTC close price and daily % change in Macro Environment section |
| Step 1 — USD Index | **DXY (not UUP)** | `DX-Y.NYB` via yfinance | Use DXY directly — UUP is an ETF with tracking error |
| Step 1 — Fear & Greed | feargreedmeter.com | https://feargreedmeter.com | Scrape/screenshot |
| Step 1 — Economic Calendar | forex.tradingcharts.com | https://forex.tradingcharts.com/economic_calendar/ | Manual check |
| **Step 3 — NAAIM Exposure Index** | **naaim.org** | `https://naaim.org/programs/naaim-exposure-index/` | **Download Excel file (linked as "HERE" on page), parse latest row, show value + date. Updated every Wednesday.** |
| Step 3 — T2108 value | Stockbee | https://stockbee.blogspot.com/p/mm.html | Read actual value — no login needed |
| Step 4A — Index vs MAs | Yahoo Finance | yfinance library | **SPY, QQQ, DIA, IWM only** — no SPX/NDX index. MA color: red if price < MA, green if price > MA. Signal badge must match actual position. |
| Step 4B — % Above MAs (exact values) | **Barchart.com** | S&P 500: `$S5TW` (20d), `$S5FI` (50d), `$S5TH` (200d); Nasdaq 100: `$NDTW` (20d), `$NDFI` (50d), `$NDTH` (200d); NYSE: `$MMTW` (20d), `$MMFI` (50d), `$MMTH` (200d) | Scrape exact % values from Barchart |
| Step 4B — % Above MAs (screenshots) | **StockCharts** | https://stockcharts.com/h-sc/ui?s=$SPXA20R | Screenshot only — use $SPXA20R, $SPXA50R, $SPXA200R, $NDXA20R, $NDXA50R, $NDXA200R, $NYA20R, $NYA50R, $NYA200R (9 charts, double size) |
| Step 4C — Sector ETF RSI | Yahoo Finance | yfinance library | **Sorted by RSI 14 descending** — must use **Wilder's SMMA** algorithm (not simple rolling mean). Use `pandas_ta` `ta.rsi()` or manual SMMA: `smma = (prev * 13 + val) / 14`. Simple rolling mean gives incorrect (lower) values vs Yahoo Finance/TradingView. |
| Step 5A — Sector Performance | Finviz | https://finviz.com/groups.ashx?g=sector&o=-change | Data + screenshot |
| Step 4D — Industry Performance | Finviz | https://finviz.com/groups.ashx?g=industry&o=-change | Data table — top 10 leaders with parent sector |
| **Step 6A — Advance/Decline Ratio** | **StockCharts Market Summary** | https://stockcharts.com/docs/doku.php?id=market_summary | Scrape Advancing/Declining counts for S&P 500, Nasdaq 100, DJIA, Russell 2000. Calculate AD Ratio = Advancing ÷ Declining (2 decimal places). Present as table. |
| Step 6B — Stockbee breadth | Stockbee | **https://stockbee.blogspot.com/p/mm.html** | Screenshot — must include T2108 column — no login needed — **must be taken AFTER 4:00 PM ET market close, not in the morning**. T2108 data is inside a Google Sheets iframe: (1) first try scrolling into the iframe on the Stockbee page; (2) if T2108 is not visible, extract the Google Sheets iframe source URL and screenshot that directly — T2108 column must never be missing from the screenshot. |

---

## User Requirements (Do Not Change Without Confirmation)

1. **Accuracy over speed** — If unsure, check. If don't remember, re-read the file. Never estimate.
2. **Intellectual Honesty** — Always distinguish between facts (directly verified via tools/code/screenshots) and inferences (guesses, assumptions, "sounds reasonable" logic). If uncertain about something — especially system behaviour, schedules, or technical causes — say "I don't know, I can't verify this" instead of filling the gap with a plausible-sounding explanation. If a previous answer was wrong, admit it directly: "I was wrong, I was guessing, not verifying." This rule applies to ALL conversations, not just report data.
5. **Step 3 NAAIM** — Download NAAIM Excel from naaim.org, parse latest row. Show value + date in Scorecard alongside VIX, Fear & Greed, T2108. Updated every Wednesday; on other days show most recent value with date label.
6. **Step 7 Market Commentary** — After all data is collected, write Bull vs Bear commentary using ONLY data from the current report. Must include: Bearish Case (4–6 points), Bullish Case (3–5 points), and Bull vs Bear Scorecard table with final score and trading guidance. Total length 600–900 Chinese characters.
7. **Step 4A** — No SPY daily chart
8. **Step 4B** — Exact values from **Barchart** tickers ($S5TW/$S5FI/$S5TH for S&P 500, $NDTW/$NDFI/$NDTH for Nasdaq 100, $MMTW/$MMFI/$MMTH for NYSE). Screenshots from StockCharts ($SPXA20R, $SPXA50R, $SPXA200R, $NDXA20R, $NDXA50R, $NDXA200R, $NYA20R, $NYA50R, $NYA200R). No TradingView. No estimates. Double the size of current screenshots.
9. **Step 4C** — Must include RSI 14 column. Must be sorted by RSI descending (not 1D%)
11. **Step 6B** — Stockbee screenshot must include T2108. No login needed. URL: stockbee.blogspot.com/p/mm.html. T2108 is inside a Google Sheets iframe — if not visible via page scroll, extract the iframe source URL and screenshot the Google Sheets directly.
12. **Step 7 UFO Watchlist** — REMOVED. Do not include.
13. **Report Comparison Notes** — REMOVED. Do not include.
14. **No estimated values** — No `~` approximations for any data values. All values must be exact and cited.
15. **All data must cite source** — Every section must have a source link/label.
16. **Show checklist before starting** — Before collecting any data, list all sections and sources for user confirmation.

---

## Report Sections (in order)

1. **Header** — Date, title, generated timestamp
2. **Verdict Box** — Overall market verdict (Bullish/Neutral/Defensive/Bearish + level)
4. **Step 1: Macro Environment** — Indices (SPY, QQQ, IWM, DIA), VIX, Gold (GLD), Oil (USO), 10Y Yield (^TNX), USD/DXY, **BTC**, Fear & Greed
6. **Step 3: Market Sentiment** — VIX scorecard, Fear & Greed, T2108, **NAAIM Exposure Index** scorecard, sentiment summary note
7. **Step 4: Technical Analysis**
   - 4A: Index vs Moving Averages (**SPY, QQQ, DIA, IWM only** — 4 tickers, no SPX/NDX index. MA color must reflect actual position: red = below MA, green = above MA)
   - 4B: % of Stocks Above MAs (StockCharts $SPXA20R, $SPXA50R, $SPXA200R screenshots, double size)
   - 4C: Sector ETF Rotation (all 11 sectors + SPY, with RSI 14, sorted by RSI)
   - 4D: Industry Leaders (Finviz — top 10 leaders with parent sector)
8. **Step 5: Sector & Industry Strength**
   - 5A: Sector Performance (Finviz heatmap screenshot + data table)
9. **Step 6: Market Breadth**
   - 6A: Advance/Decline Ratio — scrape Advancing/Declining counts from StockCharts Market Summary for S&P 500, Nasdaq 100, DJIA, Russell 2000. Calculate AD Ratio for each.
   - 6B: Stockbee Market Monitor (screenshot including T2108, up/down 4%+, 5d/10d ratios)
10. **Step 7: Daily Market Commentary (Bull vs Bear)** — Written after all data is collected. Three fixed parts:
   - 🐻 **Bearish Case**: 4–6 data-backed reasons to be cautious (cite exact values from Steps 1–6)
   - 🐂 **Bullish Case**: 3–5 data-backed reasons for potential upside (cite exact values)
   - ⚖️ **Bull vs Bear Scorecard table**: dimensions include Long-term Trend, Breadth, Sentiment, Institutional Positioning, Macro, Short-term Technical, Fundamentals — with a final score and one-line trading guidance
   - Language: Traditional Chinese main body, keep technical terms in English (RSI, VIX, MA, T2108)
   - Placed **after Step 6, before Regime Box**
11. **Regime Box** — Final market environment determination with action guidance
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
| Using stockbee.biz | Use stockbee.blogspot.com/p/mm.html |
| Saying Stockbee needs login | It does NOT need login |
| Using TradingView for Step 4B | Use Barchart for exact values ($S5TW/$S5FI/$S5TH, $NDTW/$NDFI/$NDTH, $MMTW/$MMFI/$MMTH) and StockCharts for screenshots ($SPXA20R etc.) |
| Skipping Step 6A AD Ratio | Always scrape Advancing/Declining from StockCharts Market Summary and calculate AD Ratio for S&P 500, Nasdaq 100, DJIA, Russell 2000 |
| Omitting BTC from Step 1 | Always include BTC-USD price and daily % change in Macro Environment |
| Estimating values with ~ | Always get exact values from source |
| Rewriting the builder from scratch | Always use previous day's HTML as template |
| Including Step 7 UFO | Step 7 is REMOVED |
| Including Report Comparison Notes | REMOVED |
| Sorting Step 4C by 1D% | Sort by RSI 14 descending |
| Using simple rolling mean for RSI | Use Wilder's SMMA: `smma = (prev * 13 + val) / 14` — simple mean gives wrong (lower) values |
| Using UUP for USD in Step 1 | Use DXY (`DX-Y.NYB`) — UUP is an ETF with tracking error |
| Step 4A showing wrong MA colors from template | Always recalculate: price < MA = red, price > MA = green. Never copy colors from previous day's template |
| Step 6B screenshot taken in morning | Must re-screenshot Stockbee AFTER 4:00 PM ET market close |
| Step 6B T2108 missing from screenshot | T2108 is in a Google Sheets iframe — if not visible via Stockbee page scroll, extract the Google Sheets iframe source URL and screenshot it directly |
| VIX/macro description copied from previous day | Always update all descriptive text to match today's actual data (e.g. VIX up vs down) |
| Omitting NAAIM from Step 3 Scorecard | Always include NAAIM value + date in Scorecard |
| Skipping Step 7 commentary | Always write Bull vs Bear commentary after all data is collected |
| Using estimates or opinions in Step 7 | Every point in commentary MUST cite exact data values from the report |
| Placing Step 7 after Regime Box | Step 7 goes BEFORE the Regime Box, not after |
