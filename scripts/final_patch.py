"""Final patch for 2026-03-24.html:
1. Replace Fullstack 'member login' note with actual screenshot
2. Verify all key data replacements
"""
import re

FULLSTACK_CDN = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/AKeZtENLuEgCqWgq.png"

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace the "member login" note with the actual screenshot
old_fullstack = '''<div class="note">⚠️ Fullstack Market Model page requires member login. Screenshot not available for this session. Please check <a href="https://fullstacktrading.com/market-model/" style="color:#58a6ff" target="_blank">fullstacktrading.com/market-model/</a> directly for the current model reading. Based on prior data (Mar 20), model was BULLISH (high exposure recommended).</div>'''

new_fullstack = f'''<div class="chart-container">
  <img src="{FULLSTACK_CDN}" alt="Fullstack Market Model Mar 24" style="max-width:100%;border-radius:8px;">
</div>'''

if old_fullstack in html:
    html = html.replace(old_fullstack, new_fullstack)
    print("✓ Fullstack section updated with screenshot")
else:
    print("✗ Could not find Fullstack note to replace")
    # Try partial match
    idx = html.find('Fullstack Market Model page requires member login')
    if idx >= 0:
        print(f"  Found at {idx}, context: {html[max(0,idx-50):idx+200]}")

# 2. Update the date badge from "Mar 23" to "Mar 24"
html = html.replace('✅ LIVE — Mar 23', '✅ LIVE — Mar 24')
html = html.replace('Mar 23, 2026', 'Mar 24, 2026')

# 3. Verify key data values
checks = [
    ('653.18', 'SPY price'),
    ('583.98', 'QQQ price'),
    ('248.78', 'IWM price'),
    ('461.17', 'DIA price'),
    ('26.95', 'VIX'),
    ('17</div>', 'Fear & Greed'),
    ('215 / 281', 'T2108'),
    ('Coking Coal', 'Industry leader 1'),
    ('Chemicals', 'Industry leader 2'),
    ('UchRzbLnXZOVLOSM', 'SPXA20R CDN'),
    ('LqnzwjnmCuLSIiIJ', 'NYA20R CDN'),
    ('atToNJzyXaRJbfPN', 'Stockbee CDN'),
    ('AKeZtENLuEgCqWgq', 'Fullstack CDN'),
]

print("\n=== Data Verification ===")
all_ok = True
for value, label in checks:
    found = value in html
    status = "✓" if found else "✗ MISSING"
    print(f"  {status} {label}: {value}")
    if not found:
        all_ok = False

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w', encoding='utf-8') as f:
    f.write(html)

if all_ok:
    print("\n✅ All checks passed. HTML is ready.")
else:
    print("\n⚠️ Some checks failed. Review above.")
