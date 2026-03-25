#!/usr/bin/env python3
"""
take_screenshots.py
Takes full-page screenshots of:
- Step 5A: Finviz sector performance
- Step 5B: Finviz industry leaders (top performers)
- Step 6B: Stockbee T2108
All at 1600px wide viewport for readability.
"""

import sys, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_DIR = Path('/home/ubuntu/eod_data')
DATE_STR = sys.argv[1] if len(sys.argv) > 1 else '2026-03-24'

def screenshot(url, out_path, wait_ms=5000, full_page=True, clip=None, scroll_to=None):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=1.5  # higher resolution
        )
        page = ctx.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(wait_ms)
        if scroll_to:
            page.evaluate(f'window.scrollTo(0, {scroll_to})')
            page.wait_for_timeout(1000)
        if clip:
            page.screenshot(path=str(out_path), clip=clip)
        else:
            page.screenshot(path=str(out_path), full_page=full_page)
        browser.close()
    print(f'  Saved: {out_path} ({out_path.stat().st_size//1024}KB)')

print('[Step 5A] Finviz Sector Performance...')
screenshot(
    'https://finviz.com/groups.ashx?g=sector&o=-perf1d&v=140',
    DATA_DIR / f'{DATE_STR}_5A_sectors.png',
    wait_ms=4000,
    full_page=False
)

print('[Step 5B] Finviz Industry Leaders (top 1-day performers)...')
screenshot(
    'https://finviz.com/groups.ashx?g=industry&o=-perf1d&v=140',
    DATA_DIR / f'{DATE_STR}_5B_industries.png',
    wait_ms=4000,
    full_page=False
)

print('[Step 6B] Stockbee Market Monitor (T2108)...')
screenshot(
    'https://stockbee.blogspot.com/p/mm.html',
    DATA_DIR / f'{DATE_STR}_6B_stockbee.png',
    wait_ms=6000,
    full_page=True
)

print('\nAll screenshots done. Uploading to CDN...')
result = subprocess.run(
    ['manus-upload-file',
     str(DATA_DIR / f'{DATE_STR}_5A_sectors.png'),
     str(DATA_DIR / f'{DATE_STR}_5B_industries.png'),
     str(DATA_DIR / f'{DATE_STR}_6B_stockbee.png')],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print('UPLOAD ERROR:', result.stderr)
