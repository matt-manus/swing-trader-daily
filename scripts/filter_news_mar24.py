#!/usr/bin/env python3
"""
Step 1B: OpenAI filter for Finviz news
Reads the scraped headlines and filters to 5-7 market-moving stories
"""

import json
from openai import OpenAI

# Load scraped headlines
with open('/home/ubuntu/eod_data/mar24_news.json', 'r') as f:
    data = json.load(f)

unique_headlines = data['all_headlines']
print(f"Total headlines to filter: {len(unique_headlines)}")

# Market context
market_context = """
Current market context (Mar 24, 2026 — Monday US market close):
- SPY: $653.18 (-0.34%), below all MAs (20MA: $671.05, 50MA: $680.64, 200MA: $657.19)
- VIX: 26.95 (+3.06%) — elevated, above 20 danger zone
- QQQ: $583.98 (-0.68%), below all MAs
- IWM: $248.78 (+0.54%) — small cap outperforming
- DIA: $461.17 (-0.17%), below all MAs
- XLE (Energy): $60.84 (+2.03%), RSI 81.4 — strongest sector
- XLV (Health Care): $144.79 (+0.01%), RSI 27.4 — weakest sector
- GLD: $404.13 (+0.02%), RSI 27.5
- USO: $114.54 (+3.60%), RSI 62.5 — oil rebounding
- 10Y Yield: 4.39% (+1.34%)
- DXY: 99.18 (+0.24%)
- Fear & Greed: ~16 (Extreme Fear)
- NAAIM: 19.44 (near empty)
- Regime: Bearish-to-Neutral Transition (Level 6-7 of 9)
- Previous day (Mar 23): Market bounced on Iran ceasefire hopes, SPY +1.05%
"""

# Take a sample of most relevant headlines (first 80 to avoid token limit)
sample = unique_headlines[:80]
headlines_text = "\n".join([
    f"[{h['ticker']}] {h['headline']}"
    for h in sample
])

client = OpenAI()

prompt = f"""You are a professional market analyst. Given the following market context and today's news headlines (Mar 24, 2026), select the 5-7 most market-moving stories that would be most valuable for a swing trader to know.

{market_context}

Today's headlines (Mar 24, 2026):
{headlines_text}

Return a JSON object with key "stories" containing an array of 5-7 objects, each with:
- "impact": "HIGH", "MEDIUM", or "LOW"  
- "tickers": string like "NVDA · TSLA · Tech"
- "headline": the exact headline text
- "why_it_matters": one sentence explaining investment significance

Focus on: macro/geopolitical events, major company news, sector rotation signals, Fed/rates news.
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
    temperature=0.3
)

result_text = response.choices[0].message.content
print(f"\nRaw response: {result_text[:500]}")

result = json.loads(result_text)
print(f"\nKeys in response: {list(result.keys())}")

filtered_news = result.get('stories', [])
if not filtered_news:
    # Try other possible keys
    for key in result:
        if isinstance(result[key], list):
            filtered_news = result[key]
            break

print(f"\nAI selected {len(filtered_news)} stories:")
for item in filtered_news:
    print(f"  [{item.get('impact', 'N/A')}] {item.get('headline', '')[:80]}")
    print(f"    Tickers: {item.get('tickers', '')}")
    print(f"    Why: {item.get('why_it_matters', '')[:100]}")
    print()

# Save filtered news
data['filtered_news'] = filtered_news
with open('/home/ubuntu/eod_data/mar24_news.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("=== Filtered news saved ===")
