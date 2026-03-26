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
