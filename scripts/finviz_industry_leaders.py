#!/usr/bin/env python3
"""Scrape Finviz industry groups sorted by 1-day performance to get top 10 leaders"""
import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Performance view sorted by 1-day change descending
url = "https://finviz.com/groups.ashx?g=industry&sg=&o=-perf1d&t=&f=&v=140"
resp = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

# Find the groups table
table = soup.find('table', class_='t-groups-table')
if not table:
    # Try alternate approach
    tables = soup.find_all('table')
    for t in tables:
        rows = t.find_all('tr')
        if len(rows) > 5:
            headers_row = rows[0].find_all('th')
            if headers_row and any('Change' in h.text or 'Perf' in h.text for h in headers_row):
                table = t
                break

if not table:
    print("Table not found, trying direct parsing...")
    # Parse all tr elements with td
    rows = soup.find_all('tr')
    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 10:
            no = cells[0].text.strip()
            name = cells[1].text.strip()
            change = cells[10].text.strip() if len(cells) > 10 else cells[-1].text.strip()
            if no.isdigit() and name and '%' in change:
                data.append({'rank': int(no), 'name': name, 'change_1d': change})
    data.sort(key=lambda x: float(x['change_1d'].replace('%', '')), reverse=True)
    print("Top 15 by 1D change:")
    for d in data[:15]:
        print(f"  {d['rank']}. {d['name']}: {d['change_1d']}")
    with open('/home/ubuntu/eod_data/industry_leaders.json', 'w') as f:
        json.dump(data[:15], f, indent=2)
else:
    rows = table.find_all('tr')[1:]  # skip header
    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 10:
            no = cells[0].text.strip()
            name = cells[1].text.strip()
            change = cells[10].text.strip() if len(cells) > 10 else cells[-1].text.strip()
            if no.isdigit() and name and '%' in change:
                data.append({'rank': int(no), 'name': name, 'change_1d': change})
    data.sort(key=lambda x: float(x['change_1d'].replace('%', '')), reverse=True)
    print("Top 15 by 1D change:")
    for d in data[:15]:
        print(f"  {d['rank']}. {d['name']}: {d['change_1d']}")
    with open('/home/ubuntu/eod_data/industry_leaders.json', 'w') as f:
        json.dump(data[:15], f, indent=2)
