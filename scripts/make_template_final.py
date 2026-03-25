#!/usr/bin/env python3
"""
Final correct template generation script.
Uses exact string anchors to add markers and generate TEMPLATE.html.
"""
import re

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    html = f.read()

print(f"Input HTML length: {len(html)}")
assert len(html) == 33856, f"Expected 33856, got {len(html)} — make sure you restored from git first"

# ===== STEP 1: Add NEWS markers =====
# News items are between the section-title div and the next HTML comment <!-- STEP 2
# Anchor: first <div class="news-item" after <!-- STEP 1B
step1b_comment = '<!-- STEP 1B: MARKET INTELLIGENCE NEWS -->'
step2_comment = '<!-- STEP 2:'
step1b_pos = html.find(step1b_comment)
step2_pos = html.find(step2_comment)

# Find first news-item div
first_news = html.find('<div class="news-item', step1b_pos)
# Find the last closing </div> before step2_comment (this closes the section div)
# The structure is: <div class="section"> ... news items ... </div></div>
# Find the last </div> before step2_pos
last_close = html.rfind('</div>', 0, step2_pos)
second_last_close = html.rfind('</div>', 0, last_close)

print(f"first_news: {first_news}")
print(f"last_close: {last_close}, second_last_close: {second_last_close}")
print(f"At second_last_close: ...{html[second_last_close-30:second_last_close+10]}...")

# Insert markers: NEWS_START before first news-item, NEWS_END after last news-item
html = (html[:first_news] + 
        '<!-- NEWS_START -->\n' + 
        html[first_news:second_last_close] + 
        '\n<!-- NEWS_END -->' + 
        html[second_last_close:])
print("✅ NEWS markers added")

# ===== STEP 2: Add SECTOR_ROWS markers =====
header_row = '<tr><th>#</th><th>ETF</th><th>Sector</th><th>Price</th><th>1D Chg</th><th>vs 20MA</th><th>vs 50MA</th><th>vs 200MA</th><th>RSI(14)</th><th>Signal</th></tr>'
hr_idx = html.find(header_row)
assert hr_idx != -1, "Sector header row not found"
hr_end = hr_idx + len(header_row)
table_end = html.find('</table>', hr_end)
html = (html[:hr_end] + 
        '\n<!-- SECTOR_ROWS_START -->' + 
        html[hr_end:table_end] + 
        '<!-- SECTOR_ROWS_END -->\n' + 
        html[table_end:])
print("✅ SECTOR_ROWS markers added")

# ===== STEP 3: Add BULL_BEAR markers =====
# The bull/bear content starts with <h3 style="color:#e74c3c (bear header)
# and ends before <!-- REGIME DETERMINATION -->
regime_comment = '<!-- REGIME DETERMINATION -->'
bear_h3 = html.find('<h3 style="color:#e74c3c')
regime_pos = html.find(regime_comment)

print(f"bear_h3: {bear_h3}, regime_pos: {regime_pos}")

# Find the </div> just before regime_comment
close_before_regime = html.rfind('</div>', 0, regime_pos)
print(f"close_before_regime: {close_before_regime}")
print(f"At close_before_regime: ...{html[close_before_regime-30:close_before_regime+10]}...")

html = (html[:bear_h3] + 
        '<!-- BULL_BEAR_START -->\n' + 
        html[bear_h3:close_before_regime] + 
        '\n<!-- BULL_BEAR_END -->\n' + 
        html[close_before_regime:])
print("✅ BULL_BEAR markers added")

# Save the marked HTML
with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w') as f:
    f.write(html)
print(f"✅ Saved 2026-03-24.html with markers (length: {len(html)})")

# Verify markers
for marker in ['<!-- NEWS_START -->', '<!-- NEWS_END -->', 
               '<!-- SECTOR_ROWS_START -->', '<!-- SECTOR_ROWS_END -->',
               '<!-- BULL_BEAR_START -->', '<!-- BULL_BEAR_END -->']:
    present = marker in html
    # Check content between markers
    if '<!-- NEWS_START -->' == marker:
        start = html.find('<!-- NEWS_START -->')
        end = html.find('<!-- NEWS_END -->')
        content_len = end - start - len('<!-- NEWS_START -->')
        print(f"  {marker}: {'✅' if present else '❌'} (content: {content_len} chars)")
    elif '<!-- BULL_BEAR_START -->' == marker:
        start = html.find('<!-- BULL_BEAR_START -->')
        end = html.find('<!-- BULL_BEAR_END -->')
        content_len = end - start - len('<!-- BULL_BEAR_START -->')
        print(f"  {marker}: {'✅' if present else '❌'} (content: {content_len} chars)")
    else:
        print(f"  {marker}: {'✅' if present else '❌'}")

# ===== STEP 4: Generate TEMPLATE.html =====
CDN_BASE = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"

CDN_PLACEHOLDERS = {
    "YndRxnCdwPTLhosD": "{{IMG_FULLSTACK}}",
    "RuAUnYxRnaAuoCBS": "{{IMG_SPXA20R}}",
    "CQRYQqvcgMSyQWQy": "{{IMG_SPXA50R}}",
    "OUCFYSEJIVTqYKlG": "{{IMG_SPXA200R}}",
    "UMdUxgfZPbAYZjic": "{{IMG_NDXA20R}}",
    "vxFYZnXojYzBtiTr": "{{IMG_NDXA50R}}",
    "DirehvhyGxojpBip": "{{IMG_NDXA200R}}",
    "wxYUhpCHocZQnSTA": "{{IMG_NYA20R}}",
    "iZqiqQltlzjVgmRI": "{{IMG_NYA50R}}",
    "aUCTguQxmdCqwReS": "{{IMG_NYA200R}}",
    "RNDDUEwBMsDUzWZf": "{{IMG_5A_SECTORS}}",
    "GwsfqgnCFfMvkSsb": "{{IMG_5B_INDUSTRY}}",
    "QafdcWvAqPKzVPmU": "{{IMG_MARKETINOUT}}",
    "tpmAtkMCKcbryuqp": "{{IMG_T2108_SHEET}}",
}

