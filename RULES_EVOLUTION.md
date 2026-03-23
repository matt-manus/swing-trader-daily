# 🧠 Rules Evolution — Daily Market Summary AI Brain

This file tracks evolving preferences, market patterns, and logic improvements discovered through our daily market summary interactions. The AI agent must read this file before starting each new daily summary.

> **AI Agent Instruction:** Read this file at the start of every task. Update it after each daily summary with new patterns, preferences, or logic improvements discovered.

---

## 📋 Formatting & Content Preferences

### Report Title & Timestamps
- Title format: `Market Summary — [Day] [Month DD], [YYYY]`
- Always include report generation time in both HKT and ET
- Replace "EOD close" with exact time in HKT/ET

### Sector ETF Table
- Sort by RSI 14 (descending) — highest RSI first
- Include SPY as inline benchmark row (highlighted with BENCHMARK badge)
- Include vs 20MA, vs 50MA, vs 200MA columns
- Add MA signal badge: ABOVE ALL MAs / BELOW ALL MAs / BELOW 20/50MA / etc.

### Industry Leaders
- Include top 10 industries sorted by 1D change (no laggards)
- Include sector column for each industry
- Source: Finviz

### Breadth Charts (StockCharts)
- Always include 9 charts: SPX (20/50/200MA), NDX (20/50/200MA), NYSE (20/50/200MA)
- Display in 3-column grid layout
- Include actual % value in chart card title

### News Section (Step 1B)
- Use AI filtering to select 5–7 most market-relevant headlines
- Classify by impact: HIGH / MEDIUM / LOW
- Include tickers/sectors affected
- Include "why it matters" explanation

---

## 📊 Market Pattern Observations

### Mar 20, 2026 — SPY/NDX Broke Below 200MA
- When SPY breaks below 200MA with VIX >25, it signals a full bearish regime
- $SPXA20R <15% is an extreme oversold reading that historically precedes technical bounces
- Stock/bond correlation breakdown (TLT -1.90% on same day as SPY -1.70%) = stagflation signal
- NAAIM 60.24 at that time — institutions were still reducing exposure

### Mar 23, 2026 — Geopolitical Relief Rally
- Event-driven rallies (Iran/geopolitical) can be sharp but may not sustain
- $SPXA20R recovering from 12.60% → 40.00% in 3 days shows breadth can recover quickly
- IWM outperforming (+2.16% vs SPY +1.05%) on relief rally days is typical small-cap behavior
- USO -8.95% on Iran fear easing = energy stocks may face headwind despite XLE strength
- NAAIM 19.44 (near empty) = massive potential buying power if trend confirms
- Key confirmation needed: SPY close above 200MA ($656.85) + VIX below 20

---

## 🔑 Key Decision Rules (Evolved)

### Regime Classification
| Level | Conditions | Action |
|---|---|---|
| 9/9 Bearish | VIX >30, SPY below all MAs, $SPXA20R <10% | No new longs, consider shorts |
| 8/9 Bearish | VIX >25, SPY below all MAs, $SPXA20R <20% | No new longs |
| 6-7/9 Transition | VIX 20-26, SPY near 200MA, $SPXA20R 30-50% | Small positions in leaders only |
| 4-5/9 Neutral | VIX 15-20, SPY above 200MA, mixed breadth | Selective longs |
| 1-3/9 Bullish | VIX <15, SPY above all MAs, $SPXA20R >60% | Full exposure |

### Confirmation Signals for Regime Upgrade
1. SPY closes above 200MA for 2+ consecutive days
2. VIX closes below 20 for 2+ consecutive days
3. $SPXA50R rises above 30%
4. T2108 rises above 40%
5. Stockbee 5-day ratio rises above 1.0

### Sector Rotation Logic
- Energy (XLE) has been the structural leader since early 2026 (Iran war, oil supply)
- Basic Materials strength often leads broader market recovery
- Healthcare weakness (XLV RSI 26.3) = defensive sector under pressure = unusual
- When IWM outperforms SPY, it often signals risk appetite returning

---

## 🛠 Technical Workflow Improvements

### Screenshot Issues
- Fullstack Market Model requires member login — cannot automate screenshot
- StockCharts breadth charts work with direct URL: `https://stockcharts.com/h-sc/ui?s=%24SPXA20R&p=D&yr=1`
- Use `manus-upload-file` to get CDN URLs for all screenshots before building HTML

### Data Collection
- yfinance: Use `^NDX`, `^RUT`, `^DJI`, `SPY`, `QQQ`, `IWM`, `^VIX`, `GLD`, `USO`, `^TNX`, `DX-Y.NYB`, `TLT`
- Sector ETFs: `XLK`, `XLE`, `XLF`, `XLV`, `XLI`, `XLP`, `XLB`, `XLU`, `XLRE`, `XLY`, `XLC`
- Fear & Greed: scrape from feargreedmeter.com (key: `fear_greed`)
- NAAIM: scrape from naaim.org (updates weekly, typically Wednesday)
- Finviz sectors/industries: use browser navigation to `finviz.com/groups.ashx`

### HTML Template
- Base template: copy from most recent `YYYY-MM-DD.html` in repo
- Always update: date, all prices, all % changes, all RSI values, all breadth values
- Screenshot CDN URLs: upload via `manus-upload-file` and embed in HTML
- Regime level: update based on current conditions

---

*Last updated: Mar 23, 2026*
