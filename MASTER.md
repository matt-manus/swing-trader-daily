# Swing Trader Daily — Master Reference

**Last updated: 2026-03-25**

This file is the single source of truth for this project. Any AI agent starting a new task MUST read this file first before making any changes.

---

## Project Overview

A daily market report that runs automatically via GitHub Actions every day at **HKT 06:30** (UTC 22:30 previous day). The report is generated as an HTML file and pushed to GitHub Pages.

- **Repo:** https://github.com/matt-manus/swing-trader-daily
- **Live report:** https://matt-manus.github.io/swing-trader-daily/
- **Report format:** `YYYY-MM-DD.html` (e.g. `2026-03-25.html`)
- **Template:** `TEMPLATE.html` in repo root
- **Script:** `daily_report.py` in repo root
- **Workflow:** `.github/workflows/daily-report.yml`

---

## GitHub Actions Setup

- **Schedule:** `cron: '30 22 * * *'` (= HKT 06:30 daily)
- **Manual trigger:** `workflow_dispatch` supported
- **Secret required:** `OPENAI_API_KEY` (set in repo Settings → Secrets)
  - Note: OpenAI is used for Step 7 commentary only. If key is missing/invalid, the rest of the report still generates correctly.
- **PAT for pushing:** Stored in sandbox at `/home/ubuntu/.config/gh/hosts.yml`. Has `repo` + `workflow` scope. (Token not stored here for security reasons)
- **Concurrency:** `group: daily-report` with `cancel-in-progress: true` to prevent parallel run conflicts

---

## Data Sources — DO NOT CHANGE THESE URLs

| Step | Name | URL | Method |
|------|------|-----|--------|
| Step 1 | Yahoo Finance (macro data) | yfinance library | API |
| Step 2 | Fullstack Investor Market Model | `https://fullstackinvestor.co/market-model` | Playwright screenshot |
| Step 3 | Fear & Greed Index | `https://production.dataviz.cnn.io/index/fearandgreed/graphdata` | requests JSON |
| Step 3 | NAAIM Exposure Index | `https://naaim.org/wp-content/uploads/{year}/03/NAAIM-Exposure-Index.xlsx` | requests download |
| Step 4C | StockCharts breadth (9 charts) | `https://stockcharts.com/h-sc/ui?s={symbol}&p=D&yr=1&mn=0&dy=0` | Playwright screenshot |
| Step 4B | Sector ETF RSI | yfinance library | API |
| Step 5B | Finviz Industry | `https://finviz.com/groups.ashx?g=industry&o=-change&v=110` | requests + BeautifulSoup |
| Step 6A | MarketInOut A/D Ratio | `https://www.marketinout.com/chart/market.php?breadth=advance-decline-ratio` | Playwright screenshot |
| Step 6B | Stockbee T2108 (CSV) | `https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=csv` | requests CSV |
| Step 6B | Stockbee T2108 (screenshot) | `https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=html&widget=true` | Playwright screenshot |
| Step 7 | OpenAI commentary | OpenAI API (`gpt-4.1-mini`) | API |

---

## StockCharts Symbols (Step 4C)

9 charts, all using URL pattern `https://stockcharts.com/h-sc/ui?s={symbol}&p=D&yr=1&mn=0&dy=0`:

| Name | Symbol |
|------|--------|
| SPXA20R | $SPXA20R |
| SPXA50R | $SPXA50R |
| SPXA200R | $SPXA200R |
| NDXA20R | $NDXA20R |
| NDXA50R | $NDXA50R |
| NDXA200R | $NDXA200R |
| NYA20R | $NYA20R |
| NYA50R | $NYA50R |
| NYA200R | $NYA200R |

Screenshot viewport: **1600px wide × 700px tall**

---

## Sector ETFs (Step 4B)

XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLB, XLU, XLRE, XLC, SPY (reference)

---

## Macro Tickers (Step 1)

SPY, QQQ, IWM, DIA, VIX (^VIX), GLD, USO, TLT, TNX (^TNX), DXY (DX-Y.NYB)

---

## Screenshot Viewport Sizes

