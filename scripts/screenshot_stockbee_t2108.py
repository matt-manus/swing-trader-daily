#!/usr/bin/env python3
"""
Screenshot the Stockbee Google Sheets directly to show T2108 column.
The Google Sheets URL is publicly accessible (no login needed).
"""
import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os

SHEETS_URL = "https://docs.google.com/spreadsheet/pub?key=0Am_cU8NLIU20dEhiQnVHN3Nnc3B1S3J6eGhKZFo0N3c&output=html&widget=true"
OUTPUT_PATH = "/home/ubuntu/eod_data/2026-03-24_6B_t2108_sheet.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a very wide viewport to show all columns
        page = await browser.new_page(viewport={"width": 1800, "height": 900})
        
        print("Loading Google Sheets...")
        try:
            await page.goto(SHEETS_URL, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Timeout/error loading, trying domcontentloaded: {e}")
            await page.goto(SHEETS_URL, wait_until="domcontentloaded", timeout=60000)
        
        await asyncio.sleep(3)
        
        # Take full page screenshot
        await page.screenshot(path=OUTPUT_PATH, full_page=False)
        print(f"Screenshot saved: {OUTPUT_PATH}")
        
        # Crop to just the table area (top portion with data)
        img = Image.open(OUTPUT_PATH)
        w, h = img.size
        print(f"Screenshot size: {w}x{h}")
        
        # Crop to show the top ~600px (the data rows)
        cropped = img.crop((0, 0, w, min(700, h)))
        cropped.save(OUTPUT_PATH)
        print(f"Cropped to: {cropped.size}")
        
        await browser.close()

asyncio.run(main())
