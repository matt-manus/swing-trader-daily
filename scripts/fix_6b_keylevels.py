#!/usr/bin/env python3
"""
Fix 3 remaining issues in 2026-03-24.html:
1. Delete T2108 from Key Levels section
2. Fix Step 5A note to say "sorted by 1D change"
3. Replace Step 6B with correct T2108 data + screenshot (matching Mar 21 format)
"""

CDN_6B_SHEET = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/tpmAtkMCKcbryuqp.png"

T2108_VALUE = 22.59
UP_4PCT = 215
DOWN_4PCT = 281
RATIO_5D = 0.50
RATIO_10D = 0.63

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    html = f.read()

# ---- Fix 1: Delete T2108 from Key Levels ----
# Find the Key Levels section and remove the T2108 row
import re

# Find T2108 row in key levels table (it will be a <tr> containing T2108)
# Pattern: any <tr> that contains "T2108" in the key levels section
key_levels_idx = html.find('Key Level')
if key_levels_idx == -1:
    key_levels_idx = html.find('key-level')
if key_levels_idx == -1:
    key_levels_idx = html.find('KEY LEVEL')

print(f"Key Levels section at: {key_levels_idx}")

# Find and remove T2108 rows from key levels
# Look for table rows containing T2108
t2108_row_pattern = re.compile(r'\s*<tr[^>]*>(?:(?!</tr>).)*T2108(?:(?!</tr>).)*</tr>', re.DOTALL)
matches = list(t2108_row_pattern.finditer(html))
print(f"Found {len(matches)} T2108 rows to remove")
for m in matches:
    print(f"  Row: {repr(m.group()[:100])}")

# Remove all T2108 rows
html_new = t2108_row_pattern.sub('', html)
if html_new != html:
    print("✅ Removed T2108 rows from Key Levels")
    html = html_new
else:
    # Try simpler approach - find the specific T2108 line
    print("Trying simpler T2108 removal...")
    # Look for lines with T2108 in them
    lines = html.split('\n')
    new_lines = []
    skip_next = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'T2108' in line and '<tr' in line:
            # Skip this row - find the closing </tr>
            if '</tr>' in line:
                print(f"  Removed single-line T2108 row")
                i += 1
                continue
            else:
                # Multi-line row, skip until </tr>
                print(f"  Removing multi-line T2108 row starting at line {i}")
                while i < len(lines) and '</tr>' not in lines[i]:
                    i += 1
                i += 1  # skip the </tr> line
                continue
        new_lines.append(line)
        i += 1
    html = '\n'.join(new_lines)
    print("✅ Removed T2108 from Key Levels (line-by-line)")

# ---- Fix 2: Update Step 5A header to mention sorted by 1D change ----
old_5a_header = '5A. Sector Performance (Finviz — Mar 24 EOD)'
new_5a_header = '5A. Sector Performance (Finviz — Mar 24 EOD, sorted by 1D Change)'
if old_5a_header in html:
    html = html.replace(old_5a_header, new_5a_header)
    print("✅ Updated Step 5A header")
else:
    print("⚠️  Step 5A header not found (may already be correct)")

# ---- Fix 3: Replace Step 6B with correct T2108 data + screenshot ----
h3_6b_start = html.rfind('<h3', 0, html.find('6B.'))
end_6b = html.find('<h3', h3_6b_start + 10)
if end_6b == -1:
    end_6b = html.find('<!-- Step 7', h3_6b_start)
if end_6b == -1:
    end_6b = html.find('</section>', h3_6b_start)

print(f"Step 6B: h3 at {h3_6b_start}, end at {end_6b}")

# Determine T2108 signal
if T2108_VALUE < 20:
    t2108_signal = '<span class="badge badge-bear">EXTREME OVERSOLD (&lt;20%)</span>'
    t2108_zone = "極度超賣區間 (<20%)"
elif T2108_VALUE < 40:
    t2108_signal = '<span class="badge badge-bear">OVERSOLD ZONE (&lt;40%)</span>'
    t2108_zone = "超賣區間 (<40%)"
else:
    t2108_signal = '<span class="badge badge-warn">NEUTRAL</span>'
    t2108_zone = "中性區間"

