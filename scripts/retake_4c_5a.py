#!/usr/bin/env python3
"""
Retake Step 4C (StockCharts breadth) at wide viewport and Step 5A (Finviz sectors sorted by 1D change).
"""
import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os

OUTPUT_DIR = "/home/ubuntu/eod_data"

STOCKCHARTS = [
    ("spxa20r", "https://stockcharts.com/h-sc/ui?s=%24SPXA20R&p=D&yr=1&mn=0&dy=0"),
    ("spxa50r", "https://stockcharts.com/h-sc/ui?s=%24SPXA50R&p=D&yr=1&mn=0&dy=0"),
    ("spxa200r", "https://stockcharts.com/h-sc/ui?s=%24SPXA200R&p=D&yr=1&mn=0&dy=0"),
    ("ndxa20r", "https://stockcharts.com/h-sc/ui?s=%24NDXA20R&p=D&yr=1&mn=0&dy=0"),
    ("ndxa50r", "https://stockcharts.com/h-sc/ui?s=%24NDXA50R&p=D&yr=1&mn=0&dy=0"),
    ("ndxa200r", "https://stockcharts.com/h-sc/ui?s=%24NDXA200R&p=D&yr=1&mn=0&dy=0"),
    ("nya20r", "https://stockcharts.com/h-sc/ui?s=%24NYA20R&p=D&yr=1&mn=0&dy=0"),
    ("nya50r", "https://stockcharts.com/h-sc/ui?s=%24NYA50R&p=D&yr=1&mn=0&dy=0"),
    ("nya200r", "https://stockcharts.com/h-sc/ui?s=%24NYA200R&p=D&yr=1&mn=0&dy=0"),
]

# Finviz sector sorted by 1D change descending
FINVIZ_SECTOR_URL = "https://finviz.com/groups.ashx?g=sector&o=-change&v=140"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # ---- Step 4C: StockCharts at 1600px wide ----
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        
        sc_paths = []
        for name, url in STOCKCHARTS:
            print(f"  Capturing {name}...")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            
            path = f"{OUTPUT_DIR}/2026-03-24_{name}_wide.png"
            await page.screenshot(path=path)
            
            # Crop to just the chart area (remove header/footer, keep chart)
            img = Image.open(path)
            w, h = img.size
            # StockCharts chart is roughly in the middle — crop top 80px (header) and bottom 100px
            cropped = img.crop((0, 80, w, h - 80))
            cropped.save(path)
            sc_paths.append((name, path))
            print(f"    Saved: {path} ({cropped.size})")
        
        # ---- Step 5A: Finviz sectors sorted by 1D change ----
        print("\n  Capturing Finviz sectors sorted by 1D change...")
        page5a = await browser.new_page(viewport={"width": 1400, "height": 900})
        page5a.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        try:
            await page5a.goto(FINVIZ_SECTOR_URL, wait_until="networkidle", timeout=30000)
        except:
            await page5a.goto(FINVIZ_SECTOR_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        path_5a = f"{OUTPUT_DIR}/2026-03-24_5A_sectors_sorted.png"
        await page5a.screenshot(path=path_5a)
        
        # Crop to table area
        img5a = Image.open(path_5a)
        w, h = img5a.size
        # Finviz table starts around y=100, crop to show just the table
        cropped5a = img5a.crop((0, 90, w, min(600, h)))
        cropped5a.save(path_5a)
        print(f"  Saved 5A: {path_5a} ({cropped5a.size})")
        
        await browser.close()
        
        return sc_paths, path_5a

sc_paths, path_5a = asyncio.run(main())
print("\nAll screenshots captured. Now uploading to CDN...")

import subprocess
all_files = [p for _, p in sc_paths] + [path_5a]
result = subprocess.run(
    ["manus-upload-file"] + all_files,
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)

# Parse CDN URLs from output
lines = result.stdout.strip().split('\n')
cdn_urls = [l.split('CDN URL: ')[1].strip() for l in lines if 'CDN URL:' in l]
print(f"\nGot {len(cdn_urls)} CDN URLs")

# Map names to CDN URLs
names = [name for name, _ in sc_paths] + ["5a_sectors"]
name_to_cdn = dict(zip(names, cdn_urls))

import json
with open(f"{OUTPUT_DIR}/2026-03-24_retake_cdn.json", "w") as f:
    json.dump(name_to_cdn, f, indent=2)
print("CDN mapping saved.")
for k, v in name_to_cdn.items():
    print(f"  {k}: {v}")
