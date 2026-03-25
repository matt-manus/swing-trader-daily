"""Add parent sectors to the top 10 industry leaders using Finviz sector mapping."""

# Finviz industry → sector mapping (standard)
INDUSTRY_SECTOR = {
    "Coking Coal": "Energy",
    "Chemicals": "Basic Materials",
    "Thermal Coal": "Energy",
    "Agricultural Inputs": "Basic Materials",
    "Electrical Equipment & Parts": "Industrials",
    "Silver": "Basic Materials",
    "Solar": "Technology",
    "Oil & Gas Refining & Marketing": "Energy",
    "Farm Products": "Consumer Defensive",
    "Metal Fabrication": "Industrials",
    "Electronic Components": "Technology",
    "Marine Shipping": "Industrials",
    "Communication Equipment": "Technology",
    "Semiconductor Equipment & Materials": "Technology",
    "Aluminum": "Basic Materials",
}

import json

with open('/home/ubuntu/eod_data/industry_leaders.json') as f:
    leaders = json.load(f)

top10 = leaders[:10]
for item in top10:
    item['sector'] = INDUSTRY_SECTOR.get(item['name'], 'Unknown')

print("Top 10 Industry Leaders with Sectors:")
print("-" * 60)
for i, item in enumerate(top10, 1):
    print(f"{i:2}. {item['name']:<35} {item['sector']:<25} {item['change_1d']}")

with open('/home/ubuntu/eod_data/industry_leaders_with_sectors.json', 'w') as f:
    json.dump(top10, f, indent=2)

print("\nSaved to industry_leaders_with_sectors.json")