ratio_5d_signal = "BEARISH (&lt;1.0)" if RATIO_5D < 1.0 else "BULLISH (&gt;1.0)"
ratio_10d_signal = "BEARISH (&lt;1.0)" if RATIO_10D < 1.0 else "BULLISH (&gt;1.0)"

new_6b = f'''<h3 class="sub">6B. Stockbee Market Monitor (T2108 &amp; 4% Movers) <span class="live-badge">✅ LIVE</span></h3>
    <table>
      <tr><th>Metric</th><th>Value (Mar 24)</th><th>Signal</th></tr>
      <tr><td>Stocks up 4%+ today</td><td class="red">{UP_4PCT}</td><td><span class="badge badge-bear">SELLING PRESSURE</span></td></tr>
      <tr><td>Stocks down 4%+ today</td><td class="red">{DOWN_4PCT}</td><td><span class="badge badge-bear">SELLING PRESSURE</span></td></tr>
      <tr><td>5-day ratio</td><td class="yellow">{RATIO_5D}</td><td><span class="badge badge-warn">{ratio_5d_signal}</span></td></tr>
      <tr><td>10-day ratio</td><td class="yellow">{RATIO_10D}</td><td><span class="badge badge-warn">{ratio_10d_signal}</span></td></tr>
      <tr><td><strong>T2108 (% above 40MA)</strong></td><td class="red"><strong>{T2108_VALUE}%</strong></td><td>{t2108_signal}</td></tr>
    </table>
    <div style="margin-top:12px">
      <div style="color:#8b949e; font-size:12px; margin-bottom:4px">T2108 Gauge: {T2108_VALUE}% (Oversold &lt;40% | Extreme Oversold &lt;20%) — ✅ Live Mar 24 data from Stockbee</div>
      <div class="t2108-bar">
        <div class="t2108-fill" style="width:{T2108_VALUE}%"></div>
        <div class="t2108-label">{T2108_VALUE}%</div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:10px; color:#555; margin-top:2px">
        <span>0%</span><span>20% (Extreme OS)</span><span>40% (OS)</span><span>60% (Neutral)</span><span>80% (OB)</span><span>100%</span>
      </div>
    </div>
    <img src="{CDN_6B_SHEET}" class="screenshot-img" alt="Stockbee Market Monitor — T2108 and 4% Movers (Mar 24)" style="width:100%;border-radius:6px;margin:12px 0;">
    <div class="source-label">Source: <a href="https://stockbee.blogspot.com/p/mm.html" style="color:#58a6ff">stockbee.blogspot.com/p/mm.html</a> | Screenshot taken Mar 25, 2026 HKT</div>
    <div class="note">📌 廣度總結: T2108 {T2108_VALUE}% 屬{t2108_zone}。今日下跌 4%+ 的股票有 {DOWN_4PCT} 隻，多於上漲 4%+ 的 {UP_4PCT} 隻，賣壓持續。5日及10日比率分別為 {RATIO_5D} 及 {RATIO_10D}，廣度結構仍偏弱。</div>
  </div>

'''

html = html[:h3_6b_start] + new_6b + html[end_6b:]
print("✅ Replaced Step 6B with correct T2108 data + screenshot")

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w') as f:
    f.write(html)
print("\n✅ Saved 2026-03-24.html")

# Verify
with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    check = f.read()
print("\nVerification:")
print(f"  T2108 22.59% in 6B: {'✅' if '22.59' in check else '❌'}")
print(f"  CDN sheet URL in 6B: {'✅' if CDN_6B_SHEET in check else '❌'}")
print(f"  T2108 bar present: {'✅' if 't2108-bar' in check else '❌'}")
print(f"  5A sorted by 1D: {'✅' if 'sorted by 1D Change' in check else '❌'}")
# Check T2108 in Key Levels
kl_idx = check.find('Key Level')
if kl_idx == -1:
    kl_idx = check.find('key-level')
if kl_idx != -1:
    kl_section = check[kl_idx:kl_idx+2000]
    t2108_in_kl = 'T2108' in kl_section
    print(f"  T2108 removed from Key Levels: {'❌ STILL PRESENT' if t2108_in_kl else '✅'}")
else:
    print("  Key Levels section: not found (check manually)")
