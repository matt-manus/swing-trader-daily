#!/usr/bin/env python3
"""Step 1B: Collect Finviz news and filter with OpenAI"""
import requests
from bs4 import BeautifulSoup
import json
from openai import OpenAI
from datetime import datetime

TICKERS = ['SPY', 'QQQ', 'IWM', 'DIA', 'XLE', 'XLK', 'XLF', 'XLV', 'XLB',
           'NVDA', 'AAPL', 'MSFT', 'META', 'AMZN', 'TSLA', 'GOOGL',
           'GLD', 'TLT', 'USO', 'UUP']

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

all_headlines = []
for ticker in TICKERS:
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        news_table = soup.find(id='news-table')
        if not news_table:
            continue
        rows = news_table.find_all('tr')
        for row in rows:
            td_date = row.find('td', {'align': 'right'})
            td_news = row.find('td', {'align': 'left'})
            if not td_date or not td_news:
                continue
            date_text = td_date.text.strip()
            # Only today's news
            if 'Mar-24' in date_text or 'Today' in date_text or 'Mar 24' in date_text:
                a_tag = td_news.find('a')
                if a_tag:
                    headline = a_tag.text.strip()
                    all_headlines.append({
                        'ticker': ticker,
                        'headline': headline,
                        'date': date_text
                    })
        print(f"  {ticker}: scraped")
    except Exception as e:
        print(f"  {ticker}: ERROR {e}")

print(f"\nTotal headlines collected: {len(all_headlines)}")

# AI filter
client = OpenAI()
headlines_text = "\n".join([f"[{h['ticker']}] {h['headline']}" for h in all_headlines[:100]])

market_context = """
Mar 24, 2026 Market Context:
- SPY: $653.18 (-0.34%), below all MAs (20MA $671.05, 50MA $680.64, 200MA $657.19)
- VIX: 26.95 (+3.06%) — elevated, bearish regime
- Fear & Greed: 14 (Extreme Fear)
- Energy (XLE) RSI 80.8 — sole structural leader
- Market breadth: SPXA20R 19.80%, NDXA20R 17.00% — extreme bearish
- Stockbee: 215 up 4%+, 281 down 4%+ — negative breadth thrust
"""

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

result = json.loads(response.choices[0].message.content)
filtered_news = result.get('stories', [])

print(f"\nAI selected {len(filtered_news)} stories:")
for item in filtered_news:
    print(f"  [{item.get('impact')}] {item.get('tickers')} — {item.get('headline')[:70]}")

output = {
    'report_date': '2026-03-24',
    'total_scraped': len(all_headlines),
    'filtered_news': filtered_news
}
with open('/home/ubuntu/eod_data/step1b_news_mar24.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n=== Step 1B News Saved ===")
