#!/usr/bin/env python3
"""
Step 1B: Finviz News Scraper + OpenAI Filter
Scrapes today's headlines from 20 tickers, filters to 5-7 market-moving stories
Report date: 2026-03-24 (Monday US market close)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from openai import OpenAI

REPORT_DATE = "Mar 24"  # Only include headlines from this date
REPORT_DATE_ALT = "Mar 24, 2026"

TICKERS = [
    'SPY', 'QQQ', 'IWM', 'DIA',
    'XLE', 'XLK', 'XLF', 'XLV', 'XLB',
    'NVDA', 'AAPL', 'MSFT', 'META', 'AMZN', 'TSLA', 'GOOGL',
    'GLD', 'TLT', 'USO', 'UUP'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def scrape_finviz_news(ticker):
    """Scrape today's news headlines from Finviz for a given ticker"""
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  {ticker}: HTTP {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        news_table = soup.find('table', id='news-table')
        if not news_table:
            print(f"  {ticker}: No news table found")
            return []
        
        headlines = []
        current_date = None
        
        for row in news_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            date_cell = cells[0].text.strip()
            headline_cell = cells[1]
            headline_text = headline_cell.get_text(strip=True)
            
            # Parse date/time
            if 'Mar-24-26' in date_cell or 'Mar-24' in date_cell or 'Today' in date_cell:
                current_date = REPORT_DATE
            elif any(d in date_cell for d in ['Mar-23', 'Mar-22', 'Mar-21', 'Mar-20']):
                current_date = "older"
            elif date_cell and ':' in date_cell and current_date:
                # Same date as previous row
                pass
            
            # Only include today's headlines
            if current_date == REPORT_DATE:
                # Get source
                source = ""
                source_tag = headline_cell.find('span', class_='news-link-right')
                if source_tag:
                    source = source_tag.text.strip()
                
                link_tag = headline_cell.find('a')
                link = link_tag['href'] if link_tag else ""
                
                headlines.append({
                    'ticker': ticker,
                    'headline': headline_text,
                    'source': source,
                    'link': link,
                    'date': REPORT_DATE
                })
        
        print(f"  {ticker}: {len(headlines)} today's headlines")
        return headlines
        
    except Exception as e:
        print(f"  {ticker}: Error - {e}")
        return []

# ─── Scrape all tickers ────────────────────────────────────────────────────
print("=== Scraping Finviz news for 20 tickers ===")
all_headlines = []
for ticker in TICKERS:
    headlines = scrape_finviz_news(ticker)
    all_headlines.extend(headlines)
    time.sleep(1.5)  # Be polite to Finviz

print(f"\nTotal today's headlines collected: {len(all_headlines)}")

# Remove duplicates (same headline from different tickers)
seen = set()
unique_headlines = []
for h in all_headlines:
    key = h['headline'][:80]
    if key not in seen:
        seen.add(key)
        unique_headlines.append(h)

print(f"Unique headlines: {len(unique_headlines)}")

# ─── OpenAI Filter ────────────────────────────────────────────────────────
print("\n=== Running OpenAI filter for top 5-7 market-moving stories ===")

# Market context for AI
market_context = """
Current market context (Mar 24, 2026):
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
- Fear & Greed: ~16 (Extreme Fear, from Mar 23)
- NAAIM: 19.44 (near empty, from Mar 18)
- Regime: Bearish-to-Neutral Transition (Level 6-7 of 9)
"""

headlines_text = "\n".join([
    f"[{h['ticker']}] {h['headline']}"
    for h in unique_headlines
])

if not unique_headlines:
    print("No today's headlines found. Using placeholder.")
    filtered_news = []
else:
    client = OpenAI()
    
    prompt = f"""You are a professional market analyst. Given the following market context and today's news headlines, select the 5-7 most market-moving stories that would be most valuable for a swing trader to know.

{market_context}

Today's headlines (Mar 24, 2026):
{headlines_text}

For each selected story, provide:
1. Impact level: HIGH, MEDIUM, or LOW
2. Affected tickers/sectors
3. One-sentence explanation of why it matters for investment decisions

Return as JSON array with fields: impact, tickers, headline, why_it_matters
Only include headlines that are actually from today (Mar 24). If a headline appears to be from a different date, exclude it.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].message.content)
    filtered_news = result.get('stories', result.get('headlines', result.get('news', [])))
    
    print(f"\nAI selected {len(filtered_news)} stories:")
    for item in filtered_news:
        print(f"  [{item.get('impact', 'N/A')}] {item.get('headline', '')[:80]}")

# ─── Save results ──────────────────────────────────────────────────────────
news_output = {
    'report_date': '2026-03-24',
    'total_scraped': len(unique_headlines),
    'all_headlines': unique_headlines,
    'filtered_news': filtered_news
}

with open('/home/ubuntu/eod_data/mar24_news.json', 'w') as f:
    json.dump(news_output, f, indent=2, ensure_ascii=False)

print("\n=== News data saved to /home/ubuntu/eod_data/mar24_news.json ===")