| Screenshot | Width | Height |
|-----------|-------|--------|
| Fullstack Investor | 1400px | 900px (2 pages combined) |
| StockCharts (each) | 1600px | 700px |
| MarketInOut | 1400px | 800px |
| Stockbee T2108 sheet | 1800px | 600px |

---

## Current Status (as of 2026-03-25)

| Step | Status | Notes |
|------|--------|-------|
| Step 1 Macro data | ✅ Working | All tickers from Yahoo Finance |
| Step 1B News | ✅ Disabled | Removed — not needed |
| Step 2 Fullstack Investor | ✅ Working | Uses `.co` not `.com` |
| Step 3 Fear & Greed | ✅ Working | |
| Step 3 NAAIM | ⚠️ Intermittent | NAAIM updates weekly on Wednesdays; file format sometimes changes |
| Step 4C StockCharts | ✅ Working | 9 screenshots, values show N/A (by design — read from screenshot) |
| Step 4B Sector ETF RSI | ✅ Working | |
| Step 5A Finviz Sector | ✅ Removed | Not needed |
| Step 5B Finviz Industry | ✅ Working | Uses requests+BS4, not Playwright |
| Step 6A MarketInOut | ✅ Working | Fixed URL: `/chart/market.php?breadth=advance-decline-ratio` |
| Step 6B Stockbee T2108 | ✅ Working | CSV data + screenshot |
| Step 7 OpenAI commentary | ⚠️ Needs key | Skipped if no OPENAI_API_KEY |
| GitHub Actions schedule | ✅ Working | HKT 06:30 daily |
| GitHub Pages | ✅ Working | Auto-updates after push |

---

## Known Issues

1. **Step 4C values show N/A** — This is intentional. The numbers are visible in the screenshots. StockCharts does not provide a free API for these values.

2. **NAAIM intermittent failure** — NAAIM updates their Excel file every Wednesday. The URL includes the year and month, which may need updating. Current pattern: `https://naaim.org/wp-content/uploads/{year}/03/NAAIM-Exposure-Index.xlsx`

3. **OpenAI commentary missing** — Step 7 requires `OPENAI_API_KEY` secret. Without it, the bull/bear commentary section is empty. The rest of the report is unaffected.

4. **Finviz Sector screenshot removed** — Finviz has anti-scraping that causes Playwright timeouts. Replaced with requests-based Industry table (Step 5B).

---

## Rules for Future Changes

1. **NEVER change a URL unless the user explicitly provides the new URL.**
2. **Test locally before pushing.** Run `python3 daily_report.py 2026-03-25` and verify output.
3. **Change one thing at a time.** Fix one issue, verify it works, then move to the next.
4. **Do not add new features without user request.**
5. **Do not remove existing sections without user request.**
6. **Update this MASTER.md whenever a change is made.**

---

## File Structure

```
swing-trader-daily/
├── daily_report.py          # Main script — generates HTML report
├── TEMPLATE.html            # HTML template with {{PLACEHOLDER}} variables
├── MASTER.md                # This file — single source of truth
├── MARKET_HISTORY.md        # Auto-updated daily with regime/SPY/VIX data
├── index.html               # GitHub Pages index (links to daily reports)
├── images/
│   └── YYYY-MM-DD/          # Screenshots for each day
│       ├── fullstack.png
│       ├── SPXA20R.png
│       ├── SPXA50R.png
│       ├── SPXA200R.png
│       ├── NDXA20R.png
│       ├── NDXA50R.png
│       ├── NDXA200R.png
│       ├── NYA20R.png
│       ├── NYA50R.png
│       ├── NYA200R.png
│       ├── marketinout.png
│       └── t2108_sheet.png
└── .github/
    └── workflows/
        └── daily-report.yml
```

---

## How to Start a New Task

When starting a new task for this project:

1. Read this `MASTER.md` file first
2. Check the latest run status: https://github.com/matt-manus/swing-trader-daily/actions
3. View the latest report: https://matt-manus.github.io/swing-trader-daily/
4. Ask the user what specific change they want
5. Make only that change, nothing else
6. Test before pushing
7. Update this MASTER.md if anything changes
