# Evolution: Self-Evolving Long-Term Investment Plan

## Overview
This document is the "brain" of the self-evolving system. It captures insights, lessons learned, and systemic improvements derived from past actions and market outcomes. The goal is to ensure the investment plan continuously adapts and improves over time, avoiding repeated mistakes and capitalizing on successful strategies.

## Lessons Learned & Systemic Improvements

### Format for New Entries
*Copy and paste the template below for each new entry.*

**Date**: [YYYY-MM-DD]
**Insight/Lesson Learned**: [Clear description of what was learned, e.g., "Over-allocating to tech stocks during a rate hike cycle led to excessive volatility."]
**Triggering Event/Observation**: [What happened to prompt this insight? E.g., "The tech sector dropped 15% following the unexpected 50bps rate hike on [Date]."]
**Systemic Improvement/Rule Update**: [Actionable change to the system or rules, e.g., "Implement a hard cap of 20% exposure to any single sector during periods of high interest rate volatility."]
**Status**: [Proposed / Implemented (Date) / Rejected]

---

### 2026-03-26 (Critical Rule — The Hard-Coded Template Trap)
**Insight/Lesson Learned**: If `TEMPLATE.html` contains hard-coded values, text, or HTML structure, updates to `daily_report.py` will appear to fail. The Python script only replaces `{{PLACEHOLDERS}}` it knows about. If a section is removed from the docs, or a data source changes, but the template still hard-codes the old HTML, the final report will always inherit the mistakes.
**Triggering Event/Observation**: Even after updating the script to remove Step 2 and use Barchart for exact values, the generated reports still showed Step 2 and hard-coded values like `-2.66%` for SPY 20MA. The root cause was that `TEMPLATE.html` was never cleaned up to be fully dynamic.
**Systemic Improvement/Rule Update**:
- **Rule**: `TEMPLATE.html` must remain 100% dynamic. Every single number, percentage, color class, and badge must be a `{{PLACEHOLDER}}`.
- **Rule**: If a section is removed from the report (e.g., Step 2), it must be physically deleted from `TEMPLATE.html`, not just disabled in the Python script.
- **Prevention Strategy**: Whenever updating `daily_report.py` to add new data or change logic, ALWAYS verify that `TEMPLATE.html` has the corresponding `{{PLACEHOLDER}}` tags and NO hard-coded fallback text.
**Status**: Implemented (2026-03-26)

---

### 2026-03-26 (Critical Rule — Document Updates Must Sync daily_report.py)
**Insight/Lesson Learned**: Updating documentation files (`MASTER_INSTRUCTION.md`, `WORKFLOW.md`, `evolution.md`) does NOT automatically change the behaviour of the automated report. The GitHub Actions cron job runs `daily_report.py` directly and does not read documentation. If the script is not updated, the automated report will continue using old logic indefinitely, regardless of what the documents say.
**Triggering Event/Observation**: Multiple document updates (Step 2 removal, Step 6A source change, BTC addition, Barchart exact values) had been written into the documentation but never applied to `daily_report.py`, causing new tasks to still run old behaviour.
**Systemic Improvement/Rule Update**:
- **Rule**: Every time any document is updated, `daily_report.py` MUST be updated in the same git commit.
- Script Sync Checklist (must run after every document update):
  1. New/removed data source → add/remove fetch code in script
  2. Changed URL → update URL string in script
  3. New calculation → implement in script
  4. Removed Step → delete code block in script
  5. Changed sort order → update sort logic in script
  6. Run `python3 -m py_compile daily_report.py` to confirm no syntax errors
  7. Commit and push script together with documents
**Status**: Implemented (2026-03-26)

---

