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
3. **NAAIM Exposure Index** (naaim.org Excel download — automated)
4. **Step 1B: Finviz ticker news scrape + AI filter** (automated)
   - Note: UUP replaced by DXY in ticker list
5. Fullstack Investor screenshot
6. StockCharts breadth screenshots
7. MarketInOut A/D ratio screenshot
8. Stockbee data + screenshot
9. Finviz sector and industry data

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
| Step 1 — USD Index | **DXY (not UUP)** | `DX-Y.NYB` via yfinance | Use DXY directly — UUP is an ETF with tracking error |
| Step 1 — Fear & Greed | feargreedmeter.com | https://feargreedmeter.com | Scrape/screenshot |
| Step 1 — Economic Calendar | forex.tradingcharts.com | https://forex.tradingcharts.com/economic_calendar/ | Manual check |
| **Step 1B — Market Intelligence News** | **Finviz (ticker pages) + OpenAI** | `https://finviz.com/quote.ashx?t=TICKER` | **Auto-scrape `#news-table` for SPY,QQQ,IWM,DIA,XLE,XLK,XLF,XLV,XLB,NVDA,AAPL,MSFT,META,AMZN,TSLA,GOOGL,GLD,TLT,USO,UUP — filter today’s headlines only — then use OpenAI to select 5–7 most market-moving stories with HIGH/MEDIUM/LOW impact rating** |
| **Step 3 — NAAIM Exposure Index** | **naaim.org** | `https://naaim.org/programs/naaim-exposure-index/` | **Download Excel file (linked as “HERE” on page), parse latest row, show value + date. Updated every Wednesday.** |
| Step 2 — Fullstack Investor | fullstackinvestor.co | **https://fullstackinvestor.co/market-model** | Screenshot ONLY — no data extraction, no interpretation |
| Step 3 — T2108 value | Stockbee | https://stockbee.blogspot.com/p/mm.html | Read actual value — no login needed |
| Step 4A — Index vs MAs | Yahoo Finance | yfinance library | **SPY, QQQ, DIA, IWM only** — no SPX/NDX index. MA color: red if price < MA, green if price > MA. Signal badge must match actual position. |
| Step 4B — Sector ETF RSI | Yahoo Finance | yfinance library | **Sorted by RSI 14 descending** — must use **Wilder's SMMA** algorithm (not simple rolling mean). Use `pandas_ta` `ta.rsi()` or manual SMMA: `smma = (prev * 13 + val) / 14`. Simple rolling mean gives incorrect (lower) values vs Yahoo Finance/TradingView. |
| Step 4C — % Above MAs | **StockCharts** | https://stockcharts.com/h-sc/ui?s=$SPXA20R | Screenshot — use $SPXA20R, $SPXA50R, $SPXA200R |
| Step 5A — Sector Performance | Finviz | https://finviz.com/groups.ashx?g=sector&o=-change | Data + screenshot |
| Step 5B — Industry Performance | Finviz | https://finviz.com/groups.ashx?g=industry&o=-change | Data table — top 5 and bottom 5 |
| Step 6A — A/D Ratio | MarketInOut | **https://www.marketinout.com/chart/market.php?breadth=advance-decline-ratio** | Screenshot — no login needed, shows all indices |
| Step 6B — Stockbee breadth | Stockbee | **https://stockbee.blogspot.com/p/mm.html** | Screenshot — must include T2108 column — no login needed — **must be taken AFTER 4:00 PM ET market close, not in the morning** |

---

## User Requirements (Do Not Change Without Confirmation)