t = html

# Replace CDN URLs
for cdn_id, placeholder in CDN_PLACEHOLDERS.items():
    old_url = CDN_BASE + cdn_id + ".png"
    if old_url in t:
        t = t.replace(old_url, placeholder)
    else:
        print(f"⚠️  CDN not found: {cdn_id[:12]}...")

# Replace dates
t = t.replace("Tue Mar 24, 2026", "{{REPORT_DATE_DISPLAY}}")
t = t.replace("2026-03-24", "{{REPORT_DATE}}")
t = t.replace("Mar 24, 2026", "{{REPORT_DATE_SHORT}}")
t = t.replace("Mar 24", "{{REPORT_DATE_MMDD}}")

# Replace numeric values
replacements = [
    ("$653.18 (-0.61%)", "${{SPY_PRICE}} ({{SPY_VS_200MA}})"),
    ("$653.18 (-4.03%)", "${{SPY_PRICE}} ({{SPY_VS_50MA}})"),
    ("$653.18 (-2.66%)", "${{SPY_PRICE}} ({{SPY_VS_20MA}})"),
    ("<strong>$653.18</strong>", "<strong>${{SPY_PRICE}}</strong>"),
    ("$653.18", "${{SPY_PRICE}}"),
    ("<strong>-0.34%</strong>", "<strong>{{SPY_CHANGE_PCT}}</strong>"),
    (">26.95<", ">{{VIX}}<"),
    ("26.95", "{{VIX}}"),
    ("Fear &amp; Greed: 17", "Fear &amp; Greed: {{FEAR_GREED}}"),
    (">17<", ">{{FEAR_GREED}}<"),
    ("60.24 — (Mar 18, 2026)", "{{NAAIM}} — ({{NAAIM_DATE}})"),
    ("60.24", "{{NAAIM}}"),
    ("22.59%", "{{T2108}}%"),
    ("22.59", "{{T2108}}"),
    ("width:22.59%", "width:{{T2108}}%"),
    ("19.80%", "{{SPXA20R}}%"),
    ("25.80%", "{{SPXA50R}}%"),
    ("49.20%", "{{SPXA200R}}%"),
    ("17.00%", "{{NDXA20R}}%"),
    ("22.00%", "{{NDXA50R}}%"),
    ("43.00%", "{{NDXA200R}}%"),
    ("26.05%", "{{NYA20R}}%"),
    ("26.80%", "{{NYA50R}}%"),
    ("47.15%", "{{NYA200R}}%"),
    (">215<", ">{{UP4PCT}}<"),
    (">281<", ">{{DOWN4PCT}}<"),
    ("215 up 4%+", "{{UP4PCT}} up 4%+"),
    ("281 down 4%+", "{{DOWN4PCT}} down 4%+"),
    (">0.50<", ">{{RATIO_5D}}<"),
    (">0.63<", ">{{RATIO_10D}}<"),
    ("$657.19", "${{SPY_200MA}}"),
    ("$680.64", "${{SPY_50MA}}"),
    ("$671.05", "${{SPY_20MA}}"),
    ("10:53 HKT (22:53 ET)", "{{REPORT_TIME}}"),
    ("Mar 25, 2026 HKT", "{{SCREENSHOT_DATE}} HKT"),
]

for old, new in replacements:
    t = t.replace(old, new)

# Replace dynamic sections with single placeholders
t = re.sub(
    r'<!-- NEWS_START -->\n.*?\n<!-- NEWS_END -->',
    '<!-- NEWS_START -->\n{{NEWS_ITEMS}}\n<!-- NEWS_END -->',
    t, flags=re.DOTALL
)
t = re.sub(
    r'<!-- SECTOR_ROWS_START -->.*?<!-- SECTOR_ROWS_END -->',
    '<!-- SECTOR_ROWS_START -->\n{{SECTOR_ROWS}}\n<!-- SECTOR_ROWS_END -->',
    t, flags=re.DOTALL
)
t = re.sub(
    r'<!-- BULL_BEAR_START -->\n.*?\n<!-- BULL_BEAR_END -->',
    '<!-- BULL_BEAR_START -->\n{{BULL_BEAR_CONTENT}}\n<!-- BULL_BEAR_END -->',
    t, flags=re.DOTALL
)

with open('/home/ubuntu/swing-trader-daily/TEMPLATE.html', 'w') as f:
    f.write(t)
print(f"\n✅ TEMPLATE.html saved (length: {len(t)})")

# Final verification
remaining_cdns = re.findall(r'https://files\.manuscdn\.com/[^\s"]+\.png', t)
print(f"Remaining CDN URLs: {len(remaining_cdns)}")
if remaining_cdns:
    for u in remaining_cdns:
        print(f"  ⚠️  {u}")

placeholders = sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', t)))
print(f"\nAll placeholders ({len(placeholders)}):")
for p in placeholders:
    print(f"  {p}")