### 2026-03-26 (Rule Restoration — Step 6B Google Sheets iframe for T2108)
**Insight/Lesson Learned**: The Step 6B screenshot instruction for T2108 must explicitly state that T2108 data is embedded inside a Google Sheets iframe on the Stockbee page. Without this instruction, the agent may screenshot the outer Stockbee page and miss the T2108 column entirely.
**Triggering Event/Observation**: User noticed the Google Sheets iframe fallback instruction was present in the project-level instructions but missing from the 4 core repo documents (`MASTER_INSTRUCTION.md`, `WORKFLOW.md`, `Log.md`, `evolution.md`).
**Systemic Improvement/Rule Update**:
- Step 6B screenshot technique must follow this 3-step procedure:
  1. First try scrolling into the iframe on the Stockbee page (https://stockbee.blogspot.com/p/mm.html) and screenshot from there.
  2. If T2108 is not visible in the iframe screenshot, extract the Google Sheets iframe source URL and visit it directly for a full-page screenshot.
  3. The T2108 column must **never** be missing from the final screenshot.
- This rule has been added to all 4 core documents and both Manus project shared files.
**Status**: Implemented (2026-03-26)

---

### 2026-03-26 (Rule Updates — Step 1 BTC, Step 4B Barchart, Step 6A AD Ratio)
**Insight/Lesson Learned**: Three new data requirements were added to the daily report workflow: (1) BTC price in Step 1, (2) Barchart tickers as the authoritative source for exact % above MA values in Step 4B (StockCharts remains for screenshots only), and (3) a new Step 6A Advance/Decline Ratio table sourced from StockCharts Market Summary.
**Triggering Event/Observation**: User explicitly requested these additions to improve data accuracy and breadth coverage.
**Systemic Improvement/Rule Update**:
- Step 1: Add `BTC-USD` to yfinance ticker list. Display BTC close price and daily % change in Macro Environment section.
- Step 4B: Exact % values now come from **Barchart** tickers: S&P 500 → `$S5TW`/`$S5FI`/`$S5TH`; Nasdaq 100 → `$NDTW`/`$NDFI`/`$NDTH`; NYSE → `$MMTW`/`$MMFI`/`$MMTH`. StockCharts screenshots ($SPXA20R etc.) are retained for visual display only.
- Step 6A (NEW): Before Step 6B, scrape Advancing/Declining counts for S&P 500, Nasdaq 100, DJIA, and Russell 2000 from StockCharts Market Summary page. Calculate AD Ratio = Advancing ÷ Declining (2 decimal places). Present as a table.
**Status**: Implemented (2026-03-26)

---

### 2026-03-26
**Insight/Lesson Learned**: The project had drifted from the strict `self-evolving-system` skill structure by using `RULES_EVOLUTION.md` and missing a dedicated session `Log.md`. `MARKET_HISTORY.md` was acting as a data log, but not an agent action log.
**Triggering Event/Observation**: User inquired about the location of `Log.md` and `evolution.md` as per the project skills.
**Systemic Improvement/Rule Update**: Renamed `RULES_EVOLUTION.md` to `evolution.md` and created `Log.md` to strictly adhere to the 4-core-file requirement (`MASTER_INSTRUCTION.md`, `WORKFLOW.md`, `Log.md`, `evolution.md`).
**Status**: Implemented (2026-03-26)

---

### 2026-03-23
**Insight/Lesson Learned**: Timestamp conversion between HKT and ET was backwards, causing confusion in the report header. HKT (UTC+8) is 12 hours ahead of ET (UTC-4 in summer).
**Triggering Event/Observation**: Report showed "19:45 HKT (07:45 ET)", which implies HKT is behind ET.
**Systemic Improvement/Rule Update**: Always write HKT first, then subtract 12 hours to get ET. Report generation at 07:45 HKT = 19:45 ET (prior evening). Never write "19:45 HKT / 07:45 ET".
**Status**: Implemented (2026-03-23)

---

### 2026-03-23
**Insight/Lesson Learned**: Context compression causes details (like specific URLs or exact rules) to be lost during long report generation sessions. The AI cannot rely on memory.
**Triggering Event/Observation**: Incorrect URLs or missed formatting rules in HTML generation.
**Systemic Improvement/Rule Update**: **CRITICAL:** Before starting the "Build HTML" phase, the AI MUST explicitly re-read `MASTER_INSTRUCTION.md`.
**Status**: Implemented (2026-03-23)

---

### 2026-03-20
**Insight/Lesson Learned**: Event-driven rallies (Iran/geopolitical) can be sharp but may not sustain. Breadth can recover quickly ($SPXA20R from 12.60% to 40.00% in 3 days).
**Triggering Event/Observation**: Broad market rally on Mar 23 following geopolitical relief.
**Systemic Improvement/Rule Update**: Key confirmation needed for regime change: SPY close above 200MA + VIX below 20. Do not chase initial relief rallies blindly.
**Status**: Implemented (2026-03-23)

---
*(Add new entries above this line)*

## 📋 Legacy Formatting & Content Preferences (From RULES_EVOLUTION.md)

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

## 🔑 Key Decision Rules

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