1. **Accuracy over speed** — If unsure, check. If don't remember, re-read the file. Never estimate.
2. **Intellectual Honesty** — Always distinguish between facts (directly verified via tools/code/screenshots) and inferences (guesses, assumptions, "sounds reasonable" logic). If uncertain about something — especially system behaviour, schedules, or technical causes — say "I don't know, I can't verify this" instead of filling the gap with a plausible-sounding explanation. If a previous answer was wrong, admit it directly: "I was wrong, I was guessing, not verifying." This rule applies to ALL conversations, not just report data.
3. **Step 1B Market Intelligence** — Scrape Finviz `#news-table` for today's headlines across 20 tickers. Use OpenAI to filter 5–7 most market-moving stories. Each story must have: impact level (HIGH/MEDIUM/LOW), affected sectors/tickers, one-line explanation. Only include headlines dated the same day as the report.
4. **Step 2 Fullstack** — Screenshot ONLY. No data extraction. No interpretation. Full page (stitch top + bottom). URL: fullstackinvestor.co (NOT .com)
5. **Step 3 NAAIM** — Download NAAIM Excel from naaim.org, parse latest row. Show value + date in Scorecard alongside VIX, Fear & Greed, T2108. Updated every Wednesday; on other days show most recent value with date label.
6. **Step 7 Market Commentary** — After all data is collected, write Bull vs Bear commentary using ONLY data from the current report. Must include: Bearish Case (4–6 points), Bullish Case (3–5 points), and Bull vs Bear Scorecard table with final score and trading guidance. Total length 600–900 Chinese characters.
7. **Step 4A** — No SPY daily chart
8. **Step 4B** — Must include RSI 14 column. Must be sorted by RSI descending (not 1D%)
9. **Step 4C** — Use StockCharts screenshots ($SPXA20R, $SPXA50R, $SPXA200R). No TradingView. No estimates.
10. **Step 6A** — MarketInOut A/D ratio screenshot showing all indices. No login needed.
11. **Step 6B** — Stockbee screenshot must include T2108. No login needed. URL: stockbee.blogspot.com/p/mm.html
12. **Step 7 UFO Watchlist** — REMOVED. Do not include.
13. **Report Comparison Notes** — REMOVED. Do not include.
14. **No estimated values** — No `~` approximations for any data values. All values must be exact and cited.
15. **All data must cite source** — Every section must have a source link/label.
16. **Show checklist before starting** — Before collecting any data, list all sections and sources for user confirmation.

---

## Report Sections (in order)

1. **Header** — Date, title, generated timestamp
2. **Verdict Box** — Overall market verdict (Bullish/Neutral/Defensive/Bearish + level)
3. **Key Levels** — SPX 20/50/200MA (exact values from yfinance), VIX levels, T2108
4. **Step 1: Macro Environment** — Indices (SPY, QQQ, IWM, DIA), VIX, Gold (GLD), Oil (USO), 10Y Yield (^TNX), USD (UUP), Fear & Greed
4b. **Step 1B: Market Intelligence News** — 5–7 AI-filtered market-moving headlines from Finviz (today only), with HIGH/MEDIUM/LOW impact rating, affected tickers, and one-line explanation
5. **Step 2: Fullstack Investor** — Screenshot only, link to fullstackinvestor.co/market-model
6. **Step 3: Market Sentiment** — VIX scorecard, Fear & Greed, T2108, **NAAIM Exposure Index** scorecard, sentiment summary note
7. **Step 4: Technical Analysis**
   - 4A: Index vs Moving Averages (**SPY, QQQ, DIA, IWM only** — 4 tickers, no SPX/NDX index. MA color must reflect actual position: red = below MA, green = above MA)
   - 4B: Sector ETF Rotation (all 11 sectors + SPY, with RSI 14, sorted by RSI)
   - 4C: % of Stocks Above MAs (StockCharts $SPXA20R, $SPXA50R, $SPXA200R screenshots)
8. **Step 5: Sector & Industry Strength**
   - 5A: Sector Performance (Finviz heatmap screenshot + data table)
   - 5B: Industry Leaders & Laggards (Finviz — top 5 and bottom 5 by 1D%)
9. **Step 6: Market Breadth**
   - 6A: Advance/Decline Ratio (MarketInOut screenshot — all indices)
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
| Using simple rolling mean for RSI | Use Wilder's SMMA: `smma = (prev * 13 + val) / 14` — simple mean gives wrong (lower) values |
| Using UUP for USD in Step 1 | Use DXY (`DX-Y.NYB`) — UUP is an ETF with tracking error |
| Step 4A showing wrong MA colors from template | Always recalculate: price < MA = red, price > MA = green. Never copy colors from previous day's template |
| Step 6B screenshot taken in morning | Must re-screenshot Stockbee AFTER 4:00 PM ET market close |
| VIX/macro description copied from previous day | Always update all descriptive text to match today's actual data (e.g. VIX up vs down) |
| Skipping Step 1B news intelligence | Always scrape Finviz + AI filter for today’s headlines |
| Omitting NAAIM from Step 3 Scorecard | Always include NAAIM value + date in Scorecard |
| Including old/previous-day news in Step 1B | Only include headlines dated the same day as the report |
| Skipping Step 7 commentary | Always write Bull vs Bear commentary after all data is collected |
| Using estimates or opinions in Step 7 | Every point in commentary MUST cite exact data values from the report |
| Placing Step 7 after Regime Box | Step 7 goes BEFORE the Regime Box, not after |
